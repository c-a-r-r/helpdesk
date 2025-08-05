#!/usr/bin/env python3
"""
Migration script to add password and created_by fields to offboarding table.
"""

import os
import sys
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Add the current directory to the path so we can import modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

load_dotenv()

def migrate_database():
    """Add password and created_by columns to offboarding table if they don't exist"""
    
    # Database configuration
    DB_TYPE = os.getenv("DB_TYPE", "sqlite")
    
    if DB_TYPE.lower() == "sqlite":
        DB_PATH = os.getenv("DB_PATH", "./helpdesk_crm.db")
        DATABASE_URL = f"sqlite:///{DB_PATH}"
        engine = create_engine(DATABASE_URL, echo=True)
    else:
        DB_HOST = os.getenv("DB_HOST", "localhost")
        DB_PORT = os.getenv("DB_PORT", "3306")
        DB_USER = os.getenv("DB_USER", "root")
        DB_PASSWORD = os.getenv("DB_PASSWORD", "")
        DB_NAME = os.getenv("DB_NAME", "helpdesk_crm")
        DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
        engine = create_engine(DATABASE_URL, echo=True)
    
    with engine.connect() as connection:
        # Check if offboarding table exists
        try:
            result = connection.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='offboarding'"))
            if not result.fetchone():
                print("Offboarding table does not exist. Creating tables...")
                # Import and create tables
                from models import Base
                from database import engine as db_engine
                Base.metadata.create_all(bind=db_engine)
                print("Tables created successfully!")
                return
        except Exception as e:
            print(f"Error checking table existence: {e}")
            return
        
        # Check if password column exists
        try:
            connection.execute(text("SELECT password FROM offboarding LIMIT 1"))
            print("Password column already exists")
        except Exception:
            print("Adding password column...")
            try:
                connection.execute(text("ALTER TABLE offboarding ADD COLUMN password VARCHAR(16)"))
                connection.commit()
                print("Password column added successfully!")
            except Exception as e:
                print(f"Error adding password column: {e}")
        
        # Check if created_by column exists
        try:
            connection.execute(text("SELECT created_by FROM offboarding LIMIT 1"))
            print("Created_by column already exists")
        except Exception:
            print("Adding created_by column...")
            try:
                connection.execute(text("ALTER TABLE offboarding ADD COLUMN created_by VARCHAR(255)"))
                connection.commit()
                print("Created_by column added successfully!")
            except Exception as e:
                print(f"Error adding created_by column: {e}")
        
        print("Migration completed!")

if __name__ == "__main__":
    migrate_database()
