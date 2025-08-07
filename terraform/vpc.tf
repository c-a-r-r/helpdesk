# VPC and Networking Resources

# Data source for existing VPC (when using existing VPC)
data "aws_vpc" "existing" {
  count = var.use_existing_vpc ? 1 : 0
  id    = var.existing_vpc_id
}

# Data sources for existing subnets (when using existing VPC)
data "aws_subnet" "existing_public" {
  count = var.use_existing_vpc ? length(var.existing_public_subnet_ids) : 0
  id    = var.existing_public_subnet_ids[count.index]
}

data "aws_subnet" "existing_private" {
  count = var.use_existing_vpc ? length(var.existing_private_subnet_ids) : 0
  id    = var.existing_private_subnet_ids[count.index]
}

# VPC (only created when not using existing VPC)
resource "aws_vpc" "main" {
  count                = var.use_existing_vpc ? 0 : 1
  cidr_block           = var.vpc_cidr
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name = "${var.project_name}-vpc"
  }
}

# Internet Gateway (only created when not using existing VPC)
resource "aws_internet_gateway" "main" {
  count  = var.use_existing_vpc ? 0 : 1
  vpc_id = aws_vpc.main[0].id

  tags = {
    Name = "${var.project_name}-igw"
  }
}

# Public Subnets (only created when not using existing VPC)
resource "aws_subnet" "public" {
  count             = var.use_existing_vpc ? 0 : length(var.public_subnet_cidrs)
  vpc_id            = aws_vpc.main[0].id
  cidr_block        = var.public_subnet_cidrs[count.index]
  availability_zone = data.aws_availability_zones.available.names[count.index]

  map_public_ip_on_launch = true

  tags = {
    Name = "${var.project_name}-public-subnet-${count.index + 1}"
    Type = "public"
  }
}

# Private Subnets (only created when not using existing VPC)
resource "aws_subnet" "private" {
  count             = var.use_existing_vpc ? 0 : length(var.private_subnet_cidrs)
  vpc_id            = aws_vpc.main[0].id
  cidr_block        = var.private_subnet_cidrs[count.index]
  availability_zone = data.aws_availability_zones.available.names[count.index]

  tags = {
    Name = "${var.project_name}-private-subnet-${count.index + 1}"
    Type = "private"
  }
}

# NAT Gateway Elastic IPs (only created when not using existing VPC)
resource "aws_eip" "nat" {
  count  = var.use_existing_vpc ? 0 : length(var.public_subnet_cidrs)
  domain = "vpc"

  tags = {
    Name = "${var.project_name}-nat-eip-${count.index + 1}"
  }

  depends_on = [aws_internet_gateway.main]
}

# NAT Gateways (only created when not using existing VPC)
resource "aws_nat_gateway" "main" {
  count         = var.use_existing_vpc ? 0 : length(var.public_subnet_cidrs)
  allocation_id = aws_eip.nat[count.index].id
  subnet_id     = aws_subnet.public[count.index].id

  tags = {
    Name = "${var.project_name}-nat-gw-${count.index + 1}"
  }

  depends_on = [aws_internet_gateway.main]
}

# Route Table for Public Subnets (only created when not using existing VPC)
resource "aws_route_table" "public" {
  count  = var.use_existing_vpc ? 0 : 1
  vpc_id = aws_vpc.main[0].id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.main[0].id
  }

  tags = {
    Name = "${var.project_name}-public-rt"
  }
}

# Route Table for Private Subnets (only created when not using existing VPC)
resource "aws_route_table" "private" {
  count  = var.use_existing_vpc ? 0 : length(var.private_subnet_cidrs)
  vpc_id = aws_vpc.main[0].id

  route {
    cidr_block     = "0.0.0.0/0"
    nat_gateway_id = aws_nat_gateway.main[count.index].id
  }

  tags = {
    Name = "${var.project_name}-private-rt-${count.index + 1}"
  }
}

# Route Table Associations for Public Subnets (only created when not using existing VPC)
resource "aws_route_table_association" "public" {
  count          = var.use_existing_vpc ? 0 : length(var.public_subnet_cidrs)
  subnet_id      = aws_subnet.public[count.index].id
  route_table_id = aws_route_table.public[0].id
}

# Route Table Associations for Private Subnets (only created when not using existing VPC)
resource "aws_route_table_association" "private" {
  count          = var.use_existing_vpc ? 0 : length(var.private_subnet_cidrs)
  subnet_id      = aws_subnet.private[count.index].id
  route_table_id = aws_route_table.private[count.index].id
}

# Local values to reference VPC and subnets consistently
locals {
  vpc_id = var.use_existing_vpc ? data.aws_vpc.existing[0].id : aws_vpc.main[0].id
  
  public_subnet_ids = var.use_existing_vpc ? var.existing_public_subnet_ids : aws_subnet.public[*].id
  
  private_subnet_ids = var.use_existing_vpc ? var.existing_private_subnet_ids : aws_subnet.private[*].id
  
  vpc_cidr = var.use_existing_vpc ? data.aws_vpc.existing[0].cidr_block : var.vpc_cidr
}
