# Helpdesk CRM

A comprehensive helpdesk and customer relationship management system built with FastAPI (backend) and Vue.js (frontend), featuring JumpCloud OAuth authentication and automated user onboarding/offboarding workflows.

## 🚀 Features

- **JumpCloud OAuth Authentication** - Secure single sign-on integration
- **User Management** - Automated onboarding and offboarding workflows  
- **Freshservice Integration** - Sync with Freshservice for ticket management
- **Automox Integration** - Device management and agent deployment
- **Google Workspace Integration** - User provisioning and management
- **Dashboard** - Real-time monitoring and management interface
- **Secure Production Deployment** - SSL/TLS with Let's Encrypt certificates

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Vue.js        │    │   Nginx          │    │   FastAPI       │
│   Frontend      │◄──►│   Reverse Proxy  │◄──►│   Backend       │
│   (Port 80)     │    │   (Ports 80/443) │    │   (Port 8000)   │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                              │                          │
                              │                          ▼
                              │                   ┌─────────────────┐
                              │                   │   MySQL/MariaDB │
                              │                   │   Database      │
                              │                   └─────────────────┘
                              ▼
                       ┌──────────────────┐
                       │   Let's Encrypt  │
                       │   SSL Certs      │
                       └──────────────────┘
```

## 📋 Prerequisites

### System Requirements
- Ubuntu 20.04+ or similar Linux distribution
- Docker and Docker Compose
- Domain name with DNS configured
- At least 2GB RAM and 20GB storage

### Required Accounts & API Keys
- **JumpCloud** - For OAuth authentication
- **Freshservice** - For ticket management integration  
- **Automox** - For device management
- **Google Workspace** - For user provisioning
- **AWS RDS** - For production database (optional)

## 🛠️ Installation & Deployment

### 1. Server Setup

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Install Certbot for SSL certificates
sudo apt install certbot -y
```

### 2. Clone and Configure

```bash
# Clone the repository
git clone https://github.com/your-username/helpdesk-crm.git
cd helpdesk-crm

# Copy environment template
cp .env.example .env
cp .env.example .env.production
```

### 3. Configure Environment Variables

Edit `.env.production` with your actual values:

```bash
# Application
ENVIRONMENT=production
DEBUG=false

# Database (Use AWS RDS for production)
DB_TYPE=mariadb
DB_HOST=your-rds-endpoint.amazonaws.com
DB_PORT=3306
DB_USER=admin
DB_PASSWORD=your-secure-password
DB_NAME=helpdesk_crm

# JumpCloud OAuth (Required)
JUMPCLOUD_CLIENT_ID=your-jumpcloud-client-id
JUMPCLOUD_CLIENT_SECRET=your-jumpcloud-client-secret
JUMPCLOUD_ISSUER=https://oauth.id.jumpcloud.com/
JUMPCLOUD_API_KEY=your-jumpcloud-api-key

# Frontend URL (Update with your domain)
FRONTEND_URL=https://your-domain.com
CORS_ORIGINS=https://your-domain.com

# External Service API Keys
FRESHDESK_API_KEY=your-freshdesk-api-key
FRESHDESK_DOMAIN=your-domain.freshdesk.com
AUTOMOX_API_KEY_PROD=your-automox-api-key
AUTOMOX_ORG_ID_PROD=your-automox-org-id

# Security
JWT_SECRET_KEY=generate-a-strong-secret-key
```

### 4. Configure JumpCloud OAuth

1. **Create OAuth Application in JumpCloud:**
   - Go to JumpCloud Admin Portal
   - Navigate to SSO → Applications
   - Create Custom OIDC Application
   - Set Redirect URI: `https://your-domain.com/callback`
   - Copy Client ID and Client Secret

2. **Update Environment Variables:**
   ```bash
   JUMPCLOUD_CLIENT_ID=your-client-id-here
   JUMPCLOUD_CLIENT_SECRET=your-client-secret-here
   ```

### 5. SSL Certificate Setup

```bash
# Install Let's Encrypt certificate
sudo certbot certonly --standalone -d your-domain.com

# Create SSL directory for nginx
sudo mkdir -p /home/$(whoami)/helpdesk-crm/nginx/ssl

# Copy certificates
sudo cp /etc/letsencrypt/live/your-domain.com/fullchain.pem /home/$(whoami)/helpdesk-crm/nginx/ssl/
sudo cp /etc/letsencrypt/live/your-domain.com/privkey.pem /home/$(whoami)/helpdesk-crm/nginx/ssl/

# Set proper permissions
sudo chown -R $(whoami):$(whoami) /home/$(whoami)/helpdesk-crm/nginx/ssl
sudo chmod 644 /home/$(whoami)/helpdesk-crm/nginx/ssl/*
```

### 6. Deploy Application

```bash
# Build and start services
docker-compose -f docker-compose.prod.yml up -d

# Verify all containers are running
docker-compose -f docker-compose.prod.yml ps

# Check logs if needed
docker-compose -f docker-compose.prod.yml logs -f
```

### 7. Verify Deployment

