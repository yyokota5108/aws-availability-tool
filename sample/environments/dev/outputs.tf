output "vpc_id" {
  description = "作成されたVPCのID"
  value       = module.vpc.vpc_id
}

output "public_subnet_ids" {
  description = "パブリックサブネットのIDリスト"
  value       = module.vpc.public_subnet_ids
}

output "private_subnet_ids" {
  description = "プライベートサブネットのIDリスト"
  value       = module.vpc.private_subnet_ids
}

output "alb_dns_name" {
  description = "ALBのDNS名"
  value       = module.alb.alb_dns_name
}

output "ec2_instance_ids" {
  description = "EC2インスタンスのIDリスト"
  value       = module.ec2.instance_ids
}

output "ec2_private_ips" {
  description = "EC2インスタンスのプライベートIPアドレスリスト"
  value       = module.ec2.instance_private_ips
}

output "rds_endpoint" {
  description = "RDSインスタンスのエンドポイント"
  value       = module.rds.db_instance_endpoint
}

output "waf_web_acl_id" {
  description = "WAF ACLのID"
  value       = module.waf.web_acl_id
} 
