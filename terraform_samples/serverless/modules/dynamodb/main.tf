####################
# DynamoDBテーブル #
####################
resource "aws_dynamodb_table" "this" {
  name         = "${var.project}-${var.environment}-data"
  billing_mode = "PROVISIONED"
  hash_key     = "id"

  read_capacity  = var.read_capacity
  write_capacity = var.write_capacity

  attribute {
    name = "id"
    type = "S"
  }

  point_in_time_recovery {
    enabled = true
  }

  server_side_encryption {
    enabled = true
  }

  tags = merge(
    var.tags,
    {
      Name = "${var.project}-${var.environment}-data"
    }
  )
}