1. **Health Check:**
   ```bash
   curl https://your-domain.com/health
   # Should return: healthy
   ```

2. **API Documentation:**
   - Visit: `https://your-domain.com/docs`

3. **Test OAuth Login:**
   - Visit: `https://your-domain.com/api/login`
   - Should redirect to JumpCloud for authentication

## 🔧 Configuration Details

### Nginx Configuration
The nginx configuration includes:
- SSL/TLS termination with Let's Encrypt certificates
- HTTP to HTTPS redirect
- OAuth callback routing: `/callback` → backend
- API routing: `/api/*` → backend  
- Frontend routing: `/*` → Vue.js frontend

### OAuth Flow
1. User clicks login → `/api/login`
2. Redirects to JumpCloud OAuth
3. User authenticates with JumpCloud
4. JumpCloud redirects to `/callback` with authorization code
5. Backend exchanges code for tokens
6. Backend redirects to frontend dashboard with user data

### Database
- Production: AWS RDS MySQL/MariaDB
- Development: Local MySQL container
- Automatic migrations on startup

## 📁 Project Structure

```
helpdesk-crm/
├── backend/                 # FastAPI backend
│   ├── main.py             # Main application & OAuth routes
│   ├── models.py           # Database models
│   ├── routes.py           # API routes
│   ├── auth.py             # Authentication logic
│   ├── scripts/            # Automation scripts
│   └── requirements.txt    # Python dependencies
├── vue-app/                # Vue.js frontend
│   ├── src/
│   ├── Dockerfile.prod     # Production Docker build
│   └── package.json        # Node.js dependencies
├── nginx/                  # Nginx configuration
│   ├── nginx.prod.conf     # Production nginx config
│   └── ssl/                # SSL certificates directory
├── terraform/              # AWS infrastructure (optional)
├── docker-compose.prod.yml # Production deployment
├── .env.production         # Production environment variables
└── README.md              # This file
```

## 🔐 Security Considerations

### SSL/TLS
- **Let's Encrypt certificates** for HTTPS
- **HTTP to HTTPS redirect** enforced
- **Modern TLS configuration** (TLS 1.2/1.3 only)
- **Security headers** (HSTS, CSP, X-Frame-Options)

### Authentication
- **JumpCloud OAuth 2.0** with OIDC
- **State parameter validation** for CSRF protection  
- **Secure JWT tokens** with proper expiration
- **Environment-based secrets** management

### Network Security
- **Reverse proxy** with nginx
- **Internal container networking**
- **No direct database exposure**
- **Firewall-friendly** (only ports 80/443 exposed)

## 🚀 Maintenance

### Certificate Renewal
Let's Encrypt certificates auto-renew, but you may need to restart nginx:

```bash
# Renew certificates
sudo certbot renew

# Copy new certificates
sudo cp /etc/letsencrypt/live/your-domain.com/fullchain.pem /home/$(whoami)/helpdesk-crm/nginx/ssl/
sudo cp /etc/letsencrypt/live/your-domain.com/privkey.pem /home/$(whoami)/helpdesk-crm/nginx/ssl/

# Restart nginx
docker-compose -f docker-compose.prod.yml restart nginx
```

### Application Updates
```bash
# Pull latest changes
git pull origin main

# Rebuild and restart
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml up -d --build
```

### Monitoring
- **Health endpoint:** `https://your-domain.com/health`
- **Container logs:** `docker-compose -f docker-compose.prod.yml logs -f`
- **System logs:** `/var/log/nginx/`, `/var/log/letsencrypt/`

## 🛠️ Development

### Local Development Setup
```bash
# Copy development environment
cp .env.example .env

# Start development services
docker-compose up -d

# Access services
# Frontend: http://localhost:3000
# Backend: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### Making Changes
1. Make code changes
2. Test locally with `docker-compose up -d`
3. Commit changes: `git add . && git commit -m "Description"`
4. Push to repository: `git push origin main`
5. Deploy to production using steps above

## 📚 API Documentation

Once deployed, visit `https://your-domain.com/docs` for interactive API documentation powered by FastAPI's automatic OpenAPI generation.

## 🐛 Troubleshooting

### Common Issues

**OAuth Login Not Working:**
- Verify JumpCloud OAuth application configuration
- Check redirect URI matches exactly: `https://your-domain.com/callback`
- Ensure environment variables are set correctly

**SSL Certificate Issues:**
- Verify certificates are copied to `nginx/ssl/` directory
- Check certificate permissions and ownership
- Ensure domain DNS is pointing to your server

**Database Connection Issues:**
- Verify RDS endpoint and credentials
- Check security group allows connections from EC2
- Ensure database exists and is accessible

**Container Issues:**
```bash
# Check container status
docker-compose -f docker-compose.prod.yml ps

# View logs
docker-compose -f docker-compose.prod.yml logs [service-name]

# Restart specific service
docker-compose -f docker-compose.prod.yml restart [service-name]
```

## 📄 License

This project is proprietary software. All rights reserved.

## 🤝 Support

For support and questions, contact the development team or check the project documentation in the `docs/` directory.
