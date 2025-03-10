variable "project" {
  description = "プロジェクト名"
  type        = string
}

variable "environment" {
  description = "環境名（dev/stg/prod）"
  type        = string
}

variable "vpc_id" {
  description = "VPCのID"
  type        = string
}

variable "public_subnet_ids" {
  description = "パブリックサブネットのIDリスト"
  type        = list(string)
}

variable "security_group_id" {
  description = "ALB用セキュリティグループのID"
  type        = string
}

variable "target_group_port" {
  description = "ターゲットグループのポート"
  type        = number
  default     = 80
}

variable "health_check_path" {
  description = "ヘルスチェックのパス"
  type        = string
  default     = "/"
}

variable "tags" {
  description = "リソースに付与する追加のタグ"
  type        = map(string)
  default     = {}
} 
