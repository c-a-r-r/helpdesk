# Helpdesk CRM - Production Deployment Guide

## Overview

This guide covers deploying the Helpdesk CRM application to AWS using Terraform for infrastructure as code.

## Architecture

- **Frontend**: Vue.js application served via Nginx
- **Backend**: FastAPI application
- **Database**: AWS RDS MariaDB
- **Load Balancer**: Application Load Balancer (ALB)
- **Compute**: EC2 instances with Auto Scaling
- **Networking**: VPC with public/private subnets
- **Security**: Security groups, IAM roles, encrypted storage

## Prerequisites

1. **AWS Account** with appropriate permissions
2. **AWS CLI** configured with credentials
3. **Terraform** >= 1.0 installed
4. **SSH Key Pair** created in AWS for EC2 access
5. **Domain Name** (optional, for SSL)
6. **SSL Certificate** (optional, for HTTPS)

## Deployment Steps

### 1. Clone Repository

```bash
git clone <your-repository-url>
cd helpdesk-crm
```

### 2. Configure Terraform Variables

```bash
cd terraform
cp terraform.tfvars.template terraform.tfvars
```

Edit `terraform.tfvars` with your values:

```hcl
# Required variables
aws_region = "us-west-2"
key_pair_name = "your-aws-key-pair"
db_password = "your-secure-password"

# Optional: Domain and SSL
# domain_name = "your-domain.com"
# certificate_arn = "arn:aws:acm:..."
```

### 3. Create AWS Secrets

Before deploying, create the required secrets in AWS Secrets Manager:

```bash
# Database password
aws secretsmanager create-secret \
  --name "helpdesk-crm/db-password" \
  --description "Database password for helpdesk CRM" \
  --secret-string "your-secure-database-password"

# JWT secret key
aws secretsmanager create-secret \
  --name "helpdesk-crm/jwt-secret" \
  --description "JWT secret key for helpdesk CRM" \
  --secret-string "your-super-secure-jwt-secret-key"

# Google Workspace credentials (JSON)
aws secretsmanager create-secret \
  --name "helpdesk-crm/google-credentials" \
  --description "Google Workspace service account credentials" \
  --secret-string file://path/to/google-credentials.json

# JumpCloud API key
aws secretsmanager create-secret \
  --name "helpdesk-crm/jumpcloud-api-key" \
  --description "JumpCloud API key" \
  --secret-string "your-jumpcloud-api-key"

# Freshservice API key
aws secretsmanager create-secret \
  --name "helpdesk-crm/freshservice-api-key" \
  --description "Freshservice API key" \
  --secret-string "your-freshservice-api-key"
```

### 4. Deploy Infrastructure

```bash
# Initialize Terraform
terraform init

# Plan deployment
terraform plan

# Apply changes
terraform apply
```

### 5. Post-Deployment Setup

After deployment completes:

1. **Update DNS** (if using custom domain):
   ```bash
   # Get the load balancer DNS name
   terraform output load_balancer_dns_name
   
   # Create CNAME record pointing to this DNS name
   ```

2. **Verify Application**:
   ```bash
   # Get application URL
   terraform output application_url
   
   # Test the application
   curl $(terraform output -raw application_url)/health
   ```

3. **Initialize Database**:
   The database will be automatically initialized when the application starts.

### 6. Configure SSL (Optional)

If you have a domain and want HTTPS:

1. **Request SSL Certificate**:
   ```bash
   aws acm request-certificate \
     --domain-name helpdesk.amer.biz \
     --validation-method DNS \
     --region us-west-2
   ```

2. **Update Terraform Variables**:
   ```hcl
   domain_name = "helpdesk.amer.biz"
   certificate_arn = "arn:aws:acm:us-west-2:123456789012:certificate/..."
   ```

3. **Redeploy**:
   ```bash
   terraform apply
   ```

## Monitoring and Maintenance

### CloudWatch Logs

Application logs are automatically sent to CloudWatch:
- `/aws/ec2/helpdesk-crm` - Application and system logs

### Auto Scaling

The application automatically scales based on CPU usage:
- Scale up when CPU > 80% for 4 minutes
- Scale down when CPU < 10% for 4 minutes

### Database Backups

RDS automatically creates:
- Daily backups with 7-day retention
- Point-in-time recovery available

### Security Updates

EC2 instances are configured to auto-update security patches.

## Troubleshooting

### Application Not Starting

1. Check EC2 instance logs:
   ```bash
   # SSH into instance
   ssh -i your-key.pem ec2-user@<instance-ip>
   
   # Check application status
   sudo systemctl status helpdesk-crm
   
   # Check application logs
   sudo journalctl -u helpdesk-crm -f
   ```

2. Check Docker containers:
   ```bash
   cd /opt/helpdesk-crm
   docker-compose -f docker-compose.prod.yml logs
   ```

### Database Connection Issues

1. Verify security group rules
2. Check environment variables in `/opt/helpdesk-crm/.env.prod`
3. Verify secrets in AWS Secrets Manager

### Load Balancer Health Checks Failing

1. Check target group health in AWS Console
2. Verify application is responding on port 80
3. Check `/health` endpoint

## Cleanup

To destroy all resources:

```bash
terraform destroy
```

**Warning**: This will permanently delete all data including the database.

## Security Considerations

1. **Restrict CIDR blocks** in `allowed_cidr_blocks` variable
2. **Use strong passwords** for database and JWT secrets
3. **Enable AWS CloudTrail** for audit logging
4. **Regularly update** EC2 instances and container images
5. **Monitor** CloudWatch logs and metrics
6. **Use SSL** in production with proper certificate

## Support

For issues or questions:
1. Check CloudWatch logs
2. Review Terraform state and outputs
3. Verify AWS permissions and quotas
