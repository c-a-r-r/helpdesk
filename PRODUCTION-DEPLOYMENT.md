# Production Deployment Guide

## Pre-Deployment Checklist

### 1. Environment Setup ✅
- [ ] AWS EC2 instance running
- [ ] Docker and Docker Compose installed
- [ ] SSL certificates generated (`sudo certbot certonly --nginx -d helpdesk.amer.biz`)
- [ ] `.env` file configured with production values
- [ ] RDS database accessible

### 2. Code Deployment ✅
- [ ] Code synced via rsync to production server
- [ ] All files in `/home/ec2-user/helpdesk-crm/`
- [ ] File permissions correct (`ec2-user:ec2-user`)

### 3. SSL Certificate Check
```bash
# Verify certificates exist
ls -la /etc/letsencrypt/live/helpdesk.amer.biz/
```

### 4. Database Connection
```bash
# Test RDS connection
mysql -h YOUR_RDS_ENDPOINT -u helpdesk -p helpdesk_crm
```

## Deployment Steps

### Method 1: Quick Deployment (Recommended)
```bash
# Optimized sync excluding unnecessary folders
./scripts/deploy-prod.sh
```

### Method 2: Manual Sync and Deploy
```bash
# Sync files excluding docs and terraform
rsync -avz --delete \
    --exclude='terraform/' \
    --exclude='docs/' \
    --exclude='.git/' \
    --exclude='node_modules/' \
    --exclude='__pycache__/' \
    -e "ssh -i ~/Documents/my-keys/dms-test.pem" \
    . ec2-user@ec2-44-245-190-156.us-west-2.compute.amazonaws.com:~/helpdesk-crm/

# Then deploy
ssh -i ~/Documents/my-keys/dms-test.pem ec2-user@ec2-44-245-190-156.us-west-2.compute.amazonaws.com
cd helpdesk-crm
./scripts/copy-ssl-certs.sh
docker-compose -f docker-compose.prod.yml up -d --build
```

### Method 3: Full Deployment Script
```bash
# Transfer the deploy script and run:
scp -i ~/Documents/my-keys/dms-test.pem deployment/deploy.sh ec2-user@ec2-44-245-190-156.us-west-2.compute.amazonaws.com:~/
ssh -i ~/Documents/my-keys/dms-test.pem ec2-user@ec2-44-245-190-156.us-west-2.compute.amazonaws.com
chmod +x deploy.sh
./deploy.sh
```

## Post-Deployment Verification

### 1. Container Health
```bash
docker-compose -f docker-compose.prod.yml ps
docker-compose -f docker-compose.prod.yml logs
```

### 2. Application Access
- [ ] HTTP: http://helpdesk.amer.biz redirects to HTTPS
- [ ] HTTPS: https://helpdesk.amer.biz loads correctly
- [ ] Health Check: https://helpdesk.amer.biz/health returns "healthy"
- [ ] API Docs: https://helpdesk.amer.biz/docs accessible

### 3. SSL Certificate
```bash
# Check certificate validity
openssl x509 -in nginx/ssl/fullchain.pem -text -noout | grep "Not After"
```

### 4. Database Connection
```bash
# Check backend logs for DB connection
docker-compose -f docker-compose.prod.yml logs backend | grep -i database
```

## Troubleshooting

### SSL Issues
```bash
# Recreate certificates and restart nginx
./scripts/copy-ssl-certs.sh
docker-compose -f docker-compose.prod.yml restart nginx
```

### Container Issues
```bash
# View detailed logs
docker-compose -f docker-compose.prod.yml logs [service_name]

# Restart specific service
docker-compose -f docker-compose.prod.yml restart [service_name]
```

### Database Issues
```bash
# Check environment variables
cat .env | grep DB_

# Test direct connection
mysql -h $DB_HOST -u $DB_USER -p$DB_PASSWORD $DB_NAME
```

## Monitoring

### System Monitoring
```bash
# Check system resources
free -h
df -h
docker stats
```

### Application Monitoring
```bash
# Monitor application logs
docker-compose -f docker-compose.prod.yml logs -f

# Check container health
docker-compose -f docker-compose.prod.yml ps
```

## Backup

### Manual Backup
```bash
# Create backup before changes
mkdir -p ~/backups/$(date +%Y%m%d_%H%M%S)
cp -r /home/ec2-user/helpdesk-crm ~/backups/$(date +%Y%m%d_%H%M%S)/
```

### Database Backup
```bash
# Backup RDS database
mysqldump -h $DB_HOST -u $DB_USER -p$DB_PASSWORD $DB_NAME > backup_$(date +%Y%m%d_%H%M%S).sql
```
