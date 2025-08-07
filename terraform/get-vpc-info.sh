#!/bin/bash

# Script to help gather existing VPC information for Terraform configuration
# This script will list your VPCs and their subnets to help you configure terraform.tfvars

set -e

echo "🔍 AWS VPC Information Gatherer"
echo "==============================="
echo

# Check if AWS CLI is configured
if ! aws sts get-caller-identity &>/dev/null; then
    echo "❌ AWS CLI is not configured. Please run 'aws configure' first."
    exit 1
fi

# Get current region
REGION=$(aws configure get region 2>/dev/null || echo "us-west-2")
echo "📍 Current AWS Region: $REGION"
echo

# List all VPCs
echo "📋 Available VPCs:"
echo "=================="
aws ec2 describe-vpcs \
    --region "$REGION" \
    --query 'Vpcs[*].[VpcId,CidrBlock,Tags[?Key==`Name`]|[0].Value,State]' \
    --output table

echo
echo "🔹 Select a VPC ID from the list above"
read -p "Enter VPC ID: " VPC_ID

# Validate VPC ID
if ! aws ec2 describe-vpcs --vpc-ids "$VPC_ID" --region "$REGION" &>/dev/null; then
    echo "❌ Invalid VPC ID: $VPC_ID"
    exit 1
fi

echo
echo "📊 VPC Information for: $VPC_ID"
echo "==============================="

# Get VPC details
VPC_INFO=$(aws ec2 describe-vpcs --vpc-ids "$VPC_ID" --region "$REGION" --query 'Vpcs[0]')
VPC_CIDR=$(echo "$VPC_INFO" | jq -r '.CidrBlock')
VPC_NAME=$(echo "$VPC_INFO" | jq -r '.Tags[]? | select(.Key=="Name") | .Value // "N/A"')

echo "VPC Name: $VPC_NAME"
echo "VPC CIDR: $VPC_CIDR"
echo

# Get all subnets in the VPC
echo "🏢 Subnets in VPC:"
echo "=================="
SUBNETS=$(aws ec2 describe-subnets \
    --filters "Name=vpc-id,Values=$VPC_ID" \
    --region "$REGION" \
    --query 'Subnets[*].[SubnetId,CidrBlock,AvailabilityZone,Tags[?Key==`Name`]|[0].Value,MapPublicIpOnLaunch]' \
    --output table)

echo "$SUBNETS"

echo
echo "🔍 Analyzing subnet types..."
echo

# Get public subnets (those with routes to Internet Gateway)
PUBLIC_SUBNETS=()
PRIVATE_SUBNETS=()

# Get all route tables for this VPC
ROUTE_TABLES=$(aws ec2 describe-route-tables \
    --filters "Name=vpc-id,Values=$VPC_ID" \
    --region "$REGION" \
    --query 'RouteTables[*].[RouteTableId,Associations[*].SubnetId,Routes[?GatewayId && starts_with(GatewayId, `igw-`)]]')

# Get subnets associated with route tables that have IGW routes
for subnet in $(aws ec2 describe-subnets --filters "Name=vpc-id,Values=$VPC_ID" --region "$REGION" --query 'Subnets[*].SubnetId' --output text); do
    # Check if subnet has route to IGW (making it public)
    HAS_IGW_ROUTE=$(aws ec2 describe-route-tables \
        --filters "Name=vpc-id,Values=$VPC_ID" "Name=association.subnet-id,Values=$subnet" \
        --region "$REGION" \
        --query 'RouteTables[*].Routes[?GatewayId && starts_with(GatewayId, `igw-`)].GatewayId' \
        --output text 2>/dev/null || echo "")
    
    if [ -n "$HAS_IGW_ROUTE" ]; then
        PUBLIC_SUBNETS+=("$subnet")
    else
        PRIVATE_SUBNETS+=("$subnet")
    fi
done

echo "🌐 Public Subnets (with Internet Gateway route):"
if [ ${#PUBLIC_SUBNETS[@]} -eq 0 ]; then
    echo "   No public subnets found"
else
    for subnet in "${PUBLIC_SUBNETS[@]}"; do
        SUBNET_INFO=$(aws ec2 describe-subnets --subnet-ids "$subnet" --region "$REGION" --query 'Subnets[0].[CidrBlock,AvailabilityZone]' --output text)
        echo "   $subnet ($SUBNET_INFO)"
    done
fi

echo
echo "🔒 Private Subnets (without direct Internet Gateway route):"
if [ ${#PRIVATE_SUBNETS[@]} -eq 0 ]; then
    echo "   No private subnets found"
else
    for subnet in "${PRIVATE_SUBNETS[@]}"; do
        SUBNET_INFO=$(aws ec2 describe-subnets --subnet-ids "$subnet" --region "$REGION" --query 'Subnets[0].[CidrBlock,AvailabilityZone]' --output text)
        echo "   $subnet ($SUBNET_INFO)"
    done
fi

echo
echo "📝 Terraform Configuration:"
echo "============================"
echo
echo "# Add these values to your terraform.tfvars file:"
echo
echo "use_existing_vpc = true"
echo "existing_vpc_id = \"$VPC_ID\""
echo

if [ ${#PUBLIC_SUBNETS[@]} -gt 0 ]; then
    echo -n "existing_public_subnet_ids = ["
    for i in "${!PUBLIC_SUBNETS[@]}"; do
        if [ $i -eq 0 ]; then
            echo -n "\"${PUBLIC_SUBNETS[$i]}\""
        else
            echo -n ", \"${PUBLIC_SUBNETS[$i]}\""
        fi
    done
    echo "]"
else
    echo "# No public subnets found - you may need to create them or check your routing"
    echo "existing_public_subnet_ids = []"
fi

if [ ${#PRIVATE_SUBNETS[@]} -gt 0 ]; then
    echo -n "existing_private_subnet_ids = ["
    for i in "${!PRIVATE_SUBNETS[@]}"; do
        if [ $i -eq 0 ]; then
            echo -n "\"${PRIVATE_SUBNETS[$i]}\""
        else
            echo -n ", \"${PRIVATE_SUBNETS[$i]}\""
        fi
    done
    echo "]"
else
    echo "# No private subnets found - you may need to create them"
    echo "existing_private_subnet_ids = []"
fi

echo
echo "⚠️  Important Notes:"
echo "===================="
echo "1. Ensure you have at least 2 public subnets in different AZs for the ALB"
echo "2. Ensure you have at least 2 private subnets in different AZs for EC2 and RDS"
echo "3. Private subnets should have NAT Gateway routes for internet access"
echo "4. Verify that your VPC has DNS resolution and DNS hostnames enabled"
echo
echo "🔧 To check VPC DNS settings:"
echo "aws ec2 describe-vpc-attribute --vpc-id $VPC_ID --attribute enableDnsSupport"
echo "aws ec2 describe-vpc-attribute --vpc-id $VPC_ID --attribute enableDnsHostnames"
echo
echo "✅ Configuration gathering complete!"
