#!/usr/bin/env python3
"""
Simple migration runner script
"""

import sys
import os

# Add backend directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def main():
    """Run the name fields migration"""
    print("🚀 Starting name fields migration...")
    
    try:
        from migrations.update_name_fields import run_migration
        run_migration()
        print("✅ Migration completed successfully!")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure you're running this from the backend directory")
        sys.exit(1)
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
