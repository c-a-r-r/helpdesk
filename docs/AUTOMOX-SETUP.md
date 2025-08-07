# Automox AWS Secrets Manager Configuration

To use the Automox integration, you need to store your Automox credentials in AWS Secrets Manager.

## Create the Secret

```bash
# Create Automox credentials secret
aws secretsmanager create-secret \
  --name "helpdesk-crm/automox-credentials" \
  --description "Automox API credentials for helpdesk CRM" \
  --secret-string '{
    "AUTOMOX_API_KEY_PROD": "your-production-api-key",
    "AUTOMOX_ORG_ID_PROD": "your-production-org-id",
    "AUTOMOX_API_KEY_TEST": "your-test-api-key",
    "AUTOMOX_ORG_ID_TEST": "your-test-org-id"
  }'
```

## Get Your Automox Credentials

1. **Login to Automox Console**: https://console.automox.com/
2. **Go to Settings** → **API Keys**
3. **Create a new API Key** or use existing one
4. **Get Organization ID** from Settings → Organization

## Environment Variables (Alternative)

If you prefer environment variables instead of AWS Secrets Manager, set:

```bash
export AUTOMOX_SECRET_ARN="arn:aws:secretsmanager:us-west-2:YOUR-ACCOUNT:secret:helpdesk-crm/automox-credentials"
```

## Test the Configuration

```bash
# Test the Automox script
cd backend/scripts/automox
python offboard_automox.py TEST-HOSTNAME --dry-run --env TEST
```

## Script Integration

The Automox script is automatically available in the offboarding workflow:

- **Script Type**: `automox`
- **Script Name**: `offboard_automox`
- **Required Parameter**: `hostname`
- **Optional Parameters**: `dry_run`, `environment`

## Usage in Offboarding

The script will be called automatically during user offboarding when a hostname is provided. It will:

1. Search for the device by hostname in Automox
2. Remove the device from Automox management
3. Log the results in the script execution logs
