# VPCの作成
resource "aws_vpc" "main" {
  cidr_block           = var.vpc_cidr
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = merge(
    {
      Name        = "${var.project}-${var.environment}-vpc"
      Environment = var.environment
      Project     = var.project
    },
    var.tags
  )
}

# インターネットゲートウェイの作成
resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id

  tags = merge(
    {
      Name        = "${var.project}-${var.environment}-igw"
      Environment = var.environment
      Project     = var.project
    },
    var.tags
  )
}

# パブリックサブネットの作成
resource "aws_subnet" "public" {
  count             = length(var.public_subnet_cidrs)
  vpc_id            = aws_vpc.main.id
  cidr_block        = var.public_subnet_cidrs[count.index]
  availability_zone = var.azs[count.index]

  map_public_ip_on_launch = true

  tags = merge(
    {
      Name        = "${var.project}-${var.environment}-public-subnet-${count.index + 1}"
      Environment = var.environment
      Project     = var.project
      Type        = "public"
    },
    var.tags
  )
}

# プライベートサブネットの作成
resource "aws_subnet" "private" {
  count             = length(var.private_subnet_cidrs)
  vpc_id            = aws_vpc.main.id
  cidr_block        = var.private_subnet_cidrs[count.index]
  availability_zone = var.azs[count.index]

  tags = merge(
    {
      Name        = "${var.project}-${var.environment}-private-subnet-${count.index + 1}"
      Environment = var.environment
      Project     = var.project
      Type        = "private"
    },
    var.tags
  )
}

# Elastic IPの作成（NATゲートウェイ用）
resource "aws_eip" "nat" {
  count  = length(var.public_subnet_cidrs)
  domain = "vpc"

  tags = merge(
    {
      Name        = "${var.project}-${var.environment}-nat-eip-${count.index + 1}"
      Environment = var.environment
      Project     = var.project
    },
    var.tags
  )
}

# NATゲートウェイの作成
resource "aws_nat_gateway" "main" {
  count         = length(var.public_subnet_cidrs)
  allocation_id = aws_eip.nat[count.index].id
  subnet_id     = aws_subnet.public[count.index].id

  tags = merge(
    {
      Name        = "${var.project}-${var.environment}-nat-${count.index + 1}"
      Environment = var.environment
      Project     = var.project
    },
    var.tags
  )

  depends_on = [aws_internet_gateway.main]
}

# パブリックルートテーブルの作成
resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.main.id
  }

  tags = merge(
    {
      Name        = "${var.project}-${var.environment}-public-rt"
      Environment = var.environment
      Project     = var.project
    },
    var.tags
  )
}

# プライベートルートテーブルの作成
resource "aws_route_table" "private" {
  count  = length(var.private_subnet_cidrs)
  vpc_id = aws_vpc.main.id

  route {
    cidr_block     = "0.0.0.0/0"
    nat_gateway_id = aws_nat_gateway.main[count.index].id
  }

  tags = merge(
    {
      Name        = "${var.project}-${var.environment}-private-rt-${count.index + 1}"
      Environment = var.environment
      Project     = var.project
    },
    var.tags
  )
}

# パブリックサブネットとルートテーブルの関連付け
resource "aws_route_table_association" "public" {
  count          = length(var.public_subnet_cidrs)
  subnet_id      = aws_subnet.public[count.index].id
  route_table_id = aws_route_table.public.id
}

# プライベートサブネットとルートテーブルの関連付け
resource "aws_route_table_association" "private" {
  count          = length(var.private_subnet_cidrs)
  subnet_id      = aws_subnet.private[count.index].id
  route_table_id = aws_route_table.private[count.index].id
}
