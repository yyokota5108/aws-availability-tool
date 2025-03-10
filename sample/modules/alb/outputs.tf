output "alb_arn" {
  description = "作成されたALBのARN"
  value       = aws_lb.main.arn
}

output "alb_dns_name" {
  description = "ALBのDNS名"
  value       = aws_lb.main.dns_name
}

output "target_group_arn" {
  description = "作成されたターゲットグループのARN"
  value       = aws_lb_target_group.main.arn
}

output "http_listener_arn" {
  description = "HTTPリスナーのARN"
  value       = aws_lb_listener.http.arn
} 
