"""
Migration script to add offboarding_script_logs table
Run this after updating models.py with the OffboardingScriptLog model
"""

import os
import sys
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Add parent directory to path to import database module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

load_dotenv()

def get_database_url():
    """Get database URL based on environment configuration"""
    DB_TYPE = os.getenv("DB_TYPE", "sqlite")
    
    if DB_TYPE.lower() == "sqlite":
        DB_PATH = os.getenv("DB_PATH", "./helpdesk_crm.db")
        return f"sqlite:///{DB_PATH}"
    else:
        DB_HOST = os.getenv("DB_HOST", "localhost")
        DB_PORT = os.getenv("DB_PORT", "3306")
        DB_USER = os.getenv("DB_USER", "root")
        DB_PASSWORD = os.getenv("DB_PASSWORD", "")
        DB_NAME = os.getenv("DB_NAME", "helpdesk_crm")
        return f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

def create_offboarding_script_logs_table():
    """Create the offboarding_script_logs table"""
    
    # Get database URL
    database_url = get_database_url()
    engine = create_engine(database_url)
    
    # SQL to create the table (MariaDB syntax)
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS offboarding_script_logs (
        id INT AUTO_INCREMENT PRIMARY KEY,
        offboarding_id INT NOT NULL,
        script_type VARCHAR(100) NOT NULL,
        script_name VARCHAR(200) NOT NULL,
        status VARCHAR(20) NOT NULL DEFAULT 'running',
        output TEXT,
        error_message TEXT,
        executed_by VARCHAR(255) NOT NULL,
        execution_time_seconds INT,
        additional_params JSON,
        started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        completed_at TIMESTAMP NULL,
        FOREIGN KEY (offboarding_id) REFERENCES offboarding (id) ON DELETE CASCADE
    );
    """
    
    # Create indexes for better performance
    index_statements = [
        """CREATE INDEX IF NOT EXISTS idx_offboarding_script_logs_offboarding_id 
           ON offboarding_script_logs (offboarding_id);""",
        """CREATE INDEX IF NOT EXISTS idx_offboarding_script_logs_status 
           ON offboarding_script_logs (status);""",
        """CREATE INDEX IF NOT EXISTS idx_offboarding_script_logs_started_at 
           ON offboarding_script_logs (started_at DESC);"""
    ]
    
    try:
        with engine.connect() as connection:
            # Create table
            connection.execute(text(create_table_sql))
            print("✅ Created offboarding_script_logs table")
            
            # Create indexes one by one
            for i, index_sql in enumerate(index_statements, 1):
                connection.execute(text(index_sql))
                print(f"✅ Created index {i}/3 for offboarding_script_logs table")
            
            connection.commit()
            print("✅ Migration completed successfully")
            
    except Exception as e:
        print(f"❌ Error creating table: {e}")
        raise

if __name__ == "__main__":
    print("🚀 Running migration: add_offboarding_script_logs")
    create_offboarding_script_logs_table()
