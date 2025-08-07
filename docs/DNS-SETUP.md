# DNS Configuration for helpdesk.amer.biz

## Overview

To deploy your Helpdesk CRM to production, you need to configure DNS records for `helpdesk.amer.biz`.

## Required DNS Records

### 1. SSL Certificate Validation (First Time Only)

When you run the SSL setup script (`scripts/setup-ssl.sh`), AWS will provide a CNAME record for domain validation. You'll need to add this to your `amer.biz` DNS settings.

**Example validation record:**
```
Type: CNAME
Name: _abc123def456.helpdesk.amer.biz
Value: _xyz789abc123.acm-validations.aws.
```

**Important**: Remove the domain part from the Name when adding to your DNS provider. So if AWS gives you `_abc123def456.helpdesk.amer.biz`, just use `_abc123def456.helpdesk` as the record name.

### 2. Application Traffic (After Deployment)

After your Terraform deployment completes, you'll get a load balancer DNS name. Create a CNAME record pointing to it:

```
Type: CNAME
Name: helpdesk
Value: helpdesk-crm-alb-1234567890.us-west-2.elb.amazonaws.com
```

## DNS Setup Steps

### Step 1: SSL Certificate Validation

1. Run the SSL setup script:
   ```bash
   cd /path/to/helpdesk-crm
   ./scripts/setup-ssl.sh
   ```

2. Add the validation CNAME record to your DNS provider
3. Wait for validation (can take 5-30 minutes)

### Step 2: Deploy Infrastructure

1. Update `terraform/terraform.tfvars` with the certificate ARN
2. Deploy with Terraform:
   ```bash
   cd terraform
   terraform apply
   ```

### Step 3: Point Domain to Load Balancer

1. Get the load balancer DNS name:
   ```bash
   terraform output load_balancer_dns_name
   ```

2. Add CNAME record to your DNS:
   ```
   Type: CNAME
   Name: helpdesk
   Value: <load-balancer-dns-name>
   TTL: 300 (5 minutes)
   ```

## DNS Provider Examples

### Cloudflare
1. Log into Cloudflare dashboard
2. Select `amer.biz` domain
3. Go to DNS > Records
4. Add CNAME record

### AWS Route 53
```bash
# If amer.biz is hosted in Route 53
aws route53 change-resource-record-sets \
  --hosted-zone-id Z1234567890ABC \
  --change-batch file://dns-change.json
```

### GoDaddy
1. Log into GoDaddy
2. Go to DNS Management for amer.biz
3. Add CNAME record

### Namecheap
1. Log into Namecheap
2. Domain List > Manage for amer.biz
3. Advanced DNS > Add New Record

## Verification

After DNS changes propagate (5-60 minutes):

1. **Test DNS resolution**:
   ```bash
   nslookup helpdesk.amer.biz
   dig helpdesk.amer.biz
   ```

2. **Test SSL certificate**:
   ```bash
   curl -I https://helpdesk.amer.biz
   openssl s_client -connect helpdesk.amer.biz:443 -servername helpdesk.amer.biz
   ```

3. **Test application**:
   ```bash
   curl https://helpdesk.amer.biz/health
   ```

## Troubleshooting

### DNS Not Resolving
- Check TTL settings (lower values propagate faster)
- Use different DNS checker tools online
- Wait longer (DNS can take up to 48 hours in rare cases)

### SSL Certificate Issues
- Verify validation record is correct
- Check certificate status in AWS Console
- Ensure CNAME validation record is still present

### Application Not Loading
- Check load balancer health checks in AWS Console
- Verify security group rules allow traffic
- Check CloudWatch logs for errors

## Security Notes

- Always use HTTPS in production
- Consider enabling Cloudflare proxy for additional protection
- Set appropriate TTL values for DNS records
- Monitor certificate expiration (AWS ACM auto-renews)
