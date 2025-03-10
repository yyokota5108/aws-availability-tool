# VPCの作成
module "vpc" {
  source = "../../modules/vpc"

  project              = local.project
  environment          = local.environment
  vpc_cidr             = local.vpc_cidr
  public_subnet_cidrs  = local.public_subnet_cidrs
  private_subnet_cidrs = local.private_subnet_cidrs
  tags                 = local.tags
}

# ALBの作成
module "alb" {
  source = "../../modules/alb"

  project           = local.project
  environment       = local.environment
  vpc_id            = module.vpc.vpc_id
  public_subnet_ids = module.vpc.public_subnet_ids
  security_group_id = module.vpc.alb_security_group_id
  tags              = local.tags
}

# EC2インスタンスの作成
module "ec2" {
  source = "../../modules/ec2"

  project           = local.project
  environment       = local.environment
  vpc_id            = module.vpc.vpc_id
  subnet_ids        = module.vpc.private_subnet_ids
  security_group_id = module.vpc.ec2_security_group_id
  instance_type     = local.instance_type
  key_name          = local.key_name
  target_group_arn  = module.alb.target_group_arn
  tags              = local.tags
}

# RDSの作成
module "rds" {
  source = "../../modules/rds"

  project           = local.project
  environment       = local.environment
  vpc_id            = module.vpc.vpc_id
  subnet_ids        = module.vpc.private_subnet_ids
  security_group_id = module.vpc.rds_security_group_id
  instance_class    = local.db_instance_class
  database_name     = local.db_name
  master_username   = local.db_username
  master_password   = local.db_password
  multi_az          = local.multi_az
  tags              = local.tags
}

# WAFの作成
module "waf" {
  source = "../../modules/waf"

  project     = local.project
  environment = local.environment
  alb_arn     = module.alb.alb_arn
  tags        = local.tags
}
