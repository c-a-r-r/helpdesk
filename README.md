# Helpdesk CRM - Enterprise Full Stack Application

A complete user onboarding and offboarding management system built with Vue.js frontend and FastAPI backend, featuring Docker containerization, JumpCloud OAuth authentication, and AWS Secrets Manager integration for enterprise-grade security.

## 🏗️ Architecture

- **Frontend**: Vue 3 + Vite + Nginx (Port 3000)
- **Backend**: FastAPI + SQLAlchemy + SQLite/MariaDB (Port 8000)
- **Database**: SQLite (development) / MariaDB 11.1 (production)
- **Authentication**: JumpCloud OAuth integration
- **Security**: AWS Secrets Manager for credential management
- **Deployment**: Docker containers with health checks

## 🚀 Quick Start

### Development (Local)
```bash
# 1. Start development environment
docker-compose up -d

# 2. Check system status
./check-system-status.sh
```

### Production (AWS Secrets Manager)
```bash
# 1. Setup AWS secrets (one-time)
./setup-aws-secrets.sh

# 2. Deploy with production configuration
docker-compose -f docker-compose.yml -f docker-compose.production.yml up -d

# 3. Verify deployment
./check-system-status.sh
```

### 2. Access Applications
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Debug Config**: http://localhost:8000/debug

### 3. Stop Services
```bash
docker-compose down
```

## 🔐 AWS Secrets Manager Integration

### Setup AWS Credentials
1. **Configure AWS CLI** (if not already done):
   ```bash
   aws configure
   ```

2. **Create IAM Policy** (use provided template):
   ```bash
   # Use the aws-iam-policy.json template
   aws iam create-policy --policy-name HelpDeskCRMSecretsAccess --policy-document file://aws-iam-policy.json
   ```

3. **Setup Secrets** (interactive script):
   ```bash
   ./setup-aws-secrets.sh
   ```

### Available Secret Operations
```bash
# Create/update secrets for environment
./setup-aws-secrets.sh create <environment>

# View existing secrets
./setup-aws-secrets.sh view <environment>

# Test secret retrieval
./setup-aws-secrets.sh test <environment>

# Delete secrets (careful!)
./setup-aws-secrets.sh delete <environment>
```

### Secret Structure
Each environment stores these secrets:
- `client_id` - JumpCloud OAuth client ID
- `client_secret` - JumpCloud OAuth client secret
- `api_key` - FreshDesk API key
- `database_url` - Database connection string
- `secret_key` - Application secret key

## 📁 Project Structure

```
helpdesk-crm/
├── docker-compose.yml              # Development orchestration  
├── docker-compose.production.yml   # Production with MariaDB and AWS
├── check-system-status.sh          # System health checker
├── setup-aws-secrets.sh           # AWS Secrets Manager setup
├── aws-iam-policy.json            # IAM policy template
├── AWS-SECRETS-MANAGER.md         # Detailed AWS setup guide
├── backend/                       # FastAPI backend
│   ├── Dockerfile
│   ├── main.py                   # FastAPI application
│   ├── models.py                 # Database models
│   ├── routes.py                 # API endpoints
│   ├── requirements.txt          # Python dependencies
│   └── init_db.py               # Database initialization
└── vue-app/                      # Vue.js frontend
    ├── Dockerfile
    ├── nginx.conf                # Nginx configuration
    ├── package.json              # Node dependencies
    └── src/
        ├── components/
        └── router/
```

## 🐳 Docker Commands

### Development Environment
```bash
# Build all images
docker-compose build

# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Restart specific service
docker-compose restart backend

# Check system status
./check-system-status.sh
```

### Production Environment
```bash
# Start with MariaDB and AWS Secrets Manager
docker-compose -f docker-compose.yml -f docker-compose.production.yml up -d

# View production logs
docker-compose -f docker-compose.yml -f docker-compose.production.yml logs -f

# Stop production
docker-compose -f docker-compose.yml -f docker-compose.production.yml down
```

## 🔧 Configuration

### Environment Configuration
The system uses environment variables from `.env` file for configuration.

### Local Development Setup
1. Create environment file:
   ```bash
   # Create .env file with your credentials
   ```

2. Configure JumpCloud OAuth:
   ```bash
   # Add to .env
   JUMPCLOUD_CLIENT_ID=your_client_id
   JUMPCLOUD_CLIENT_SECRET=your_client_secret
   JUMPCLOUD_ISSUER=https://your-org.jumpcloud.com
   ```

### Production Setup
1. **AWS Prerequisites**:
   - AWS CLI configured
   - IAM permissions for Secrets Manager
   - Appropriate AWS region set

2. **Deploy Secrets**:
   ```bash
## 📋 Features

- **User Onboarding**: Multi-user form with auto-generation
- **User Offboarding**: Display and manage existing users  
- **Department Management**: OU path configuration
- **Authentication**: JumpCloud OAuth integration
- **Security**: AWS Secrets Manager for credential management
- **Monitoring**: Health checks and system status monitoring
- **Scalability**: Container orchestration with Docker Compose

## 🚀 Production Ready

- **Containerized**: Multi-stage Docker builds with Nginx reverse proxy
- **Secure**: AWS Secrets Manager integration with IAM policies
- **Scalable**: Health checks and persistent storage
- **Observable**: Comprehensive logging and status monitoring
- **Configurable**: Environment-based configuration management
- **Documented**: Complete setup and deployment guides

## 🛠️ Troubleshooting

### Check System Status
```bash
./check-system-status.sh
```

### Common Issues

1. **OAuth "Not Found" Error**:
   - Verify JumpCloud configuration in secrets/environment
   - Check redirect URI matches JumpCloud app settings

2. **AWS Secrets Access Denied**:
   - Verify IAM policy is attached to user/role
   - Check AWS credentials and region

3. **Container Won't Start**:
   - Check logs: `docker-compose logs <service>`
   - Verify environment variables are set

4. **Database Connection Issues**:
   - Ensure database volume has proper permissions
   - Check DATABASE_URL in configuration

### Debug Endpoints
- **Configuration**: `GET /debug` - Shows current config and secret source
- **Health Check**: `GET /health` - Service health status

## 📚 Additional Documentation

- **[MariaDB Configuration Guide](./MARIADB-GUIDE.md)** - Database setup and management
- **[AWS Secrets Manager Setup](./AWS-SECRETS-MANAGER.md)** - Detailed AWS integration guide
- **[API Documentation](http://localhost:8000/docs)** - Interactive API docs (when running)

## 🔒 Security Best Practices

- Secrets stored in AWS Secrets Manager with encryption
- IAM policies follow least-privilege principle
- Environment separation (dev/staging/prod)
- No hardcoded credentials in code or containers
- Audit logging through AWS CloudTrail