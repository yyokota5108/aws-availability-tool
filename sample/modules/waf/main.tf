# WAF IPセットの作成
resource "aws_wafv2_ip_set" "blocked_ips" {
  name               = "${var.project}-${var.environment}-blocked-ips"
  description        = "Blocked IP addresses"
  scope              = "REGIONAL"
  ip_address_version = "IPV4"
  addresses          = []

  tags = merge(
    {
      Name        = "${var.project}-${var.environment}-blocked-ips"
      Environment = var.environment
      Project     = var.project
    },
    var.tags
  )
}

# WAF ACLの作成
resource "aws_wafv2_web_acl" "main" {
  name        = "${var.project}-${var.environment}-waf-acl"
  description = "WAF ACL for ${var.project}-${var.environment}"
  scope       = "REGIONAL"

  default_action {
    allow {}
  }

  rule {
    name     = "AWSManagedRulesCommonRuleSet"
    priority = 1

    override_action {
      none {}
    }

    statement {
      managed_rule_group_statement {
        name        = "AWSManagedRulesCommonRuleSet"
        vendor_name = "AWS"
      }
    }

    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "AWSManagedRulesCommonRuleSetMetric"
      sampled_requests_enabled   = true
    }
  }

  rule {
    name     = "IPRateLimit"
    priority = 2

    action {
      block {}
    }

    statement {
      rate_based_statement {
        limit              = var.ip_rate_limit
        aggregate_key_type = "IP"
      }
    }

    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "IPRateLimitMetric"
      sampled_requests_enabled   = true
    }
  }

  rule {
    name     = "BlockedIPs"
    priority = 3

    action {
      block {}
    }

    statement {
      ip_set_reference_statement {
        arn = aws_wafv2_ip_set.blocked_ips.arn
      }
    }

    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "BlockedIPsMetric"
      sampled_requests_enabled   = true
    }
  }

  visibility_config {
    cloudwatch_metrics_enabled = true
    metric_name                = "${var.project}-${var.environment}-waf-acl-metric"
    sampled_requests_enabled   = true
  }

  tags = merge(
    {
      Name        = "${var.project}-${var.environment}-waf-acl"
      Environment = var.environment
      Project     = var.project
    },
    var.tags
  )
}

# WAF ACLとALBの関連付け
resource "aws_wafv2_web_acl_association" "main" {
  resource_arn = var.alb_arn
  web_acl_arn  = aws_wafv2_web_acl.main.arn
}

# WAF ログの有効化
resource "aws_wafv2_web_acl_logging_configuration" "main" {
  log_destination_configs = [aws_cloudwatch_log_group.waf.arn]
  resource_arn            = aws_wafv2_web_acl.main.arn
}

# WAFログ用のCloudWatch Logグループ
resource "aws_cloudwatch_log_group" "waf" {
  name              = "/aws/waf/${var.project}-${var.environment}"
  retention_in_days = 30

  tags = merge(
    {
      Name        = "${var.project}-${var.environment}-waf-logs"
      Environment = var.environment
      Project     = var.project
    },
    var.tags
  )
} 
