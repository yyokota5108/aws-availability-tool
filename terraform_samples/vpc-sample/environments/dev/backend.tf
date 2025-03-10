# terraform {
#   backend "s3" {
#     bucket         = "terraform-state-webservice-dev"
#     key            = "terraform.tfstate"
#     region         = "ap-northeast-1"
#     encrypt        = true
#     dynamodb_table = "terraform-lock-webservice-dev"
#   }
# } 

terraform {
  backend "local" {
    path = "./terraform.tfstate"
  }
}
