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

variable "subnet_ids" {
  description = "EC2インスタンスを配置するサブネットのIDリスト"
  type        = list(string)
}

variable "security_group_id" {
  description = "EC2用セキュリティグループのID"
  type        = string
}

variable "instance_type" {
  description = "EC2インスタンスタイプ"
  type        = string
  default     = "t3.micro"
}

variable "key_name" {
  description = "EC2インスタンスのキーペア名"
  type        = string
}

variable "target_group_arn" {
  description = "ALBターゲットグループのARN"
  type        = string
}

variable "instance_count" {
  description = "作成するEC2インスタンスの数"
  type        = number
  default     = 2
}

variable "tags" {
  description = "リソースに付与する追加のタグ"
  type        = map(string)
  default     = {}
} 
