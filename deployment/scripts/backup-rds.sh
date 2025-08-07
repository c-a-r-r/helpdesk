#!/bin/bash

# RDS Backup Script for Production
# This script creates backups of your RDS database

set -e

# Configuration
RDS_INSTANCE_ID="helpdesk-db-prod"
BACKUP_RETENTION_DAYS=7
DATE=$(date +%Y%m%d_%H%M%S)
LOG_FILE="/var/log/helpdesk-backup.log"

echo "$(date): Starting RDS backup process" >> $LOG_FILE

# Create RDS snapshot
SNAPSHOT_ID="helpdesk-manual-backup-$DATE"

echo "$(date): Creating RDS snapshot: $SNAPSHOT_ID" >> $LOG_FILE

aws rds create-db-snapshot \
    --db-instance-identifier $RDS_INSTANCE_ID \
    --db-snapshot-identifier $SNAPSHOT_ID \
    --region ${AWS_REGION:-us-west-2}

if [ $? -eq 0 ]; then
    echo "$(date): RDS snapshot created successfully: $SNAPSHOT_ID" >> $LOG_FILE
    
    # Optional: Send notification
    # aws sns publish --topic-arn "arn:aws:sns:region:account:helpdesk-alerts" \
    #     --message "RDS backup completed: $SNAPSHOT_ID"
else
    echo "$(date): ERROR: Failed to create RDS snapshot" >> $LOG_FILE
    exit 1
fi

# Clean up old snapshots (keep only last 7 days of manual backups)
echo "$(date): Cleaning up old manual snapshots" >> $LOG_FILE

aws rds describe-db-snapshots \
    --db-instance-identifier $RDS_INSTANCE_ID \
    --snapshot-type manual \
    --query "DBSnapshots[?SnapshotCreateTime<=\`$(date -d "-$BACKUP_RETENTION_DAYS days" -u +%Y-%m-%dT%H:%M:%S.%3NZ)\`].DBSnapshotIdentifier" \
    --output text | tr '\t' '\n' | while read snapshot; do
    if [[ $snapshot == helpdesk-manual-backup-* ]]; then
        echo "$(date): Deleting old snapshot: $snapshot" >> $LOG_FILE
        aws rds delete-db-snapshot --db-snapshot-identifier $snapshot --region ${AWS_REGION:-us-west-2}
    fi
done

echo "$(date): Backup process completed" >> $LOG_FILE
