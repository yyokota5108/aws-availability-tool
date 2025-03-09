# RDSサブネットグループの作成
resource "aws_db_subnet_group" "main" {
  name        = "${var.project}-${var.environment}-db-subnet-group"
  description = "Database subnet group for ${var.project}-${var.environment}"
  subnet_ids  = var.subnet_ids

  tags = merge(
    {
      Name        = "${var.project}-${var.environment}-db-subnet-group"
      Environment = var.environment
      Project     = var.project
    },
    var.tags
  )
}

# RDSパラメータグループの作成
resource "aws_db_parameter_group" "main" {
  name        = "${var.project}-${var.environment}-db-parameter-group"
  family      = "mysql8.0"
  description = "Database parameter group for ${var.project}-${var.environment}"

  parameter {
    name  = "character_set_server"
    value = "utf8mb4"
  }

  parameter {
    name  = "character_set_client"
    value = "utf8mb4"
  }

  tags = merge(
    {
      Name        = "${var.project}-${var.environment}-db-parameter-group"
      Environment = var.environment
      Project     = var.project
    },
    var.tags
  )
}

# RDSインスタンスの作成
resource "aws_db_instance" "main" {
  identifier = "${var.project}-${var.environment}-db"

  engine            = "mysql"
  engine_version    = "8.0"
  instance_class    = var.instance_class
  allocated_storage = var.allocated_storage
  storage_type      = "gp3"
  storage_encrypted = true

  db_name  = var.database_name
  username = var.master_username
  password = var.master_password

  multi_az               = var.multi_az
  db_subnet_group_name   = aws_db_subnet_group.main.name
  vpc_security_group_ids = [var.security_group_id]
  parameter_group_name   = aws_db_parameter_group.main.name

  backup_retention_period = var.backup_retention_period
  backup_window           = "03:00-04:00"
  maintenance_window      = "Mon:04:00-Mon:05:00"

  auto_minor_version_upgrade = true
  copy_tags_to_snapshot      = true
  skip_final_snapshot        = true

  tags = merge(
    {
      Name        = "${var.project}-${var.environment}-db"
      Environment = var.environment
      Project     = var.project
    },
    var.tags
  )
} 
