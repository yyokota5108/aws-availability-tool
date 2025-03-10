locals {
  project     = "webservice"
  environment = "dev"

  vpc_cidr             = "10.0.0.0/16"
  public_subnet_cidrs  = ["10.0.1.0/24", "10.0.2.0/24"]
  private_subnet_cidrs = ["10.0.11.0/24", "10.0.12.0/24"]

  instance_type = "t3.micro"
  key_name      = "webservice-dev"

  db_instance_class = "db.t3.micro"
  db_name           = "webservice"
  db_username       = "admin"
  db_password       = "WebService123!"
  multi_az          = false

  tags = {
    Owner       = "DevTeam"
    Environment = "Development"
    Project     = "WebService"
  }
}
