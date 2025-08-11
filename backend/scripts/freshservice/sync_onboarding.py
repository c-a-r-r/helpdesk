#!/usr/bin/env python3
"""
Freshservice Onboarding Sync Script (Journeys-native)
Retrieves onboarding requests from Freshservice and creates user records in the helpdesk CRM
"""
import sys
import os
import json
import requests
import secrets
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv

# Load environment variables from .env file
from pathlib import Path
env_path = Path(__file__).parent.parent.parent.parent / '.env'
if env_path.exists():
    with open(env_path) as f:
        for line in f:
            if line.strip() and not line.startswith('#'):
                key, value = line.strip().split('=', 1)
                os.environ[key] = value

# Make your package paths available (as in your original)
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from base_script import BaseUserScript

class FreshserviceOnboardingSync(BaseUserScript):
    """Syncs Freshservice Onboarding Requests (Journeys) to helpdesk CRM"""
    
    def __init__(self):
        super().__init__()
        self.freshservice_api_key: Optional[str] = None
        self.region = "us-west-2"
        self.freshservice_domain = os.getenv("FRESHSERVICE_DOMAIN", "americor.freshservice.com")
        self.default_headers = {"Accept": "application/json"}
        self.base_url = f"https://{self.freshservice_domain}/api/v2"

        # workspace handling
        # If you know your main workspace (e.g., IT), set FRESHSERVICE_WORKSPACE_ID in env.
        self.workspace_id = os.getenv("FRESHSERVICE_WORKSPACE_ID")  # string or None

    # ------------------------------
    # Secrets
    # ------------------------------
    def get_secrets(self) -> bool:
        """
        Get configuration from AWS Secrets Manager or fallback to .env file
        """
        try:
            from aws_secrets import get_freshdesk_credentials
            secrets = get_freshdesk_credentials()
            if secrets and secrets.get('api_key'):
                self.freshservice_api_key = secrets['api_key']
                print("Successfully retrieved Freshservice API key from AWS Secrets Manager")
                return True
        except ImportError:
            print("Warning: AWS Secrets Manager not available, falling back to .env file")
        except Exception as e:
            print(f"Error retrieving secrets from AWS: {e}")
        
        # Fallback to .env file
        try:
            load_dotenv()
            api_key = os.getenv('FRESHDESK_API_KEY')
            if api_key:
                self.freshservice_api_key = api_key
                print("Using Freshservice API key from .env file (fallback)")
                return True
            else:
                print("Error: FRESHDESK_API_KEY not found in environment variables")
                return False
        except Exception as e:
            print(f"Error loading .env file: {e}")
            return False

    # ------------------------------
    # HTTP helpers
    # ------------------------------
    def _headers(self, workspace_id: Optional[str] = None) -> Dict[str, str]:
        h = dict(self.default_headers)
        if workspace_id:
            h["X-Flow-Workspace-Id"] = str(workspace_id)
        return h

    def _get(self, path: str, params: Dict[str, Any] = None, workspace_id: Optional[str] = None) -> requests.Response:
        url = f"{self.base_url.rstrip('/')}/{path.lstrip('/')}"
        return requests.get(url, auth=(self.freshservice_api_key, "X"), headers=self._headers(workspace_id), params=params, timeout=30)

    def list_workspaces(self) -> List[str]:
        """Return list of workspace IDs (strings). If single-workspace, return []."""
        try:
            r = self._get("workspaces")
            if r.status_code != 200:
                return []
            data = r.json()
            return [str(w["id"]) for w in data.get("workspaces", [])]
        except Exception:
            return []

    # ------------------------------
    # Onboarding requests (Journeys)
    # ------------------------------
    def list_recent_onboarding_requests(self, hours_back: int = 5) -> List[Dict[str, Any]]:
        """
        Fetch onboarding_requests updated in the last N hours.
        Tries:
          1) explicit workspace (env var) if provided
          2) default (no workspace header)
          3) all workspaces discovered via /workspaces
        Returns list of onboarding_request dicts.
        """
        print(f"DEBUG: list_recent_onboarding_requests called with hours_back={hours_back}")
        since_iso = (datetime.now(timezone.utc) - timedelta(hours=hours_back)).strftime("%Y-%m-%dT%H:%M:%SZ")
        print(f"DEBUG: Looking for requests since {since_iso}")
        params = {"page": 1, "per_page": 100}
        results: List[Dict[str, Any]] = []

        def scan_ctx(wid: Optional[str]) -> None:
            page = 1
            while True:
                params["page"] = page
                r = self._get("onboarding_requests", params=params, workspace_id=wid)
                if r.status_code != 200:
                    self.log_warning(f"/onboarding_requests {wid or '(default)'}: {r.status_code} {r.text[:200]}")
                    break
                data = r.json()
                items = data.get("onboarding_requests", [])
                if not items:
                    break
                # filter by updated_since manually (API may not accept updated_since for this endpoint in all accounts)
                for ob in items:
                    updated_at = ob.get("updated_at") or ob.get("created_at")
                    if updated_at and updated_at >= since_iso:
                        results.append({**ob, "_workspace_id": wid})
                page += 1

        # 1) explicit workspace if provided
        if self.workspace_id:
            self.log_info(f"Scanning onboarding requests in workspace {self.workspace_id} since {since_iso}")
            scan_ctx(self.workspace_id)

        # 2) default context
        self.log_info(f"Scanning onboarding requests (default workspace) since {since_iso}")
        scan_ctx(None)

        # 3) all workspaces
        for wid in self.list_workspaces():
            # skip if same as explicit
            if self.workspace_id and str(wid) == str(self.workspace_id):
                continue
            self.log_info(f"Scanning onboarding requests in workspace {wid} since {since_iso}")
            scan_ctx(wid)

        self.log_info(f"Found {len(results)} onboarding requests across contexts")
        return results

    def get_onboarding_request_full(self, onboarding_id: int, workspace_id: Optional[str]) -> Optional[Dict[str, Any]]:
        r = self._get(f"onboarding_requests/{onboarding_id}", workspace_id=workspace_id)
        if r.status_code != 200:
            self.log_error(f"Failed to fetch onboarding_request {onboarding_id}: {r.status_code} {r.text[:200]}")
            return None
        return r.json().get("onboarding_request")

    # ------------------------------
    # Transform fields -> CRM user
    # ------------------------------
    def transform_freshservice_fields(self, onboarding_fields: Dict[str, Any], fallback_ticket_id: Optional[int]) -> Dict[str, Any]:
        """
        Map Onboarding Request fields (cf_*, msf_*, doj, etc.) to your CRM schema.
        Example fields observed:
          cf_first_name, cf_last_name, cf_display_name, cf_email, cf_phone_number,
          cf_title, cf_department, cf_manager, cf_city, cf_state, cf_zip_code,
          cf_strett_name (typo), msf_company (list), msf_address_type (list),
          msf_location_first_day (list), doj (Start Date), cf_extras_details, ...
        """
        # Normalize multi-select/list values
        def norm(v):
            if isinstance(v, list):
                return ", ".join(map(str, v))
            return v

        first = onboarding_fields.get("cf_first_name", "") or ""
        last  = onboarding_fields.get("cf_last_name", "") or ""
        display_name = onboarding_fields.get("cf_display_name", f"{first} {last}".strip())

        # company can be list (msf_company: ['Americor'])
        company_raw = onboarding_fields.get("msf_company")
        company = (company_raw[0] if isinstance(company_raw, list) and company_raw else company_raw) or ""
        company_l = str(company).lower()

        # username and company email
        username = f"{first.lower()}.{last.lower()}" if first and last else ""
        domain = {"credit9": "credit9.com", "americor": "americor.com"}.get(company_l, "americor.com")
        company_email = f"{username}@{domain}" if username else ""

        # Start date: doj ("08-29-2025" or similar). Keep robust parsing.
        start_date_str = onboarding_fields.get("doj", "")
        formatted_start_date = None
        if start_date_str:
            try:
                from dateutil import parser
                parsed = parser.parse(start_date_str)
                formatted_start_date = parsed.strftime("%Y-%m-%d %H:%M:%S")
            except Exception as e:
                self.log_warning(f"Could not parse doj '{start_date_str}': {e}")

        # Address fields (note: schema typo cf_strett_name)
        street = onboarding_fields.get("cf_strett_name") or onboarding_fields.get("cf_street_name") or ""

        password = secrets.token_urlsafe(16)

        user_data = {
            "freshservice_ticket_id": str(fallback_ticket_id or onboarding_fields.get("ticket_id") or ""),
            "username": username,
            "first_name": first,
            "last_name": last,
            "display_name": display_name,
            "company_email": company_email,
            "personal_email": onboarding_fields.get("cf_email", ""),

            "company": company or "",
            "title": onboarding_fields.get("cf_title", ""),
            "department": onboarding_fields.get("cf_department", ""),  # single dept observed
            "manager": onboarding_fields.get("cf_manager", ""),
            "start_date": formatted_start_date,

            "phone_number": str(onboarding_fields.get("cf_phone_number", "")),

            "address_type": norm(onboarding_fields.get("msf_address_type", "")),
            "street_name": street,
            "city": onboarding_fields.get("cf_city", ""),
            "state": onboarding_fields.get("cf_state", ""),
            "zip_code": str(onboarding_fields.get("cf_zip_code", "")),

            "location_first_day": norm(onboarding_fields.get("msf_location_first_day", "")),

            "extras_details": onboarding_fields.get("cf_extras_details", ""),
            "hostname": "",

            "onboarding_status": "pending",
            "sync_source": "freshservice",
            "sync_timestamp": datetime.now().isoformat(),
            "password": password,
        }
        return user_data

    # ------------------------------
    # Validation (required by BaseUserScript)
    # ------------------------------
    def validate_user_data(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate user data before processing"""
        errors = []
        warnings = []
        
        # Required fields
        required_fields = ["first_name", "last_name", "company_email"]
        for field in required_fields:
            if not user_data.get(field):
                errors.append(f"Missing required field: {field}")
        
        # Email validation
        email = user_data.get("company_email", "")
        if email and "@" not in email:
            errors.append("Invalid email format")
        
        # Username validation
        if user_data.get("username") and not user_data["username"].replace(".", "").replace("_", "").isalnum():
            warnings.append("Username contains special characters")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }

    # ------------------------------
    # DB write (unchanged from your logic, just called with new mapping)
    # ------------------------------
    def save_user_to_database(self, user_data: Dict[str, Any]) -> bool:
        try:
            from sqlalchemy import create_engine, text
            from sqlalchemy.orm import sessionmaker

            db_host = os.getenv('DB_HOST', 'localhost')
            db_port = os.getenv('DB_PORT', '3306')
            db_user = os.getenv('DB_USER', 'helpdesk')
            db_password = os.getenv('DB_PASSWORD', 'helpdesk123')
            db_name = os.getenv('DB_NAME', 'helpdesk_crm')

            connection_string = f"mysql+pymysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
            engine = create_engine(connection_string)
            Session = sessionmaker(bind=engine)
            session = Session()

            # Check existing
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

            insert_query = text("""
                INSERT INTO onboarding (
                    username, first_name, last_name, display_name, company_email, personal_email, title, 
                    department, manager, start_date, phone_number, company, status, notes, 
                    ticket_number, location_first_day, address_type, street_name, city, state, zip_code,
                    password, created_by, created_at, updated_at
                ) VALUES (
                    :username, :first_name, :last_name, :display_name, :company_email, :personal_email, :title,
                    :department, :manager, :start_date, :phone_number, :company, :status, :notes,
                    :ticket_number, :location_first_day, :address_type, :street_name, :city, :state, :zip_code,
                    :password, :created_by, NOW(), NOW()
                )
            """)

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
                "status": "PENDING",
                "notes": "",
                "ticket_number": str(user_data["freshservice_ticket_id"]),
                "location_first_day": user_data["location_first_day"] or "Remote",
                "address_type": user_data["address_type"] or "RESIDENTIAL",
                "street_name": user_data["street_name"],
                "city": user_data["city"],
                "state": user_data["state"],
                "zip_code": user_data["zip_code"],
                "password": user_data["password"],
                "created_by": "freshservice-sync"
            })

            session.commit()
            session.close()
            self.log_info(f"Saved user to DB: {user_data['company_email']}")
            return True

        except Exception as e:
            self.log_error(f"DB error: {e}")
            if 'session' in locals():
                session.rollback()
                session.close()
            return False

    # ------------------------------
    # Execute
    # ------------------------------
    def execute(self) -> Dict[str, Any]:
        print("DEBUG: Starting execute() method")
        self.log_info("Starting Freshservice onboarding sync (Journeys)…")

        hours_back = int(os.getenv("SYNC_WINDOW_HOURS", "24"))  # Changed from 5 to 24 hours
        print(f"DEBUG: Sync window set to {hours_back} hours")

        print("DEBUG: About to call get_secrets()")
        if not self.get_secrets():
            print("DEBUG: get_secrets() failed")
            return {
                "status": "failed",
                "error": "Failed to retrieve Freshservice API credentials",
                "message": "Unable to access Freshservice API",
                "execution_logs": self.get_execution_logs()
            }
        print("DEBUG: get_secrets() succeeded")

        try:
            print("DEBUG: About to call list_recent_onboarding_requests()")
            onboarding_list = self.list_recent_onboarding_requests(hours_back=hours_back)
            print(f"DEBUG: Found {len(onboarding_list) if onboarding_list else 0} onboarding requests")
            if not onboarding_list:
                self.log_info("No onboarding requests found in the time window")
                return {
                    "status": "completed",
                    "message": "No new onboarding requests to process",
                    "tickets_processed": 0,
                    "users_created": 0,
                    "users_skipped": 0,
                    "sync_window_hours": hours_back,
                    "processed_tickets": [],
                    "sync_timestamp": datetime.now().isoformat(),
                    "execution_logs": self.get_execution_logs()
                }

            users_created = 0
            users_skipped = 0
            processed = []

            for ob in onboarding_list:
                ob_id = ob.get("id")
                wid   = ob.get("_workspace_id")  # may be None (default context)
                full  = self.get_onboarding_request_full(ob_id, wid)
                if not full:
                    continue

                fields = full.get("fields") or {}
                # minimal sanity: require first/last
                if not fields.get("cf_first_name") or not fields.get("cf_last_name"):
                    self.log_info(f"Skipping onboarding_request {ob_id} - missing first/last name")
                    users_skipped += 1
                    continue

                # Find the SR ticket id (if present on the object)
                fallback_ticket_id = full.get("ticket_id") or ob.get("ticket_id")

                user_data = self.transform_freshservice_fields(fields, fallback_ticket_id)
                self.log_info(f"OB {ob_id} -> {user_data['display_name']} ({user_data['company_email']})")

                result = self.save_user_to_database(user_data)
                if result == "skipped":
                    users_skipped += 1
                elif result:
                    users_created += 1
                else:
                    users_skipped += 1

                processed.append({
                    "onboarding_id": ob_id,
                    "ticket_id": user_data["freshservice_ticket_id"],
                    "user_name": user_data["display_name"],
                    "company_email": user_data["company_email"],
                    "department": user_data["department"],
                    "title": user_data["title"]
                })

            self.log_info(f"Sync completed. Created: {users_created}, Skipped: {users_skipped}")
            return {
                "status": "completed",
                "message": f"Processed {len(processed)} onboarding requests",
                "tickets_processed": len(processed),
                "users_created": users_created,
                "users_skipped": users_skipped,
                "sync_window_hours": hours_back,
                "processed_tickets": processed,
                "sync_timestamp": datetime.now().isoformat(),
                "execution_logs": self.get_execution_logs()
            }

        except Exception as e:
            err = f"Error during Freshservice onboarding sync: {e}"
            self.log_error(err)
            return {
                "status": "failed",
                "error": err,
                "message": "Failed to sync onboarding data from Freshservice",
                "execution_logs": self.get_execution_logs()
            }

    def run(self):
        """Override BaseUserScript.run() to bypass stdin reading"""
        print("DEBUG: Custom run() method called")
        try:
            print("DEBUG: About to call execute() directly")
            result = self.execute()
            print("DEBUG: execute() completed successfully")
            self.output_success(result)
        except Exception as e:
            print(f"DEBUG: Exception in run(): {e}")
            self.output_error(f"Script execution failed: {str(e)}")

def main():
    print("DEBUG: main() function called")
    script = FreshserviceOnboardingSync()
    print("DEBUG: FreshserviceOnboardingSync instance created")
    print("DEBUG: About to call script.run()")
    script.run()
    print("DEBUG: script.run() completed")

if __name__ == "__main__":
    print("DEBUG: Script starting - __name__ == '__main__'")
    main()