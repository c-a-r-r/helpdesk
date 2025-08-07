# 🚀 Helpdesk CRM - Enterprise User Management Platform

[![Production Ready](https://img.shields.io/badge/Production-Ready-green.svg)](https://github.com/c-a-r-r/helpdesk)
[![AWS](https://img.shields.io/badge/AWS-Infrastructure-orange.svg)](https://aws.amazon.com/)
[![Docker](https://img.shields.io/badge/Docker-Containerized-blue.svg)](https://www.docker.com/)

A complete enterprise-grade user onboarding and offboarding management system with automated provisioning across multiple platforms including JumpCloud, Google Workspace, Automox, and FreshService.

## 🏗️ Production Architecture

### **Infrastructure Components**
- **Compute**: AWS EC2 Auto Scaling Group (t3.medium instances)
- **Database**: AWS RDS MariaDB 10.11 with encryption and automated backups
- **Load Balancer**: Application Load Balancer with SSL termination
- **Networking**: VPC with public/private subnets across multiple AZs
- **Security**: AWS Secrets Manager + IAM roles with least privilege
- **Monitoring**: CloudWatch with custom metrics, logs, and alerting
- **Storage**: EBS encrypted volumes with automatic backups

### **Application Stack**
- **Frontend**: Vue 3 + Vite (Production build) → Nginx
- **Backend**: FastAPI + SQLAlchemy + Uvicorn (Multiple workers)
- **Database**: MariaDB 10.11 with connection pooling
- **Authentication**: JumpCloud OAuth 2.0 with role-based access
- **API Gateway**: Nginx reverse proxy with rate limiting
- **Container Orchestration**: Docker Compose with health checks

---

## 📋 Production Deployment Guide

### **Prerequisites**

#### 1. AWS Account Setup
```bash
# Install AWS CLI
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

# Configure AWS credentials
aws configure
```

#### 2. Required AWS Permissions
Your AWS user/role needs these permissions:
- EC2 (instances, security groups, load balancers)
- RDS (database creation and management)
- VPC (networking components)
- IAM (roles and policies)
- Secrets Manager (storing credentials)
- CloudWatch (monitoring and logging)
- Certificate Manager (SSL certificates)

#### 3. Domain and SSL Certificate
- Domain name pointed to your AWS region
- SSL certificate in AWS Certificate Manager

---

## 🚀 Step-by-Step Deployment

### **Step 1: Infrastructure Deployment with Terraform**

#### 1.1 Clone Repository
```bash
git clone https://github.com/c-a-r-r/helpdesk.git
cd helpdesk/terraform
```

#### 1.2 Configure Terraform Variables
```bash
# Copy template and customize
cp terraform.tfvars.template terraform.tfvars

# Edit configuration
nano terraform.tfvars
```

**Required Configuration:**
```hcl
# terraform.tfvars
aws_region          = "us-west-2"
environment         = "prod"
project_name        = "helpdesk-crm"

# Networking
vpc_cidr               = "10.0.0.0/16"
public_subnet_cidrs    = ["10.0.1.0/24", "10.0.2.0/24"]
private_subnet_cidrs   = ["10.0.10.0/24", "10.0.20.0/24"]

# EC2 Configuration
instance_type      = "t3.medium"
key_pair_name      = "your-ec2-keypair"
min_size          = 1
max_size          = 3
desired_capacity  = 2

# Database Configuration
db_instance_class = "db.t3.micro"  # Adjust based on needs
db_name          = "helpdesk_crm"
db_username      = "admin"
db_password      = "secure-random-password-here"

# Security
allowed_cidr_blocks = ["0.0.0.0/0"]  # Restrict in production

# Optional: SSL Certificate
domain_name      = "helpdesk.yourdomain.com"
certificate_arn  = "arn:aws:acm:region:account:certificate/cert-id"
```

#### 1.3 Deploy Infrastructure
```bash
# Initialize Terraform
terraform init

# Review deployment plan
terraform plan

# Deploy infrastructure
terraform apply

# Note the outputs (ALB DNS name, RDS endpoint, etc.)
terraform output
```

### **Step 2: Configure Application Secrets**

#### 2.1 Create AWS Secrets
```bash
# Navigate to project root
cd ..

# Create secrets in AWS Secrets Manager
aws secretsmanager create-secret \
    --name "helpdesk-crm/db-password" \
    --description "Database password" \
    --secret-string "your-secure-db-password"

aws secretsmanager create-secret \
    --name "helpdesk-crm/jwt-secret" \
    --description "JWT signing secret" \
    --secret-string "$(openssl rand -base64 32)"

# JumpCloud credentials
aws secretsmanager create-secret \
    --name "helpdesk-crm/jumpcloud-credentials" \
    --description "JumpCloud OAuth credentials" \
    --secret-string '{
        "client_id": "your-jumpcloud-client-id",
        "client_secret": "your-jumpcloud-client-secret",
        "api_key": "your-jumpcloud-api-key"
    }'

# Google Workspace credentials (if using)
aws secretsmanager create-secret \
    --name "helpdesk-crm/google-credentials" \
    --description "Google Workspace service account" \
    --secret-string "$(cat path/to/google-service-account.json)"

# FreshService API key (if using)
aws secretsmanager create-secret \
    --name "helpdesk-crm/freshservice-api-key" \
    --description "FreshService API key" \
    --secret-string "your-freshservice-api-key"
```

#### 2.2 JumpCloud Application Setup
1. **Login to JumpCloud Admin Console**
2. **Create OAuth Application:**
   - Go to SSO Applications → Add Application
   - Choose "Custom OIDC App"
   - Configuration:
     ```
     Display Label: Helpdesk CRM
     SSO URL: https://your-domain.com/api/v1/auth/callback
     Audience: your-jumpcloud-client-id
     Login URL: https://your-domain.com/auth/login
     ```
3. **Note the Client ID and Client Secret** for AWS Secrets Manager

### **Step 3: Application Deployment**

#### 3.1 SSH to EC2 Instance
```bash
# Get instance IP from Terraform output
INSTANCE_IP=$(terraform output -raw alb_dns_name)

# SSH to instance (via bastion or direct if configured)
ssh -i ~/.ssh/your-key.pem ec2-user@$INSTANCE_IP
```

#### 3.2 Deploy Application Code
```bash
# On EC2 instance
sudo su - ec2-user
cd /opt

# Clone application code
git clone https://github.com/c-a-r-r/helpdesk.git helpdesk-crm
cd helpdesk-crm

# Make deployment script executable
chmod +x deployment/deploy.sh

# Run deployment
./deployment/deploy.sh
```

#### 3.3 Configure Environment Variables
The deployment script will prompt you to configure the environment file:
```bash
# Edit production environment file
nano .env

# Required configuration:
ENVIRONMENT=production
DEBUG=false

# Database (from Terraform outputs)
DB_HOST=your-rds-endpoint.region.rds.amazonaws.com
DB_PORT=3306
DB_NAME=helpdesk_crm
DB_USER=admin
DB_PASSWORD_SECRET_NAME=helpdesk-crm/db-password

# AWS Configuration
AWS_REGION=us-west-2
AWS_DEFAULT_REGION=us-west-2

# Secrets Manager
SECRETS_MANAGER_ENABLED=true
JUMPCLOUD_CREDENTIALS_SECRET_NAME=helpdesk-crm/jumpcloud-credentials
GOOGLE_CREDENTIALS_SECRET_NAME=helpdesk-crm/google-credentials
FRESHSERVICE_API_KEY_SECRET_NAME=helpdesk-crm/freshservice-api-key
JWT_SECRET_SECRET_NAME=helpdesk-crm/jwt-secret

# Application URLs (replace with your domain)
CORS_ORIGINS=https://your-domain.com,https://www.your-domain.com
REDIRECT_URI=https://your-domain.com/api/v1/auth/callback
API_BASE_URL=https://your-domain.com/api/v1

# JumpCloud Configuration
JUMPCLOUD_ISSUER=https://your-org.jumpcloud.com
```

### **Step 4: SSL Configuration**

#### 4.1 Update Nginx for HTTPS
```bash
# Edit nginx configuration for SSL
sudo nano /opt/helpdesk-crm/nginx/nginx.conf

# Update server_name to your domain
# Uncomment HTTPS configuration
# Add SSL certificate paths
```

#### 4.2 Domain DNS Configuration
Point your domain to the ALB DNS name:
```bash
# Get ALB DNS name
aws elbv2 describe-load-balancers \
    --names helpdesk-crm-alb \
    --query 'LoadBalancers[0].DNSName' \
    --output text
```

Create CNAME record:
```
helpdesk.yourdomain.com → helpdesk-crm-alb-xxxxxxxxx.us-west-2.elb.amazonaws.com
```

### **Step 5: Health Checks and Monitoring**

#### 5.1 Verify Deployment
```bash
# Check container status
docker-compose ps

# View application logs
docker-compose logs -f

# Test health endpoints
curl http://localhost/health
curl http://localhost/api/v1/health
```

#### 5.2 Configure CloudWatch Monitoring
```bash
# CloudWatch agent is already configured via user-data script
# Verify it's running
sudo systemctl status amazon-cloudwatch-agent

# View logs in CloudWatch
aws logs describe-log-groups --query 'logGroups[?contains(logGroupName,`helpdesk`)]'
```

#### 5.3 Set Up Alerting
```bash
# Create CloudWatch alarms for critical metrics
aws cloudwatch put-metric-alarm \
    --alarm-name "helpdesk-crm-high-cpu" \
    --alarm-description "High CPU utilization" \
    --metric-name CPUUtilization \
    --namespace AWS/EC2 \
    --statistic Average \
    --period 300 \
    --threshold 80 \
    --comparison-operator GreaterThanThreshold \
    --evaluation-periods 2
```

---

## 🔧 Production Configuration

### **Database Configuration**
```sql
-- Connect to RDS and create optimized settings
-- (These are already configured in Terraform)

-- Verify configuration
SHOW VARIABLES LIKE 'innodb_buffer_pool_size';
SHOW VARIABLES LIKE 'max_connections';
SHOW GLOBAL STATUS LIKE 'Connections';
```

### **Performance Optimization**

#### Backend Configuration
```python
# backend/main.py - Production settings
import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        workers=4,  # Adjust based on CPU cores
        access_log=False,  # Use nginx for access logging
        reload=False
    )
```

#### Frontend Build Optimization
```javascript
// vue-app/vite.config.js - Production build
export default {
  build: {
    minify: 'terser',
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['vue', 'vue-router'],
          auth: ['./src/composables/useAuth.js']
        }
      }
    }
  }
}
```

### **Security Hardening**

#### 1. Network Security
```bash
# Security groups are configured in Terraform
# ALB: Only 80, 443 from internet
# EC2: Only ALB security group access
# RDS: Only EC2 security group access
```

#### 2. Application Security
```python
# CORS configuration
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)
```

#### 3. Rate Limiting (Nginx)
```nginx
# nginx/nginx.conf
http {
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    limit_req_zone $binary_remote_addr zone=auth:10m rate=5r/s;
    
    server {
        location /api/ {
            limit_req zone=api burst=20 nodelay;
        }
        
        location /api/v1/auth/ {
            limit_req zone=auth burst=10 nodelay;
        }
    }
}
```

---

## 📊 Monitoring and Maintenance

### **Health Monitoring**
```bash
# Application health check script
#!/bin/bash
# /opt/helpdesk-crm/scripts/health-check.sh

# Check application health
APP_HEALTH=$(curl -s -o /dev/null -w "%{http_code}" http://localhost/health)
API_HEALTH=$(curl -s -o /dev/null -w "%{http_code}" http://localhost/api/v1/health)

if [[ $APP_HEALTH != "200" ]] || [[ $API_HEALTH != "200" ]]; then
    echo "Health check failed - restarting services"
    cd /opt/helpdesk-crm
    docker-compose restart
fi
```

### **Automated Backups**
```bash
# Database backup script (already included)
# /opt/helpdesk-crm/backup/backup.sh

# Set up daily backups
crontab -e
# Add: 0 2 * * * /opt/helpdesk-crm/backup/backup.sh
```

### **Log Management**
```bash
# Application logs location
/opt/helpdesk-crm/logs/
├── backend.log
├── frontend.log
├── nginx.log
└── deployment.log

# CloudWatch log groups
/aws/ec2/helpdesk-crm/system
/aws/ec2/helpdesk-crm/application
/aws/rds/instance/helpdesk-crm-db/error
```

---

## 🚨 Troubleshooting

### **Common Issues**

#### 1. Application Won't Start
```bash
# Check container status
docker-compose ps

# View logs
docker-compose logs backend
docker-compose logs frontend
docker-compose logs nginx

# Check environment variables
docker-compose exec backend env | grep -E "(DB_|AWS_|SECRET)"
```

#### 2. Database Connection Issues
```bash
# Test database connectivity
docker-compose exec backend python -c "
from database import engine
try:
    with engine.connect() as conn:
        print('Database connection successful')
except Exception as e:
    print(f'Database connection failed: {e}')
"
```

#### 3. OAuth Authentication Issues
```bash
# Check JumpCloud configuration
curl -H "x-api-key: $JUMPCLOUD_API_KEY" \
     https://console.jumpcloud.com/api/organizations

# Verify redirect URI matches JumpCloud app settings
# Check CORS origins include your domain
```

#### 4. AWS Secrets Manager Issues
```bash
# Test secret retrieval
aws secretsmanager get-secret-value \
    --secret-id helpdesk-crm/jumpcloud-credentials \
    --query SecretString \
    --output text

# Check IAM permissions
aws sts get-caller-identity
aws iam get-role --role-name helpdesk-crm-ec2-role
```

### **Performance Tuning**
```bash
# Monitor resource usage
docker stats

# Database performance
docker-compose exec mysql mysql -u admin -p -e "SHOW PROCESSLIST;"

# Nginx access logs
tail -f /var/log/nginx/access.log
```

---

## 🔄 Updates and Maintenance

### **Application Updates**
```bash
# Update application code
cd /opt/helpdesk-crm
git pull origin main

# Rebuild and restart
docker-compose build --no-cache
docker-compose up -d

# Verify health
./scripts/health-check.sh
```

### **Infrastructure Updates**
```bash
# Update Terraform infrastructure
cd terraform
terraform plan
terraform apply

# Update EC2 instances (rolling update via ASG)
aws autoscaling start-instance-refresh \
    --auto-scaling-group-name helpdesk-crm-asg
```

### **Database Maintenance**
```bash
# Connect to RDS
mysql -h your-rds-endpoint.region.rds.amazonaws.com \
      -u admin -p helpdesk_crm

# Run maintenance queries
OPTIMIZE TABLE users;
ANALYZE TABLE onboarding_requests;
```

---

## 📈 Scaling Considerations

### **Horizontal Scaling**
- Auto Scaling Group automatically scales based on CPU/memory
- Application Load Balancer distributes traffic
- RDS can be scaled vertically or with read replicas

### **Vertical Scaling**
```bash
# Update instance type in Terraform
instance_type = "t3.large"  # or m5.large for more memory

# Apply changes
terraform apply
```

### **Database Scaling**
```bash
# Scale RDS instance
aws rds modify-db-instance \
    --db-instance-identifier helpdesk-crm-db \
    --db-instance-class db.t3.small \
    --apply-immediately
```

---

## 🔐 Security Best Practices

### **Regular Security Tasks**
1. **Rotate Secrets** (every 90 days)
2. **Update Dependencies** (monthly)
3. **Review IAM Permissions** (quarterly)
4. **Security Scanning** (automated via CI/CD)
5. **Audit Logs Review** (weekly)

### **Compliance Monitoring**
```bash
# AWS Config rules for compliance
aws configservice describe-compliance-by-config-rule

# Security Hub findings
aws securityhub get-findings
```

---

## 📚 Additional Resources

- **[API Documentation](https://your-domain.com/api/v1/docs)** - Interactive API documentation
- **[JumpCloud Integration Guide](./docs/JUMPCLOUD-SETUP.md)** - Detailed JumpCloud setup
- **[AWS Architecture Diagram](./docs/ARCHITECTURE.md)** - Infrastructure overview
- **[Monitoring Runbook](./docs/MONITORING.md)** - Operations guide

---

## 🎯 Production Checklist

### **Pre-Launch**
- [ ] Infrastructure deployed via Terraform
- [ ] SSL certificate configured
- [ ] Domain DNS configured
- [ ] All secrets stored in AWS Secrets Manager
- [ ] JumpCloud OAuth application configured
- [ ] Database migrations completed
- [ ] Health checks passing
- [ ] Monitoring and alerting configured
- [ ] Backup strategy implemented

### **Post-Launch**
- [ ] Performance monitoring enabled
- [ ] Log aggregation working
- [ ] Backup verification completed
- [ ] Security scanning scheduled
- [ ] Documentation updated
- [ ] Team training completed

---

## 📞 Support

For deployment support and troubleshooting:
1. Check application logs: `docker-compose logs -f`
2. Review CloudWatch metrics and alarms
3. Verify AWS resource status in console
4. Test health endpoints: `/health` and `/api/v1/health`

**Your Helpdesk CRM is now production-ready! 🚀**
