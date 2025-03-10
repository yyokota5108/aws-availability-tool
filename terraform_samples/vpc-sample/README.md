# AWSウェブサイト構築（基本編）Terraformプロジェクト

このプロジェクトは、AWSウェブサイト構築（基本編）のアーキテクチャを実装するためのTerraformコードを提供します。

## アーキテクチャ概要

- マルチAZ構成（2つのアベイラビリティゾーン）
- パブリック/プライベートサブネット
- Application Load Balancer
- EC2インスタンス（Webサーバー）
- RDS for MySQL（Multi-AZ）
- AWS WAF

## 前提条件

- Terraform v1.4.0以上
- AWS CLIのインストールと設定
- AWS認証情報の設定

## ディレクトリ構造

```
terraform/
├── README.md
├── environments/
│   ├── dev/    # 開発環境
│   ├── stg/    # ステージング環境
│   └── prod/   # 本番環境
└── modules/
    ├── vpc/    # ネットワーク
    ├── alb/    # ロードバランサー
    ├── ec2/    # Webサーバー
    ├── rds/    # データベース
    └── waf/    # Webアプリケーションファイアウォール
```

## 使用方法

1. 環境の初期化
```bash
cd environments/dev
terraform init
```

2. 実行計画の確認
```bash
terraform plan
```

3. インフラストラクチャのデプロイ
```bash
terraform apply
```

4. インフラストラクチャの削除
```bash
terraform destroy
```

## 環境変数

以下の環境変数を設定する必要があります：

- `AWS_ACCESS_KEY_ID`: AWSアクセスキーID
- `AWS_SECRET_ACCESS_KEY`: AWSシークレットアクセスキー
- `AWS_DEFAULT_REGION`: AWSリージョン（デフォルト: ap-northeast-1）

## セキュリティ考慮事項

- すべてのデータは暗号化されています（RDS, EBS）
- セキュリティグループは最小権限原則に従って設定されています
- AWS WAFで基本的なWebアプリケーション保護を提供します

## 注意事項

- 本番環境へのデプロイは、必ず承認プロセスを経てください
- コスト最適化のため、開発環境ではマルチAZ構成を無効化しています
- 定期的なバックアップが設定されています 