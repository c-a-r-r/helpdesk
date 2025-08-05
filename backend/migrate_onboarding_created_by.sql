-- MariaDB Migration: Add created_by field to onboarding table
-- Run this script in your MariaDB container

-- Check if created_by column already exists
SELECT COLUMN_NAME 
FROM INFORMATION_SCHEMA.COLUMNS 
WHERE TABLE_SCHEMA = DATABASE() 
  AND TABLE_NAME = 'onboarding' 
  AND COLUMN_NAME = 'created_by';

-- Add created_by column if it doesn't exist
ALTER TABLE onboarding 
ADD COLUMN IF NOT EXISTS created_by VARCHAR(255) NULL 
COMMENT 'Email of user who created record, or "freshdesk-sync" for automated';

-- Verify the column was added
DESCRIBE onboarding;

-- Optionally update existing records to indicate they were created via sync
-- (Only run this if you want to mark existing records)
-- UPDATE onboarding SET created_by = 'freshdesk-sync' WHERE created_by IS NULL;
