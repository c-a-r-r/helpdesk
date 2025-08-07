#!/bin/bash

# Update system
yum update -y

# Install Docker
yum install -y docker
systemctl start docker
systemctl enable docker
usermod -a -G docker ec2-user

# Install Docker Compose
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose
ln -s /usr/local/bin/docker-compose /usr/bin/docker-compose

# Install AWS CLI v2
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

# Install git
yum install -y git

# Create application directory
mkdir -p /opt/helpdesk-crm
cd /opt/helpdesk-crm

# Clone the repository (you'll need to replace this with your actual repo)
# For now, we'll create the structure manually
mkdir -p backend vue-app nginx

# Create production environment file
cat > .env.prod << EOF
# Database Configuration
DB_HOST=${db_host}
DB_PORT=3306
DB_NAME=${db_name}
DB_USER=${db_username}

# AWS Configuration
AWS_REGION=${aws_region}
SECRETS_MANAGER_ENABLED=true
GOOGLE_CREDENTIALS_SECRET_NAME=${project_name}/google-credentials
JUMPCLOUD_API_KEY_SECRET_NAME=${project_name}/jumpcloud-api-key
FRESHSERVICE_API_KEY_SECRET_NAME=${project_name}/freshservice-api-key

# Application Configuration
ENVIRONMENT=production
DEBUG=false
CORS_ORIGINS=*

# Security
ALLOWED_HOSTS=*
EOF

# Get database password from AWS Secrets Manager
DB_PASSWORD=$(aws secretsmanager get-secret-value --secret-id ${project_name}/db-password --region ${aws_region} --query SecretString --output text)
echo "DB_PASSWORD=$DB_PASSWORD" >> .env.prod

# Get JWT secret from AWS Secrets Manager
JWT_SECRET=$(aws secretsmanager get-secret-value --secret-id ${project_name}/jwt-secret --region ${aws_region} --query SecretString --output text)
echo "JWT_SECRET_KEY=$JWT_SECRET" >> .env.prod

# Create docker-compose.prod.yml
cat > docker-compose.prod.yml << 'EOF'
version: '3.8'

services:
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile.prod
    env_file:
      - .env.prod
    networks:
      - app-network
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  frontend:
    build:
      context: ./vue-app
      dockerfile: Dockerfile.prod
    networks:
      - app-network
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/conf.d/default.conf:ro
    depends_on:
      - backend
      - frontend
    networks:
      - app-network
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost/health"]
      interval: 30s
      timeout: 10s
      retries: 3

networks:
  app-network:
    driver: bridge
EOF

# Create systemd service for the application
cat > /etc/systemd/system/helpdesk-crm.service << 'EOF'
[Unit]
Description=Helpdesk CRM Application
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/opt/helpdesk-crm
ExecStart=/usr/local/bin/docker-compose -f docker-compose.prod.yml up -d
ExecStop=/usr/local/bin/docker-compose -f docker-compose.prod.yml down
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target
EOF

# Enable and start the service
systemctl daemon-reload
systemctl enable helpdesk-crm.service

# Install CloudWatch agent
wget https://s3.amazonaws.com/amazoncloudwatch-agent/amazon_linux/amd64/latest/amazon-cloudwatch-agent.rpm
rpm -U ./amazon-cloudwatch-agent.rpm

# Configure CloudWatch agent
cat > /opt/aws/amazon-cloudwatch-agent/etc/amazon-cloudwatch-agent.json << EOF
{
    "logs": {
        "logs_collected": {
            "files": {
                "collect_list": [
                    {
                        "file_path": "/var/log/messages",
                        "log_group_name": "/aws/ec2/${project_name}",
                        "log_stream_name": "{instance_id}/system"
                    },
                    {
                        "file_path": "/opt/helpdesk-crm/logs/*.log",
                        "log_group_name": "/aws/ec2/${project_name}",
                        "log_stream_name": "{instance_id}/application"
                    }
                ]
            }
        }
    },
    "metrics": {
        "namespace": "CWAgent",
        "metrics_collected": {
            "disk": {
                "measurement": [
                    "used_percent"
                ],
                "metrics_collection_interval": 60,
                "resources": [
                    "*"
                ]
            },
            "mem": {
                "measurement": [
                    "mem_used_percent"
                ],
                "metrics_collection_interval": 60
            }
        }
    }
}
EOF

# Start CloudWatch agent
/opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl -a fetch-config -m ec2 -c file:/opt/aws/amazon-cloudwatch-agent/etc/amazon-cloudwatch-agent.json -s

# Create log directory
mkdir -p /opt/helpdesk-crm/logs

# Set proper permissions
chown -R ec2-user:ec2-user /opt/helpdesk-crm
chmod +x /opt/helpdesk-crm

# Log completion
echo "User data script completed successfully" > /var/log/user-data.log
