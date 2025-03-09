# AWS Terraform可用性チェックツール

TerraformコードをJSONに変換し、AWS Bedrockを使用して可用性分析を行うツールです。AWS Well-Architected Frameworkの信頼性の柱に基づいて、インフラストラクチャの可用性を評価します。

## 機能

1. **Terraformコード解析**：Terraformコードを解析してJSON形式に変換
2. **可用性分析**：AWS Bedrockを使用してTerraformリソースの可用性を評価
3. **改善提案**：可用性を向上させるための具体的な提案を提示
4. **レポート出力**：分析結果をJSON形式およびHTML形式で保存可能

## 前提条件

- Python 3.7以上
- AWS CLI設定済み
- AWS Bedrockへのアクセス権限
- Terraformプロジェクト（解析対象）

## インストール

### 方法1: pipでインストール（推奨）

```bash
# リポジトリをクローン
git clone <repository-url>
cd aws_availability_tool

# パッケージとしてインストール
pip install -e .
```

### 方法2: 依存パッケージのみインストール

```bash
# リポジトリをクローン
git clone <repository-url>
cd aws_availability_tool

# 依存パッケージをインストール
pip install -r requirements.txt
```

### AWS認証情報の設定

```bash
# AWS CLIがインストール済みの場合
aws configure

# または環境変数を設定
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
export AWS_REGION=ap-northeast-1
```

## 使用方法

### 方法1: インストール済みのコマンドを使用（推奨）

```bash
# 基本的な使用法
terraform-availability /path/to/terraform/project
```

### 方法2: モジュールとして実行

```bash
# 基本的な使用法
python -m src.cli /path/to/terraform/project
```

### オプション

```
使用方法: terraform-availability [-h] [--json-output JSON_OUTPUT] [--report-output REPORT_OUTPUT] [--html HTML] [--region REGION] [--model MODEL] [--language {ja,en}] [--skip-analysis] [--debug] [--example] [terraform_dir]

AWSリソースの可用性チェックツール (Terraform解析 + Bedrockによる可用性評価)

位置引数:
  terraform_dir          Terraformプロジェクトのディレクトリパス

オプション:
  -h, --help             このヘルプメッセージを表示して終了
  --json-output JSON_OUTPUT
                         Terraform解析結果を保存するJSONファイルパス
  --report-output REPORT_OUTPUT
                         可用性評価レポートを保存するJSONファイルパス
  --html HTML            可用性評価結果をHTMLファイルとして出力するパス
  --region REGION        AWS リージョン
  --model MODEL          Bedrock モデルID
  --language {ja,en}     使用する言語（ja/en）
  --skip-analysis        Bedrockによる分析をスキップし、JSONエクスポートのみを実行
  --debug                デバッグモードを有効化
  --example              使用例を表示
```

### 実行例

#### Terraformプロジェクトの可用性をチェック
```bash
terraform-availability ~/projects/my-terraform-project
```

#### 解析結果と評価レポートを保存
```bash
terraform-availability ~/projects/my-terraform-project \
    --json-output terraform_export.json \
    --report-output availability_report.json
```

#### 結果をHTML形式で出力
```bash
terraform-availability ~/projects/my-terraform-project \
    --html availability_report.html
```

#### 英語で分析結果を出力
```bash
terraform-availability ~/projects/my-terraform-project \
    --language en
```

#### JSON変換のみ実行
```bash
terraform-availability ~/projects/my-terraform-project \
    --skip-analysis \
    --json-output terraform_export.json
```

## 設定管理

### 設定ファイル

このツールはYAML形式の設定ファイルをサポートしています。以下の場所の設定ファイルが自動的に読み込まれます（優先順位順）：

1. `--config` オプションで指定されたパス
2. カレントディレクトリの `config.yaml`
3. カレントディレクトリの `config/config.yaml`
4. ホームディレクトリの `.aws_availability/config.yaml`

設定ファイルのサンプルは `config/config.yaml.example` にあります。コピーして使用できます：

```bash
cp config/config.yaml.example config/config.yaml
# 必要に応じて編集
```

設定ファイルの基本構造：

```yaml
# AWS関連設定
aws:
  region: ap-northeast-1
  model_id: anthropic.claude-3-5-sonnet-20240620-v1:0

# 出力設定
output:
  directory: output
  default_json_filename: terraform_parsed.json
  default_report_filename: availability_report.json
  default_html_filename: availability_report.html

# アプリケーション設定
app:
  language: ja
  debug: false
```

### 環境変数

設定ファイルの代わりに、または設定ファイルを上書きするために環境変数を使用できます：

```bash
# AWS設定
export AWS_REGION=us-east-1
export AWS_MODEL_ID=anthropic.claude-3-5-sonnet-20240620-v1:0

# 出力設定
export OUTPUT_DIRECTORY=custom_output

# アプリケーション設定
export APP_LANGUAGE=en
export APP_DEBUG=true
```

環境変数を `.env` ファイルに保存することもできます。サンプルは `.env.example` にあります：

```bash
cp .env.example .env
# 必要に応じて編集
```

### 設定の優先順位

設定は以下の優先順位で適用されます：

1. コマンドラインオプション（例：`--region`）
2. 環境変数（例：`AWS_REGION`）
3. 設定ファイル
4. デフォルト値

詳細な設定ヘルプを表示するには：

```bash
terraform-availability --config-help
```

より詳細な設定管理については、[設定管理ガイド](docs/configuration.md)を参照してください。

## プロジェクト構造

```
aws_availability_tool/
├── src/                   # ソースコード
│   ├── analysis/          # 分析関連モジュール
│   ├── client/            # AWS APIクライアント
│   ├── config/            # 設定管理
│   ├── reporting/         # レポート生成
│   ├── terraform/         # Terraform解析
│   └── ui/                # ユーザーインターフェース
├── config/                # 設定ファイル
├── tests/                 # テストコード
└── docs/                  # ドキュメント
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

## 開発

### テスト実行

```bash
# テストの実行
pytest

# カバレッジレポート付きでテスト実行
pytest --cov=src
```

### コードフォーマット

```bash
# コードフォーマットの実行
black src tests

# 型チェック
mypy src

# リンター実行
flake8 src tests
```

## ライセンス

MIT

## 注意事項

- AWS Bedrockの使用にはコストが発生します
- 分析結果は参考情報であり、実際のシステム設計・運用においては専門家の判断を仰いでください 