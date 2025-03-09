output "instance_ids" {
  description = "作成されたEC2インスタンスのIDリスト"
  value       = aws_instance.web[*].id
}

output "instance_private_ips" {
  description = "EC2インスタンスのプライベートIPアドレスリスト"
  value       = aws_instance.web[*].private_ip
}

output "iam_role_name" {
  description = "EC2インスタンスに割り当てられたIAMロール名"
  value       = aws_iam_role.ec2_role.name
}

output "iam_role_arn" {
  description = "EC2インスタンスに割り当てられたIAMロールのARN"
  value       = aws_iam_role.ec2_role.arn
} 
