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
  description = "RDSインスタンスを配置するサブネットのIDリスト"
  type        = list(string)
}

variable "security_group_id" {
  description = "RDS用セキュリティグループのID"
  type        = string
}

variable "instance_class" {
  description = "RDSインスタンスクラス"
  type        = string
  default     = "db.t3.micro"
}

variable "allocated_storage" {
  description = "割り当てるストレージサイズ（GB）"
  type        = number
  default     = 20
}

variable "database_name" {
  description = "作成するデータベース名"
  type        = string
}

variable "master_username" {
  description = "マスターユーザー名"
  type        = string
}

variable "master_password" {
  description = "マスターパスワード"
  type        = string
}

variable "multi_az" {
  description = "マルチAZ構成を有効にするかどうか"
  type        = bool
  default     = false
}

variable "backup_retention_period" {
  description = "バックアップ保持期間（日）"
  type        = number
  default     = 7
}

variable "tags" {
  description = "リソースに付与する追加のタグ"
  type        = map(string)
  default     = {}
} 
