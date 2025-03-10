# ALB用セキュリティグループ
resource "aws_security_group" "alb" {
  name_prefix = "${var.project}-${var.environment}-alb-sg"
  description = "Security group for ALB"
  vpc_id      = aws_vpc.main.id

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "Allow HTTP from anywhere"
  }

  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "Allow HTTPS from anywhere"
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
    description = "Allow all outbound traffic"
  }

  tags = merge(
    {
      Name        = "${var.project}-${var.environment}-alb-sg"
      Environment = var.environment
      Project     = var.project
    },
    var.tags
  )

  lifecycle {
    create_before_destroy = true
  }
}

# EC2用セキュリティグループ
resource "aws_security_group" "ec2" {
  name_prefix = "${var.project}-${var.environment}-ec2-sg"
  description = "Security group for EC2 instances"
  vpc_id      = aws_vpc.main.id

  ingress {
    from_port       = 80
    to_port         = 80
    protocol        = "tcp"
    security_groups = [aws_security_group.alb.id]
    description     = "Allow HTTP from ALB"
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
    description = "Allow all outbound traffic"
  }

  tags = merge(
    {
      Name        = "${var.project}-${var.environment}-ec2-sg"
      Environment = var.environment
      Project     = var.project
    },
    var.tags
  )

  lifecycle {
    create_before_destroy = true
  }
}

# RDS用セキュリティグループ
resource "aws_security_group" "rds" {
  name_prefix = "${var.project}-${var.environment}-rds-sg"
  description = "Security group for RDS instances"
  vpc_id      = aws_vpc.main.id

  ingress {
    from_port       = 3306
    to_port         = 3306
    protocol        = "tcp"
    security_groups = [aws_security_group.ec2.id]
    description     = "Allow MySQL from EC2 instances"
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
    description = "Allow all outbound traffic"
  }

  tags = merge(
    {
      Name        = "${var.project}-${var.environment}-rds-sg"
      Environment = var.environment
      Project     = var.project
    },
    var.tags
  )

  lifecycle {
    create_before_destroy = true
  }
} 
