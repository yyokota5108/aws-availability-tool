output "vpc_id" {
  description = "作成されたVPCのID"
  value       = aws_vpc.main.id
}

output "public_subnet_ids" {
  description = "作成されたパブリックサブネットのIDリスト"
  value       = aws_subnet.public[*].id
}

output "private_subnet_ids" {
  description = "作成されたプライベートサブネットのIDリスト"
  value       = aws_subnet.private[*].id
}

output "vpc_cidr_block" {
  description = "VPCのCIDRブロック"
  value       = aws_vpc.main.cidr_block
}

output "nat_gateway_ids" {
  description = "作成されたNATゲートウェイのIDリスト"
  value       = aws_nat_gateway.main[*].id
}

output "public_route_table_id" {
  description = "パブリックルートテーブルのID"
  value       = aws_route_table.public.id
}

output "private_route_table_ids" {
  description = "プライベートルートテーブルのIDリスト"
  value       = aws_route_table.private[*].id
}

# セキュリティグループの出力
output "alb_security_group_id" {
  description = "ALB用セキュリティグループのID"
  value       = aws_security_group.alb.id
}

output "ec2_security_group_id" {
  description = "EC2用セキュリティグループのID"
  value       = aws_security_group.ec2.id
}

output "rds_security_group_id" {
  description = "RDS用セキュリティグループのID"
  value       = aws_security_group.rds.id
}
