# 利用可能なアベイラビリティゾーンの取得
data "aws_availability_zones" "available" {
  state = "available"
}

# 現在のAWSアカウントIDの取得
data "aws_caller_identity" "current" {}

# 現在のリージョンの取得
data "aws_region" "current" {} 
