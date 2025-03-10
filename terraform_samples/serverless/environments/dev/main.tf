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

# IAMロールとポリシーの作成
module "iam" {
  source = "../../modules/iam"

  project     = local.project
  environment = local.environment
  tags        = local.tags
}

# S3バケットの作成
module "s3" {
  source = "../../modules/s3"

  project       = local.project
  environment   = local.environment
  force_destroy = local.force_destroy
  tags          = local.tags
}

# DynamoDBテーブルの作成
module "dynamodb" {
  source = "../../modules/dynamodb"

  project        = local.project
  environment    = local.environment
  read_capacity  = local.read_capacity
  write_capacity = local.write_capacity
  tags           = local.tags
}

# Lambdaファンクションの作成
module "lambda" {
  source = "../../modules/lambda"

  project             = local.project
  environment         = local.environment
  vpc_id              = module.vpc.vpc_id
  subnet_ids          = module.vpc.private_subnet_ids
  lambda_role_arn     = module.iam.lambda_role_arn
  s3_bucket_name      = module.s3.bucket_name
  lambda_runtime      = local.lambda_runtime
  memory_size         = local.memory_size
  timeout             = local.timeout
  dynamodb_table_name = module.dynamodb.table_name
  dynamodb_table_arn  = module.dynamodb.table_arn
  tags                = local.tags
}

# API Gatewayの作成
module "api_gateway" {
  source = "../../modules/api_gateway"

  project              = local.project
  environment          = local.environment
  lambda_function_name = module.lambda.function_name
  lambda_invoke_arn    = module.lambda.invoke_arn
  tags                 = local.tags
}

# WAFの作成
module "waf" {
  source = "../../modules/waf"

  project        = local.project
  environment    = local.environment
  api_gateway_id = module.api_gateway.api_id
  stage_name     = module.api_gateway.stage_name
  tags           = local.tags
}
