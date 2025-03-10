locals {
  project     = "serverless-app"
  environment = "dev"

  # VPC設定
  vpc_cidr             = "10.0.0.0/16"
  public_subnet_cidrs  = ["10.0.1.0/24", "10.0.2.0/24"]
  private_subnet_cidrs = ["10.0.11.0/24", "10.0.12.0/24"]

  # Lambda設定
  lambda_runtime = "nodejs18.x"
  memory_size    = 128
  timeout        = 10

  # DynamoDB設定
  read_capacity  = 5
  write_capacity = 5

  # S3設定
  force_destroy = true # 開発環境では削除を許可

  # 共通タグ
  tags = {
    Owner       = "DevTeam"
    Environment = "Development"
    Project     = "ServerlessApp"
    Terraform   = "true"
  }
}
