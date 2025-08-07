# 🚀 Production Deployment Checklist for Helpdesk CRM

## Pre-Deployment Requirements ✅

### AWS Account Setup
- [ ] AWS Account configured with proper billing
- [ ] AWS CLI installed and configured
- [ ] IAM user/role with required permissions:
  - EC2 (Full access)
  - RDS (Full access)
  - VPC (Full access)
  - Secrets Manager (Full access)
  - CloudWatch (Full access)
  - Certificate Manager (Read/Write)

### Domain and SSL
- [ ] Domain name purchased and configured
- [ ] DNS management access
- [ ] SSL certificate obtained (Let's Encrypt or ACM)

### Third-Party Integrations
- [ ] JumpCloud organization and OAuth app configured
- [ ] Google Workspace service account (if using)
- [ ] FreshService API access (if using)
- [ ] Automox API access (if using)

---

## Infrastructure Deployment ⚡

### Step 1: Terraform Infrastructure
```bash
cd terraform/
cp terraform.tfvars.template terraform.tfvars
# Edit terraform.tfvars with your values
terraform init
terraform plan
terraform apply
```

**Required Configuration:**
- [ ] AWS region set
- [ ] VPC and subnet CIDRs configured
- [ ] EC2 instance type selected
- [ ] RDS instance class configured
- [ ] Database name and username set
- [ ] Key pair name specified
- [ ] Domain name (if using ACM)

### Step 2: AWS Secrets Manager Setup
```bash
# Database password
aws secretsmanager create-secret \
    --name "helpdesk-crm/db-password" \
    --secret-string "your-secure-password"

# JWT secret
aws secretsmanager create-secret \
    --name "helpdesk-crm/jwt-secret" \
    --secret-string "$(openssl rand -base64 32)"

# JumpCloud credentials
aws secretsmanager create-secret \
    --name "helpdesk-crm/jumpcloud-credentials" \
    --secret-string '{
        "client_id": "your-client-id",
        "client_secret": "your-client-secret",
        "api_key": "your-api-key"
    }'
```

**Secrets Checklist:**
- [ ] Database password created
- [ ] JWT signing secret created
- [ ] JumpCloud credentials stored
- [ ] Google Workspace credentials stored (if needed)
- [ ] FreshService API key stored (if needed)

---

## Application Deployment 🚀

### Step 3: EC2 Instance Configuration
```bash
# SSH to EC2 instance
ssh -i ~/.ssh/your-key.pem ec2-user@your-instance-ip

# Clone repository
sudo mkdir -p /opt/helpdesk-crm
sudo chown ec2-user:ec2-user /opt/helpdesk-crm
git clone https://github.com/c-a-r-r/helpdesk.git /opt/helpdesk-crm
cd /opt/helpdesk-crm

# Run deployment script
./deployment/deploy.sh
```

**Deployment Steps:**
- [ ] Repository cloned to EC2
- [ ] Docker and Docker Compose installed
- [ ] Environment variables configured
- [ ] Containers built and started
- [ ] Health checks passing

### Step 4: Environment Configuration
Edit `/opt/helpdesk-crm/.env` with:
- [ ] Database connection (RDS endpoint)
- [ ] AWS region and secrets configuration
- [ ] Domain name and CORS origins
- [ ] JumpCloud issuer URL
- [ ] API base URL with HTTPS

### Step 5: SSL and Domain Setup
- [ ] DNS A record pointing to ALB
- [ ] SSL certificate installed/configured
- [ ] HTTPS redirect enabled in nginx
- [ ] Security headers configured

---

## Security Configuration 🔒

### SSL/TLS Configuration
- [ ] TLS 1.2+ enabled
- [ ] Strong cipher suites configured
- [ ] HSTS headers enabled
- [ ] Certificate auto-renewal set up

### Application Security
- [ ] CORS origins restricted to domain
- [ ] Rate limiting enabled
- [ ] Security headers configured
- [ ] Debug mode disabled in production
- [ ] Error logging configured (no sensitive data)

### Network Security
- [ ] Security groups configured (ALB → EC2 → RDS)
- [ ] Database in private subnet
- [ ] No direct internet access to EC2 (ALB only)
- [ ] VPC flow logs enabled

### Access Control
- [ ] IAM roles follow least privilege
- [ ] EC2 instances use instance profiles
- [ ] SSH access restricted to management IPs
- [ ] Database access from application only

---

## Monitoring and Alerting 📊

### CloudWatch Configuration
- [ ] Application logs streaming to CloudWatch
- [ ] Custom metrics for application health
- [ ] Dashboard created for key metrics
- [ ] Alerts configured for:
  - High CPU/Memory usage
  - Application errors
  - Database connection issues
  - SSL certificate expiry

### Health Monitoring
```bash
# Set up health check monitoring
chmod +x /opt/helpdesk-crm/scripts/health-check.sh

# Add to crontab for regular checks
echo "*/5 * * * * /opt/helpdesk-crm/scripts/health-check.sh" | crontab -
```

- [ ] Health check script configured
- [ ] Automated monitoring scheduled
- [ ] Email alerts configured
- [ ] Log aggregation working

---

## Backup and Recovery 💾

### Database Backups
- [ ] RDS automated backups enabled (7+ days)
- [ ] RDS snapshots scheduled
- [ ] Cross-region backup replication (optional)

### Application Backups
```bash
# Configure application backup
chmod +x /opt/helpdesk-crm/backup/backup.sh

# Schedule daily backups
echo "0 2 * * * /opt/helpdesk-crm/backup/backup.sh" | crontab -
```

- [ ] Application backup script configured
- [ ] S3 bucket for backups (optional)
- [ ] Backup retention policy set
- [ ] Backup restoration tested

---

## Performance Optimization ⚡

### Database Optimization
- [ ] RDS parameter group optimized
- [ ] Connection pooling configured
- [ ] Performance Insights enabled
- [ ] Slow query logging enabled

### Application Performance
- [ ] Uvicorn workers configured (CPU cores × 2)
- [ ] Nginx caching enabled for static assets
- [ ] Gzip compression enabled
- [ ] CDN configured (optional)

### Auto Scaling
- [ ] Auto Scaling Group configured
- [ ] CloudWatch alarms for scaling
- [ ] Load balancer health checks
- [ ] Instance refresh strategy defined

---

## Final Verification ✅

### Functional Testing
- [ ] Application accessible via domain
- [ ] JumpCloud OAuth login working
- [ ] User onboarding flow complete
- [ ] User offboarding flow complete
- [ ] API endpoints responding correctly
- [ ] Database operations working

### Security Testing
- [ ] SSL Labs test passed (A+ rating)
- [ ] Security headers verified
- [ ] OWASP security scan (basic)
- [ ] Vulnerability assessment complete

### Performance Testing
- [ ] Load testing completed
- [ ] Response times acceptable (< 2s)
- [ ] Database performance verified
- [ ] Resource utilization normal

### Disaster Recovery
- [ ] Backup restoration tested
- [ ] RDS failover tested
- [ ] Multi-AZ deployment verified
- [ ] Recovery procedures documented

---

## Post-Deployment Tasks 📋

### Documentation
- [ ] Architecture diagram updated
- [ ] Runbook created for operations team
- [ ] Troubleshooting guide documented
- [ ] API documentation published

### Team Training
- [ ] Operations team trained on deployment
- [ ] Monitoring procedures documented
- [ ] Incident response plan created
- [ ] Backup/restore procedures tested

### Ongoing Maintenance
- [ ] Security patch schedule defined
- [ ] Dependency update schedule created
- [ ] Certificate renewal automation
- [ ] Cost optimization review scheduled

---

## Emergency Contacts and Resources 📞

### Key Resources
- **Application URL**: https://your-domain.com
- **API Documentation**: https://your-domain.com/api/v1/docs
- **Health Check**: https://your-domain.com/health
- **AWS Console**: [Direct link to your resources]
- **Repository**: https://github.com/c-a-r-r/helpdesk

### Scripts and Commands
```bash
# Check application status
/opt/helpdesk-crm/scripts/health-check.sh

# View application logs
docker-compose -f /opt/helpdesk-crm/docker-compose.prod.yml logs -f

# Restart application
sudo systemctl restart helpdesk-crm

# Manual backup
/opt/helpdesk-crm/backup/backup.sh

# System monitoring
/opt/helpdesk-crm/scripts/health-check.sh monitor
```

---

## Success Criteria 🎯

Your deployment is successful when:
- [ ] Application loads without errors
- [ ] Users can authenticate via JumpCloud
- [ ] Onboarding creates users in target systems
- [ ] Offboarding removes users properly
- [ ] All health checks pass
- [ ] Monitoring is operational
- [ ] Backups are running
- [ ] SSL certificate is valid
- [ ] Performance meets requirements

**🎉 Congratulations! Your Helpdesk CRM is now production-ready!**
