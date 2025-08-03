# Helpdesk CRM - AWS Secrets Manager Configuration

This application uses AWS Secrets Manager for all environments (dev, staging, prod) to ensure secure credential management.

## Quick Start

### 1. Configure AWS Credentials
```bash
aws configure
# or set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY
```

### 2. Create Secret Template (First Time Only)
```bash
./create-secret-template.sh dev
```

### 3. Update Secret with Real Values
Use AWS Console or CLI to update the secret with your actual credentials:

```bash
aws secretsmanager update-secret \
  --secret-id "helpdesk-crm/dev/config" \
  --secret-string '{
    "jumpcloud_client_id": "your-real-client-id",
    "jumpcloud_client_secret": "your-real-client-secret",
    "jumpcloud_issuer": "https://oauth.id.jumpcloud.com/",
    "jumpcloud_api_key": "your-real-api-key",
    "freshdesk_api_key": "your-freshservice-api-key",
    "freshdesk_domain": "your-company.freshservice.com",
    "database_url": "sqlite:///./helpdesk.db",
    "cors_origins": "http://localhost:3000,http://localhost:5173",
    "redirect_uri": "http://localhost:8000/callback"
  }'
```

### 4. Start Application
```bash
./start-backend.sh dev    # for development
./start-backend.sh prod   # for production
```

## Available Scripts

| Script | Purpose |
|--------|---------|
| `./create-secret-template.sh [env]` | Create secret template (first time only) |
| `./load-secrets.sh [env]` | Validate existing secret configuration |
| `./view-secrets.sh [env]` | View current secret values (redacted) |
| `./start-backend.sh [env] [port]` | Start application with proper environment |

## Environment Behavior

### Development (`dev`)
- Uses AWS Secrets Manager if available
- Falls back to placeholder values if secrets not configured
- Shows warnings about missing OAuth configuration
- Application starts but login will not work without real credentials

### Production/Staging (`prod`, `staging`)
- **Requires** AWS Secrets Manager configuration
- **Fails to start** if secrets are missing or invalid
- No fallback to placeholder values
- Strict validation of all required fields

## Required Secret Structure

The AWS secret must contain these fields:

```json
{
  "jumpcloud_client_id": "your-jumpcloud-oauth-client-id",
  "jumpcloud_client_secret": "your-jumpcloud-oauth-client-secret", 
  "jumpcloud_issuer": "https://oauth.id.jumpcloud.com/",
  "jumpcloud_api_key": "your-jumpcloud-api-key",
  "freshdesk_api_key": "your-freshservice-api-key",
  "freshdesk_domain": "your-company.freshservice.com",
  "database_url": "sqlite:///./helpdesk.db",
  "cors_origins": "http://localhost:3000,http://localhost:5173",
  "redirect_uri": "http://localhost:8000/callback"
}
```

## Secret Names by Environment

- Development: `helpdesk-crm/dev/config`
- Staging: `helpdesk-crm/staging/config`
- Production: `helpdesk-crm/prod/config`

## Troubleshooting

### AWS Credentials Issues
```bash
# Check credentials
aws sts get-caller-identity

# Configure if needed
aws configure
```

### Secret Not Found
```bash
# Create template
./create-secret-template.sh dev

# Then update with real values via AWS Console or CLI
```

### Production Startup Failure
- Ensure AWS credentials are configured
- Verify secret exists and contains all required fields
- Check AWS region configuration

## Security Notes

- **Never commit** `.env` files or credentials to version control
- **Always use** AWS Secrets Manager for all environments
- **Rotate credentials** regularly
- **Use least privilege** IAM policies for Secrets Manager access
