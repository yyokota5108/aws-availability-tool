variable "project" {
  description = "Project name"
  type        = string
}

variable "environment" {
  description = "Environment name"
  type        = string
}

variable "vpc_id" {
  description = "VPC ID where Lambda will be deployed"
  type        = string
}

variable "subnet_ids" {
  description = "Subnet IDs where Lambda will be deployed"
  type        = list(string)
}

variable "lambda_role_arn" {
  description = "ARN of the IAM role for Lambda"
  type        = string
}

variable "s3_bucket_name" {
  description = "Name of the S3 bucket for Lambda code"
  type        = string
}

variable "lambda_runtime" {
  description = "Runtime for Lambda function"
  type        = string
  default     = "nodejs18.x"
}

variable "memory_size" {
  description = "Memory size for Lambda function in MB"
  type        = number
  default     = 128
}

variable "timeout" {
  description = "Timeout for Lambda function in seconds"
  type        = number
  default     = 10
}

variable "dynamodb_table_name" {
  description = "Name of the DynamoDB table"
  type        = string
}

variable "dynamodb_table_arn" {
  description = "ARN of the DynamoDB table"
  type        = string
}

variable "tags" {
  description = "Tags to apply to resources"
  type        = map(string)
  default     = {}
}
