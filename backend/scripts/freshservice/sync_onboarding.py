#!/usr/bin/env python3
"""
Freshservice Onboarding Sync Script
Retrieves onboarding tickets from Freshservice and creates user records in the helpdesk CRM
"""
import sys
import os
import json
import requests
import secrets
from datetime import datetime, timedelta, timezone
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from base_script import BaseUserScript
from typing import Dict, Any, List

class FreshserviceOnboardingSync(BaseUserScript):
    """Syncs onboarding tickets from Freshservice to helpdesk CRM"""
    
    def __init__(self):
        super().__init__()
        self.freshdesk_api_key = None
        self.jumpcloud_api_key = None
        self.region = "us-west-2"
        self.freshdesk_domain = "americor.freshservice.com"
    
    def get_secrets(self) -> bool:
        """Get Freshdesk & JumpCloud API keys from environment variables"""
        try:
            # Get API keys from environment variables
            self.freshdesk_api_key = os.getenv("FRESHDESK_API_KEY")
            self.jumpcloud_api_key = os.getenv("JUMPCLOUD_API_KEY")
            freshdesk_domain = os.getenv("FRESHDESK_DOMAIN")
            
            if freshdesk_domain:
                self.freshdesk_domain = freshdesk_domain
            
            if not self.freshdesk_api_key:
                self.log_error("FRESHDESK_API_KEY not found in environment variables")
                return False
            
            if not self.jumpcloud_api_key:
                self.log_error("JUMPCLOUD_API_KEY not found in environment variables")
                return False
            
            self.log_info("Successfully retrieved API keys from environment variables")
            return True
            
        except Exception as e:
            self.log_error(f"Error getting secrets: {e}")
            return False
    
    def get_recent_onboarding_tickets(self, hours_back: int = 24) -> List[int]:
        """Get Freshdesk tickets updated in the specified time window"""
        try:
            time_ago = (datetime.now(timezone.utc) - timedelta(hours=hours_back)).isoformat()
            url = f"https://{self.freshdesk_domain}/api/v2/tickets"
            params = {"updated_since": time_ago, "per_page": 100}
            
            self.log_info(f"Fetching tickets updated since: {time_ago}")
            
            resp = requests.get(url, auth=(self.freshdesk_api_key, "X"), params=params, timeout=30)
            
            if resp.status_code != 200:
                self.log_error(f"Error fetching tickets: {resp.status_code} {resp.text}")
                return []
            
            tickets = resp.json()
            if isinstance(tickets, list):
                # API returns array directly
                onboarding_tickets = [t["id"] for t in tickets if t["subject"].startswith("NEW ONBOARDING")]
            else:
                # API returns object with tickets key
                tickets_list = tickets.get("tickets", [])
                onboarding_tickets = [t["id"] for t in tickets_list if t["subject"].startswith("NEW ONBOARDING")]
            
            self.log_info(f"Found {len(onboarding_tickets)} onboarding tickets: {onboarding_tickets}")
            return onboarding_tickets
            
        except Exception as e:
            self.log_error(f"Error fetching recent tickets: {e}")
            return []
    
    def get_ticket_requested_items(self, ticket_id: int) -> List[Dict[str, Any]]:
        """Get ticket details (requested_items & custom_fields)"""
        try:
            url = f"https://{self.freshdesk_domain}/api/v2/tickets/{ticket_id}/requested_items"
            resp = requests.get(url, auth=(self.freshdesk_api_key, "X"), timeout=30)
            
            if resp.status_code != 200:
                self.log_error(f"Failed to fetch requested_items for ticket {ticket_id}: {resp.status_code}")
                return []
            
            response_data = resp.json()
            return response_data.get("requested_items", [])
            
        except Exception as e:
            self.log_error(f"Error fetching ticket {ticket_id} requested items: {e}")
            return []
    
    def transform_freshservice_data(self, ticket_id: int, custom_fields: Dict[str, Any]) -> Dict[str, Any]:
        """Transform Freshservice custom fields to helpdesk CRM user format"""
        
        # Extract company email from display_name and company
        first_name = custom_fields.get("first_name", "")
        last_name = custom_fields.get("last_name", "")
        company = custom_fields.get("company", "").lower()
        
        # Generate company email based on company
        username = f"{first_name.lower()}.{last_name.lower()}" if first_name and last_name else ""
        
        company_domain_map = {
            "credit9": "credit9.com",
            "americor": "americor.com"
        }
        
        domain = company_domain_map.get(company, "americor.com")
        company_email = f"{username}@{domain}" if username else ""
        
        # Parse and format start_date for MySQL
        start_date = custom_fields.get("start_date", "")
        formatted_start_date = None
        if start_date:
            try:
                # Parse ISO format date (2025-08-29T15:00:00Z)
                from dateutil import parser
                parsed_date = parser.parse(start_date)
                # Format for MySQL datetime (YYYY-MM-DD HH:MM:SS)
                formatted_start_date = parsed_date.strftime("%Y-%m-%d %H:%M:%S")
            except Exception as e:
                self.log_error(f"Error parsing start_date '{start_date}': {e}")
                formatted_start_date = None
        
        # Transform the data to match your helpdesk CRM format
        password = secrets.token_urlsafe(16)  # Generate a random password
        
        user_data = {
            # Basic info
            "freshservice_ticket_id": ticket_id,
            "username": username,
            "first_name": first_name,
            "last_name": last_name,
            "display_name": custom_fields.get("display_name", f"{first_name} {last_name}"),
            "company_email": company_email,
            "personal_email": custom_fields.get("email", ""),
            
            # Company info
            "company": custom_fields.get("company", ""),
            "title": custom_fields.get("title", ""),
            "department": custom_fields.get("department", ""),
            "manager": custom_fields.get("manager", ""),
            "start_date": formatted_start_date,
            
            # Contact info
            "phone_number": str(custom_fields.get("phone_number", "")),
            
            # Address info
            "address_type": custom_fields.get("address_type", ""),
            "street_name": custom_fields.get("street_name", ""),
            "city": custom_fields.get("city", ""),
            "state": custom_fields.get("state", ""),
            "zip_code": str(custom_fields.get("zip_code", "")),
            
            # Work location
            "location_first_day": custom_fields.get("location_first_day", ""),
            
            # Additional details
            "extras_details": custom_fields.get("extras_details", ""),
            
            # System info (for future use)
            "hostname": custom_fields.get("hostname", ""),
            
            # Status tracking
            "onboarding_status": "pending",
            "sync_source": "freshservice",
            "sync_timestamp": datetime.now().isoformat(),
            "password": password,
        }
        
        return user_data
    
    def save_user_to_database(self, user_data: Dict[str, Any]) -> bool:
        """Save user data to the helpdesk CRM database"""
        try:
            # Import database models here to avoid circular imports
            from sqlalchemy import create_engine, text
            from sqlalchemy.orm import sessionmaker
            import os
            
            # Get database connection from environment
            db_host = os.getenv('DB_HOST', 'localhost')
            db_port = os.getenv('DB_PORT', '3306')
            db_user = os.getenv('DB_USER', 'helpdesk')
            db_password = os.getenv('DB_PASSWORD', 'helpdesk123')
            db_name = os.getenv('DB_NAME', 'helpdesk_crm')
            
            connection_string = f"mysql+pymysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
            engine = create_engine(connection_string)
            Session = sessionmaker(bind=engine)
            session = Session()
            
            # Check if user already exists based on company_email or freshservice_ticket_id
            existing_user_query = text("""
                SELECT id FROM onboarding 
                WHERE company_email = :email OR notes LIKE :ticket_search OR ticket_number = :ticket_number
                LIMIT 1
            """)
            
            existing_user = session.execute(existing_user_query, {
                "email": user_data["company_email"],
                "ticket_search": f"%freshservice_ticket_id:{user_data['freshservice_ticket_id']}%",
                "ticket_number": str(user_data['freshservice_ticket_id'])
            }).fetchone()
            
            if existing_user:
                self.log_info(f"User already exists for ticket {user_data['freshservice_ticket_id']}: {user_data['company_email']}")
                session.close()
                return "skipped"
            
            # Insert new user
            insert_query = text("""
                INSERT INTO onboarding (
                    username, first_name, last_name, display_name, company_email, personal_email, title, 
                    department, manager, start_date, phone_number, company, status, notes, 
                    ticket_number, location_first_day, address_type, street_name, city, state, zip_code,
                    password, created_at, updated_at
                ) VALUES (
                    :username, :first_name, :last_name, :display_name, :company_email, :personal_email, :title,
                    :department, :manager, :start_date, :phone_number, :company, :status, :notes,
                    :ticket_number, :location_first_day, :address_type, :street_name, :city, :state, :zip_code,
                    :password, NOW(), NOW()
                )
            """)
            
            password = user_data.get("password", None)
            
            # Remove detailed JSON object from notes
            session.execute(insert_query, {
                "username": user_data["username"],
                "first_name": user_data["first_name"],
                "last_name": user_data["last_name"],
                "display_name": user_data["display_name"],
                "company_email": user_data["company_email"],
                "personal_email": user_data["personal_email"],
                "title": user_data["title"],
                "department": user_data["department"],
                "manager": user_data["manager"],
                "start_date": user_data["start_date"] or None,
                "phone_number": user_data["phone_number"],
                "company": user_data["company"],
                "status": "PENDING",  # Use enum value for status
                "notes": "",  # Empty notes field
                "ticket_number": str(user_data["freshservice_ticket_id"]),
                "location_first_day": user_data["location_first_day"],
                "address_type": user_data["address_type"] or "RESIDENTIAL",  # Default enum value
                "street_name": user_data["street_name"],
                "city": user_data["city"],
                "state": user_data["state"],
                "zip_code": user_data["zip_code"],
                "password": password
            })
            
            session.commit()
            session.close()
            
            self.log_info(f"Successfully saved user to database: {user_data['company_email']}")
            return True
            
        except Exception as e:
            self.log_error(f"Error saving user to database: {e}")
            if 'session' in locals():
                session.rollback()
                session.close()
            return False
    
    def validate_user_data(self) -> bool:
        """
        For Freshservice sync, we don't need user input validation
        since we're fetching data from API
        """
        return True
    
    def execute(self) -> Dict[str, Any]:
        """
        Execute the Freshservice sync operation - this is the implementation from the first execute method
        """
        self.log_info("Starting Freshservice onboarding sync...")
        
        # For this sync we don't need user data, use default values
        hours_back = 24
        
        # Get API credentials
        if not self.get_secrets():
            return {
                "status": "failed",
                "error": "Failed to retrieve API credentials from AWS Secrets Manager",
                "message": "Unable to access Freshservice and JumpCloud APIs"
            }
        
        try:
            # Get recent onboarding tickets from Freshservice
            self.log_info(f"Fetching onboarding tickets from last {hours_back} hours...")
            ticket_ids = self.get_recent_onboarding_tickets(hours_back)
            
            if not ticket_ids:
                self.log_info("No onboarding tickets found in the specified time window")
                return {
                    "status": "completed",
                    "message": "No new onboarding tickets to process",
                    "tickets_processed": 0,
                    "users_created": 0,
                    "users_skipped": 0,
                    "sync_window_hours": hours_back,
                    "processed_tickets": [],
                    "sync_timestamp": datetime.now().isoformat()
                }
            
            self.log_info(f"Found {len(ticket_ids)} tickets to process")
            
            # Process each ticket
            users_created = 0
            users_skipped = 0
            processed_tickets = []
            
            for ticket_id in ticket_ids:
                self.log_info(f"Processing ticket {ticket_id}...")
                
                # Get requested items for this ticket
                requested_items = self.get_ticket_requested_items(ticket_id)
                
                for item in requested_items:
                    custom_fields = item.get("custom_fields", {})
                    
                    # Skip if no essential data
                    if not custom_fields.get("first_name") or not custom_fields.get("last_name"):
                        self.log_info(f"Skipping ticket {ticket_id} - missing essential user data")
                        users_skipped += 1
                        continue
                    
                    # Transform data
                    user_data = self.transform_freshservice_data(ticket_id, custom_fields)
                    
                    self.log_info(f"Ticket {ticket_id} - User: {user_data['display_name']} ({user_data['company_email']})")
                    self.log_info(f"Department: {user_data['department']}, Title: {user_data['title']}")
                    
                    # Save to database
                    result = self.save_user_to_database(user_data)
                    if result == "skipped":
                        users_skipped += 1
                        self.log_info(f"User skipped (already exists): {user_data['company_email']}")
                    elif result:
                        users_created += 1
                        self.log_info(f"User created: {user_data['company_email']}")
                    else:
                        users_skipped += 1
                        self.log_error(f"Failed to create user: {user_data['company_email']}")
                    
                    processed_tickets.append({
                        "ticket_id": ticket_id,
                        "user_name": user_data['display_name'],
                        "company_email": user_data['company_email'],
                        "department": user_data['department'],
                        "title": user_data['title']
                    })
            
            self.log_info(f"Sync completed. Created: {users_created}, Skipped: {users_skipped}")
            
            return {
                "status": "completed",
                "message": f"Processed {len(ticket_ids)} tickets from Freshservice",
                "tickets_processed": len(ticket_ids),
                "users_created": users_created,
                "users_skipped": users_skipped,
                "sync_window_hours": hours_back,
                "processed_tickets": processed_tickets,
                "sync_timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            error_msg = f"Error during Freshservice sync: {str(e)}"
            self.log_error(error_msg)
            return {
                "status": "failed",
                "error": error_msg,
                "message": "Failed to sync onboarding data from Freshservice"
            }

def main():
    script = FreshserviceOnboardingSync()
    script.run()

if __name__ == "__main__":
    main()
