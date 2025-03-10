output "web_acl_id" {
  description = "作成されたWAF ACLのID"
  value       = aws_wafv2_web_acl.main.id
}

output "web_acl_arn" {
  description = "WAF ACLのARN"
  value       = aws_wafv2_web_acl.main.arn
}

output "ip_set_id" {
  description = "ブロックされたIPセットのID"
  value       = aws_wafv2_ip_set.blocked_ips.id
}

output "ip_set_arn" {
  description = "ブロックされたIPセットのARN"
  value       = aws_wafv2_ip_set.blocked_ips.arn
}

output "log_group_name" {
  description = "WAFログのCloudWatch Logグループ名"
  value       = aws_cloudwatch_log_group.waf.name
}

output "log_group_arn" {
  description = "WAFログのCloudWatch LogグループのARN"
  value       = aws_cloudwatch_log_group.waf.arn
} 
