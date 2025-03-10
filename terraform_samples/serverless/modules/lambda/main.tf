#####################
# Lambda関数コード #
#####################
data "archive_file" "lambda_code" {
  type        = "zip"
  output_path = "${path.module}/lambda_function.zip"

  source {
    content  = <<EOF
exports.handler = async (event) => {
  console.log('Event: ', JSON.stringify(event, null, 2));
  
  // DynamoDBからデータを取得するサンプルコード
  // const AWS = require('aws-sdk');
  // const dynamodb = new AWS.DynamoDB.DocumentClient();
  
  // S3にデータを保存するサンプルコード
  // const s3 = new AWS.S3();
  
  return {
    statusCode: 200,
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      message: 'Hello from Lambda!',
      timestamp: new Date().toISOString()
    })
  };
};
EOF
    filename = "index.js"
  }
}

#####################
# Lambda関数 #
#####################
resource "aws_lambda_function" "this" {
  function_name = "${var.project}-${var.environment}-function"
  role          = var.lambda_role_arn
  handler       = "index.handler"
  runtime       = var.lambda_runtime
  memory_size   = var.memory_size
  timeout       = var.timeout

  filename         = data.archive_file.lambda_code.output_path
  source_code_hash = data.archive_file.lambda_code.output_base64sha256

  vpc_config {
    subnet_ids         = var.subnet_ids
    security_group_ids = [aws_security_group.lambda.id]
  }

  environment {
    variables = {
      ENVIRONMENT    = var.environment
      DYNAMODB_TABLE = var.dynamodb_table_name
      S3_BUCKET      = var.s3_bucket_name
    }
  }

  tags = var.tags
}

#####################
# Lambda権限 #
#####################
resource "aws_lambda_permission" "api_gateway" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.this.function_name
  principal     = "apigateway.amazonaws.com"
}

#####################
# セキュリティグループ #
#####################
resource "aws_security_group" "lambda" {
  name        = "${var.project}-${var.environment}-lambda-sg"
  description = "Security group for Lambda functions"
  vpc_id      = var.vpc_id

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = merge(
    var.tags,
    {
      Name = "${var.project}-${var.environment}-lambda-sg"
    }
  )
}

#####################
# CloudWatch Logs #
#####################
resource "aws_cloudwatch_log_group" "lambda" {
  name              = "/aws/lambda/${aws_lambda_function.this.function_name}"
  retention_in_days = 14

  tags = var.tags
}
