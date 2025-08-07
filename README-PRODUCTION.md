# 🚀 Helpdesk CRM - Enterprise User Management Platform

[![Production Ready](https://img.shields.io/badge/Production-Ready-green.svg)](https://github.com/c-a-r-r/helpdesk)
[![AWS](https://img.shields.io/badge/AWS-Infrastructure-orange.svg)](https://aws.amazon.com/)
[![Docker](https://img.shields.io/badge/Docker-Containerized-blue.svg)](https://www.docker.com/)

A complete enterprise-grade user onboarding and offboarding management system with automated provisioning across multiple platforms including JumpCloud, Google Workspace, Automox, and FreshService.

## 🏗️ Architecture Overview

**Production Infrastructure:**
- **Compute**: AWS EC2 Auto Scaling Group with Application Load Balancer
- **Database**: AWS RDS MariaDB with encryption and automated backups
- **Security**: AWS Secrets Manager + IAM roles with least privilege
- **Monitoring**: CloudWatch with custom metrics, logs, and alerting
- **SSL/TLS**: Certificate Manager with automatic renewal

**Application Stack:**
- **Frontend**: Vue 3 + Vite (Production optimized) → Nginx
- **Backend**: FastAPI + SQLAlchemy + Uvicorn (Multiple workers)
- **Authentication**: JumpCloud OAuth 2.0 with role-based access
- **Container Orchestration**: Docker Compose with health checks

---

## 🚀 Quick Start

### For Production Deployment
**Your application is production-ready!** Follow our comprehensive production guide:

📖 **[Complete Production Deployment Guide](./PRODUCTION-README.md)**
✅ **[Production Deployment Checklist](./PRODUCTION-CHECKLIST.md)**

### For Development

#### Prerequisites
- Docker and Docker Compose
- Git

#### Start Development Environment
```bash
# Clone repository
git clone https://github.com/c-a-r-r/helpdesk.git
cd helpdesk

# Start development environment
docker-compose up -d

# Check system status
./scripts/health-check.sh
```

#### Access Applications
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

---

## 📋 Key Features

### User Management
- **Onboarding**: Multi-user form with automated provisioning
- **Offboarding**: Secure user deactivation across all systems
- **Bulk Operations**: Process multiple users simultaneously
- **Audit Trail**: Complete activity logging and reporting

### Platform Integrations
- **JumpCloud**: User creation, group management, device binding
- **Google Workspace**: Account creation, group assignment, aliases
- **Automox**: Agent management and device removal
- **FreshService**: Ticket integration and status synchronization

### Enterprise Features
- **OAuth Authentication**: JumpCloud SSO with role-based access
- **Security**: AWS Secrets Manager for credential management
- **Monitoring**: Health checks, metrics, and alerting
- **Scalability**: Auto-scaling infrastructure with load balancing
- **Backup**: Automated database and application backups

---

## 🛠️ Development

### Project Structure
```
helpdesk-crm/
├── 📖 PRODUCTION-README.md          # Complete production guide
├── ✅ PRODUCTION-CHECKLIST.md       # Deployment checklist
├── 🐳 docker-compose.yml            # Development
├── 🐳 docker-compose.prod.yml       # Production
├── backend/                         # FastAPI backend
│   ├── 📄 Dockerfile.prod          # Production container
│   ├── 🐍 main.py                  # Application entry
│   ├── 🗄️ models.py                # Database models
│   ├── 🛣️ routes.py                 # API endpoints
│   └── 📜 scripts/                 # Automation scripts
├── vue-app/                        # Vue.js frontend
│   ├── 📄 Dockerfile.prod          # Production container
│   ├── ⚙️ vite.config.js           # Build configuration
│   └── 🎨 src/                     # Application source
├── terraform/                      # Infrastructure as Code
│   ├── 🏗️ main.tf                  # Main configuration
│   ├── 💻 ec2.tf                   # Auto Scaling Group
│   ├── 🗄️ rds.tf                   # Database
│   └── 🌐 alb.tf                   # Load Balancer
├── nginx/                          # Reverse proxy
│   ├── 📄 nginx.conf               # Development
│   └── 📄 nginx.prod.conf          # Production
├── deployment/                     # Deployment automation
│   └── 🚀 deploy.sh                # Production deployment
├── scripts/                        # Operational scripts
│   └── 🏥 health-check.sh          # System monitoring
└── backup/                         # Backup system
    └── 💾 backup.sh                # Automated backups
```

### Local Development Commands
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Restart specific service
docker-compose restart backend

# Run health checks
./scripts/health-check.sh

# Stop all services
docker-compose down
```

---

## 🔧 Configuration

### Environment Variables
The application uses environment-based configuration:

**Development**: Uses `.env` file with local settings
**Production**: Uses AWS Secrets Manager for sensitive data

Key configuration areas:
- Database connection (RDS endpoint)
- JumpCloud OAuth credentials
- Google Workspace service account
- AWS region and credentials
- Application URLs and CORS settings

### JumpCloud Setup
1. Create OAuth application in JumpCloud
2. Configure redirect URI: `https://your-domain.com/api/v1/auth/callback`
3. Store credentials in AWS Secrets Manager
4. Update environment configuration

---

## 📊 Monitoring and Operations

### Health Monitoring
```bash
# Check application health
curl https://your-domain.com/health

# Detailed system status
./scripts/health-check.sh

# Continuous monitoring
./scripts/health-check.sh monitor
```

### Logging
- **Application logs**: CloudWatch Logs
- **Access logs**: Nginx access logs
- **Error tracking**: Structured JSON logging
- **Audit trail**: Database activity logs

### Backup and Recovery
- **Database**: RDS automated backups + manual snapshots
- **Application**: Daily full application backup
- **Configuration**: Infrastructure as Code (Terraform)
- **Recovery**: Documented restoration procedures

---

## 🔒 Security Features

### Authentication & Authorization
- JumpCloud OAuth 2.0 integration
- Role-based access control
- Session management with secure cookies
- API key authentication for integrations

### Data Protection
- Encryption at rest (RDS + EBS)
- Encryption in transit (TLS 1.2+)
- AWS Secrets Manager for credentials
- Network isolation with VPC

### Security Headers
- HSTS (HTTP Strict Transport Security)
- CSP (Content Security Policy)
- X-Frame-Options, X-XSS-Protection
- Rate limiting and DDoS protection

---

## 📚 Documentation

### For Administrators
- **[Production Deployment Guide](./PRODUCTION-README.md)** - Complete setup instructions
- **[Deployment Checklist](./PRODUCTION-CHECKLIST.md)** - Step-by-step verification
- **[API Documentation](https://your-domain.com/api/v1/docs)** - Interactive API docs

### For Developers
- **Development Setup** - Local environment configuration
- **Architecture Overview** - System design and components
- **Contributing Guidelines** - Code standards and practices

### For Operations
- **Monitoring Runbook** - Health checks and alerting
- **Backup Procedures** - Data protection and recovery
- **Troubleshooting Guide** - Common issues and solutions

---

## 🎯 Production Readiness

Your Helpdesk CRM application is **production-ready** with:

✅ **Infrastructure**: Auto-scaling AWS infrastructure with Terraform  
✅ **Security**: End-to-end encryption and secure credential management  
✅ **Monitoring**: Comprehensive health checks and CloudWatch integration  
✅ **Backup**: Automated database and application backups  
✅ **Performance**: Optimized containers with proper resource limits  
✅ **SSL/TLS**: Certificate management and security headers  
✅ **Documentation**: Complete deployment and operational guides  

### Next Steps
1. **Deploy Infrastructure**: Use Terraform to create AWS resources
2. **Configure Secrets**: Store credentials in AWS Secrets Manager
3. **Deploy Application**: Run the automated deployment script
4. **Setup Monitoring**: Configure CloudWatch alerts and dashboards
5. **Go Live**: Point your domain to the load balancer

🚀 **Ready to deploy? Start with the [Production Deployment Guide](./PRODUCTION-README.md)!**
