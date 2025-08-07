#!/bin/bash

# SSL Certificate Setup Script for helpdesk.amer.biz
# Run this script to request and configure SSL certificate

set -e

DOMAIN="helpdesk.amer.biz"
REGION="us-west-2"

echo "🔐 Setting up SSL certificate for $DOMAIN"

# Step 1: Request SSL certificate
echo "📜 Requesting SSL certificate..."
CERT_ARN=$(aws acm request-certificate \
    --domain-name $DOMAIN \
    --validation-method DNS \
    --region $REGION \
    --query 'CertificateArn' \
    --output text)

echo "✅ Certificate requested: $CERT_ARN"

# Step 2: Get validation records
echo "🔍 Getting DNS validation records..."
aws acm describe-certificate \
    --certificate-arn $CERT_ARN \
    --region $REGION \
    --query 'Certificate.DomainValidationOptions[0].[ValidationDomain,ResourceRecord.Name,ResourceRecord.Value]' \
    --output table

echo ""
echo "📋 DNS Configuration Required:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "You need to add the DNS validation record shown above"
echo "to your DNS provider (amer.biz domain settings)."
echo ""
echo "Record Type: CNAME"
echo "Record Name: (see Name column above - remove the domain part)"
echo "Record Value: (see Value column above)"
echo ""
echo "After adding the DNS record, run:"
echo "aws acm wait certificate-validated --certificate-arn $CERT_ARN --region $REGION"
echo ""
echo "Then update your terraform.tfvars file:"
echo "certificate_arn = \"$CERT_ARN\""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Save certificate ARN for later use
echo $CERT_ARN > .certificate_arn
echo "💾 Certificate ARN saved to .certificate_arn file"
