variable "project" {
  description = "プロジェクト名"
  type        = string
}

variable "environment" {
  description = "環境名（dev/stg/prod）"
  type        = string
}

variable "alb_arn" {
  description = "WAFを関連付けるALBのARN"
  type        = string
}

variable "ip_rate_limit" {
  description = "IPアドレスごとのリクエスト制限（5分あたり）"
  type        = number
  default     = 2000
}

variable "tags" {
  description = "リソースに付与する追加のタグ"
  type        = map(string)
  default     = {}
} 
