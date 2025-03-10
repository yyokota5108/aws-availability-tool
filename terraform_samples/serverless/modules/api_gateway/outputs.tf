output "api_id" {
  description = "ID of the API Gateway REST API"
  value       = aws_api_gateway_rest_api.this.id
}

output "invoke_url" {
  description = "Invoke URL of the API Gateway"
  value       = "${aws_api_gateway_deployment.this.invoke_url}${aws_api_gateway_resource.this.path}"
}

output "stage_name" {
  description = "Stage name of the API Gateway"
  value       = aws_api_gateway_stage.this.stage_name
}

output "execution_arn" {
  description = "Execution ARN of the API Gateway"
  value       = aws_api_gateway_rest_api.this.execution_arn
}
