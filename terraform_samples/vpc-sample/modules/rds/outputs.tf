output "db_instance_id" {
  description = "RDSインスタンスのID"
  value       = aws_db_instance.main.id
}

output "db_instance_endpoint" {
  description = "RDSインスタンスのエンドポイント"
  value       = aws_db_instance.main.endpoint
}

output "db_instance_address" {
  description = "RDSインスタンスのアドレス"
  value       = aws_db_instance.main.address
}

output "db_instance_port" {
  description = "RDSインスタンスのポート"
  value       = aws_db_instance.main.port
}

output "db_subnet_group_name" {
  description = "RDSサブネットグループ名"
  value       = aws_db_subnet_group.main.name
}

output "db_parameter_group_name" {
  description = "RDSパラメータグループ名"
  value       = aws_db_parameter_group.main.name
} 
