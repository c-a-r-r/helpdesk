# Simple EC2 Instance Configuration

# IAM Role for EC2 instance
resource "aws_iam_role" "ec2_role" {
  name = "${var.project_name}-ec2-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ec2.amazonaws.com"
        }
      }
    ]
  })

  tags = {
    Name = "${var.project_name}-ec2-role"
  }
}

# IAM Policy for accessing AWS Secrets Manager
resource "aws_iam_policy" "secrets_manager_policy" {
  name        = "${var.project_name}-secrets-manager-policy"
  description = "Policy for accessing AWS Secrets Manager"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "secretsmanager:GetSecretValue",
          "secretsmanager:DescribeSecret"
        ]
        Resource = "arn:aws:secretsmanager:${var.aws_region}:*:secret:${var.project_name}/*"
      }
    ]
  })
}

# Attach custom policy to role
resource "aws_iam_role_policy_attachment" "secrets_manager_attachment" {
  policy_arn = aws_iam_policy.secrets_manager_policy.arn
  role       = aws_iam_role.ec2_role.name
}

# Attach AWS managed policies
resource "aws_iam_role_policy_attachment" "ssm_managed_instance" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
  role       = aws_iam_role.ec2_role.name
}

resource "aws_iam_role_policy_attachment" "cloudwatch_agent" {
  policy_arn = "arn:aws:iam::aws:policy/CloudWatchAgentServerPolicy"
  role       = aws_iam_role.ec2_role.name
}

# Instance Profile
resource "aws_iam_instance_profile" "ec2_profile" {
  name = "${var.project_name}-ec2-profile"
  role = aws_iam_role.ec2_role.name
}

# User Data Script
locals {
  user_data = base64encode(templatefile("${path.module}/user-data.sh", {
    db_host     = aws_db_instance.main.endpoint
    db_name     = var.db_name
    db_username = var.db_username
    project_name = var.project_name
    aws_region  = var.aws_region
  }))
}

# EC2 Instance
resource "aws_instance" "main" {
  ami                    = data.aws_ami.amazon_linux.id
  instance_type          = var.instance_type
  key_name              = var.key_pair_name
  vpc_security_group_ids = [aws_security_group.ec2.id]
  subnet_id             = var.use_existing_vpc ? var.existing_public_subnet_ids[0] : aws_subnet.public[0].id
  iam_instance_profile  = aws_iam_instance_profile.ec2_profile.name

  user_data = local.user_data

  root_block_device {
    volume_size = 20
    volume_type = "gp3"
    encrypted   = true
  }

  monitoring = true

  tags = {
    Name = "${var.project_name}-instance"
    Environment = var.environment
  }

  # Create the instance in a public subnet for direct internet access
  associate_public_ip_address = true
}

# Elastic IP for consistent public IP
resource "aws_eip" "main" {
  instance = aws_instance.main.id
  domain   = "vpc"

  tags = {
    Name = "${var.project_name}-eip"
  }

  depends_on = [aws_instance.main]
}
