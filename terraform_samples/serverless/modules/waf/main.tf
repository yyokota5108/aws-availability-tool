#####################
# WAF Web ACL #
#####################
resource "aws_wafv2_web_acl" "this" {
  name        = "${var.project}-${var.environment}-web-acl"
  description = "WAF Web ACL for ${var.project} ${var.environment}"
  scope       = "REGIONAL"

  default_action {
    allow {}
  }

  # AWS マネージドルール - コアルールセット
  rule {
    name     = "AWS-AWSManagedRulesCommonRuleSet"
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
      metric_name                = "AWS-AWSManagedRulesCommonRuleSet"
      sampled_requests_enabled   = true
    }
  }

  # AWS マネージドルール - 既知の不正な入力
  rule {
    name     = "AWS-AWSManagedRulesKnownBadInputsRuleSet"
    priority = 2

    override_action {
      none {}
    }

    statement {
      managed_rule_group_statement {
        name        = "AWSManagedRulesKnownBadInputsRuleSet"
        vendor_name = "AWS"
      }
    }

    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "AWS-AWSManagedRulesKnownBadInputsRuleSet"
      sampled_requests_enabled   = true
    }
  }

  # レートベースのルール - IP制限
  rule {
    name     = "RateBasedRule"
    priority = 3

    action {
      block {}
    }

    statement {
      rate_based_statement {
        limit              = 1000
        aggregate_key_type = "IP"
      }
    }

    visibility_config {
      cloudwatch_metrics_enabled = true
      metric_name                = "RateBasedRule"
      sampled_requests_enabled   = true
    }
  }

  visibility_config {
    cloudwatch_metrics_enabled = true
    metric_name                = "${var.project}-${var.environment}-web-acl"
    sampled_requests_enabled   = true
  }

  tags = var.tags
}

#####################
# WAF Web ACL関連付け #
#####################
resource "aws_wafv2_web_acl_association" "this" {
  resource_arn = "arn:aws:apigateway:${data.aws_region.current.name}::/restapis/${var.api_gateway_id}/stages/${var.stage_name}"
  web_acl_arn  = aws_wafv2_web_acl.this.arn
}

#####################
# Data Source #
#####################
data "aws_region" "current" {}
