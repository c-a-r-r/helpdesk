import os
import sys
sys.path.append('/app')

from database import SessionLocal, engine
from sqlalchemy import text

def add_missing_columns():
    db = SessionLocal()
    
    try:
        print('🚀 Adding missing individual script status columns...')
        
        # Check if columns exist first
        result = db.execute(text("""
            SELECT COLUMN_NAME 
            FROM information_schema.COLUMNS 
            WHERE TABLE_SCHEMA = DATABASE() 
            AND TABLE_NAME = 'onboarding' 
            AND COLUMN_NAME IN ('bind_machine_status', 'add_alias_status', 'force_pwd_change_status')
        """))
        
        existing_columns = [row[0] for row in result]
        print(f'📋 Existing status columns: {existing_columns}')
        
        columns_to_add = [
            ('bind_machine_status', "ALTER TABLE onboarding ADD COLUMN bind_machine_status ENUM('pending', 'running', 'completed', 'failed') DEFAULT 'pending'"),
            ('add_alias_status', "ALTER TABLE onboarding ADD COLUMN add_alias_status ENUM('pending', 'running', 'completed', 'failed') DEFAULT 'pending'"),
            ('force_pwd_change_status', "ALTER TABLE onboarding ADD COLUMN force_pwd_change_status ENUM('pending', 'running', 'completed', 'failed') DEFAULT 'pending'")
        ]
        
        for column_name, sql in columns_to_add:
            if column_name not in existing_columns:
                print(f'➕ Adding column: {column_name}')
                db.execute(text(sql))
                print(f'✅ Added column: {column_name}')
            else:
                print(f'⚠️  Column {column_name} already exists')
        
        db.commit()
        print('🎉 Migration completed successfully!')
        
    except Exception as e:
        print(f'❌ Error: {e}')
        db.rollback()
        return False
    finally:
        db.close()
    
    return True

if __name__ == '__main__':
    success = add_missing_columns()
    sys.exit(0 if success else 1)
