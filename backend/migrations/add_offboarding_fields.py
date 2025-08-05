#!/usr/bin/env python3
"""
Migration: Add password and created_by fields to offboarding table
Date: 2025-08-04
Description: Adds password (VARCHAR(16)) and created_by (VARCHAR(255)) fields to the offboarding table
"""

import os
import sys
import logging
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError, ProgrammingError
from dotenv import load_dotenv

# Add the parent directory to sys.path to import from backend
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_database_url():
    """Get database URL from environment variables"""
    DB_TYPE = os.getenv("DB_TYPE", "mariadb")
    
    if DB_TYPE.lower() == "mariadb":
        DB_HOST = os.getenv("DB_HOST", "localhost")
        DB_PORT = os.getenv("DB_PORT", "3306")
        DB_USER = os.getenv("DB_USER", "helpdesk")
        DB_PASSWORD = os.getenv("DB_PASSWORD", "helpdesk123")
        DB_NAME = os.getenv("DB_NAME", "helpdesk_crm")
        return f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    else:
        raise ValueError(f"Unsupported database type: {DB_TYPE}")

def check_column_exists(engine, table_name, column_name):
    """Check if a column exists in a table"""
    try:
        with engine.connect() as connection:
            result = connection.execute(text("""
                SELECT COUNT(*) as count
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE table_schema = DATABASE() 
                AND table_name = :table_name 
                AND column_name = :column_name
            """), {"table_name": table_name, "column_name": column_name})
            
            count = result.fetchone()[0]
            return count > 0
    except Exception as e:
        logger.error(f"Error checking if column {column_name} exists: {e}")
        return False

def add_offboarding_fields():
    """Add password and created_by fields to offboarding table"""
    try:
        # Get database URL
        database_url = get_database_url()
        logger.info(f"Connecting to database...")
        
        # Create engine
        engine = create_engine(database_url, echo=True)
        
        # Test connection
        with engine.connect() as connection:
            logger.info("Database connection successful")
            
            # Check if password column exists
            if not check_column_exists(engine, "offboarding", "password"):
                logger.info("Adding password column to offboarding table...")
                connection.execute(text("""
                    ALTER TABLE offboarding 
                    ADD COLUMN password VARCHAR(16) NULL
                """))
                connection.commit()
                logger.info("✅ Password column added successfully")
            else:
                logger.info("Password column already exists")
            
            # Check if created_by column exists
            if not check_column_exists(engine, "offboarding", "created_by"):
                logger.info("Adding created_by column to offboarding table...")
                connection.execute(text("""
                    ALTER TABLE offboarding 
                    ADD COLUMN created_by VARCHAR(255) NULL
                """))
                connection.commit()
                logger.info("✅ Created_by column added successfully")
            else:
                logger.info("Created_by column already exists")
                
            logger.info("🎉 Migration completed successfully!")
            
    except OperationalError as e:
        if "Can't connect to MySQL server" in str(e) or "Connection refused" in str(e):
            logger.error("❌ Cannot connect to MariaDB. Make sure the database container is running.")
            logger.info("💡 Try running: docker-compose up db")
        else:
            logger.error(f"❌ Database operation error: {e}")
        sys.exit(1)
    except ProgrammingError as e:
        if "Table 'offboarding' doesn't exist" in str(e):
            logger.error("❌ The offboarding table doesn't exist. Please run the main database initialization first.")
            logger.info("💡 Try running: python init_db.py")
        else:
            logger.error(f"❌ SQL programming error: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    logger.info("🚀 Starting migration: Add password and created_by fields to offboarding table")
    add_offboarding_fields()
