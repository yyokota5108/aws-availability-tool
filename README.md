# AWS Terraform可用性チェックツール

TerraformコードをJSONに変換し、AWS Bedrockを使用して可用性分析を行うツールです。AWS Well-Architected Frameworkの信頼性の柱に基づいて、インフラストラクチャの可用性を評価します。

## 機能

1. **Terraformコード解析**：Terraformコードを解析してJSON形式に変換
2. **可用性分析**：AWS Bedrockを使用してTerraformリソースの可用性を評価
3. **改善提案**：可用性を向上させるための具体的な提案を提示
4. **レポート出力**：分析結果をJSON形式で保存可能

## 前提条件

- Python 3.7以上
- AWS CLI設定済み
- AWS Bedrockへのアクセス権限
- Terraformプロジェクト（解析対象）

## インストール

1. リポジトリをクローン
```bash
git clone <repository-url>
cd aws_availability_tool
```

2. 依存パッケージをインストール
```bash
pip install -r requirements.txt
```

3. AWS認証情報を設定
```bash
# AWS CLIがインストール済みの場合
aws configure

# または環境変数を設定
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
export AWS_REGION=ap-northeast-1
```

## 使用方法

### 基本的な使用法

```bash
python terraform_availability_checker.py /path/to/terraform/project
```

### オプション

```
使用方法: terraform_availability_checker.py [-h] [--json-output JSON_OUTPUT] [--report-output REPORT_OUTPUT] [--region REGION] [--model MODEL] [--skip-analysis] [--debug] terraform_dir

AWSリソースの可用性チェックツール (Terraform解析 + Bedrockによる可用性評価)

位置引数:
  terraform_dir          Terraformプロジェクトのディレクトリパス

オプション:
  -h, --help             このヘルプメッセージを表示して終了
  --json-output JSON_OUTPUT
                         Terraform解析結果を保存するJSONファイルパス
  --report-output REPORT_OUTPUT
                         可用性評価レポートを保存するJSONファイルパス
  --region REGION        AWS リージョン
  --model MODEL          Bedrock モデルID
  --skip-analysis        Bedrockによる分析をスキップし、JSONエクスポートのみを実行
  --debug                デバッグモードを有効化
```

### 実行例

#### Terraformプロジェクトの可用性をチェック
```bash
python terraform_availability_checker.py ~/projects/my-terraform-project
```

#### 解析結果と評価レポートを保存
```bash
python terraform_availability_checker.py ~/projects/my-terraform-project \
    --json-output terraform_export.json \
    --report-output availability_report.json
```

#### JSON変換のみ実行
```bash
python terraform_availability_checker.py ~/projects/my-terraform-project \
    --skip-analysis \
    --json-output terraform_export.json
```

## 評価項目

ツールは以下の観点でAWSリソースの可用性を評価します：

1. マルチAZ構成
2. 単一障害点(SPOF)の有無
3. ロードバランサーの設定
4. オートスケーリングの設定
5. バックアップと復旧メカニズム
6. タイムアウト設定とリトライ機構
7. 障害復旧時間目標（RTO）と復旧ポイント目標（RPO）
8. サービスレベル目標（SLO）の達成可能性
9. コスト効率を考慮した可用性向上策

## ライセンス

MIT

## 注意事項

- AWS Bedrockの使用にはコストが発生します
- 分析結果は参考情報であり、実際のシステム設計・運用においては専門家の判断を仰いでください 