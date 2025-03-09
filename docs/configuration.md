# 設定管理ガイド

AWS Terraform可用性チェックツールの設定管理システムに関する詳細ガイドです。

## 目次
- [設定管理ガイド](#設定管理ガイド)
  - [目次](#目次)
  - [設定の優先順位](#設定の優先順位)
  - [設定ファイル](#設定ファイル)
    - [サポートされている形式](#サポートされている形式)
    - [設定ファイルの検索順序](#設定ファイルの検索順序)
    - [設定ファイルの構造](#設定ファイルの構造)
  - [環境変数](#環境変数)
    - [サポートされている環境変数](#サポートされている環境変数)
    - [.envファイル](#envファイル)
  - [コマンドラインオプション](#コマンドラインオプション)
  - [設定カスタマイズの例](#設定カスタマイズの例)
    - [リージョンとモデルIDの変更](#リージョンとモデルidの変更)
    - [出力ディレクトリの変更](#出力ディレクトリの変更)
    - [言語設定の変更](#言語設定の変更)
    - [デバッグモードの有効化](#デバッグモードの有効化)
  - [現在の設定値の確認](#現在の設定値の確認)

## 設定の優先順位

設定は以下の優先順位で適用されます：

1. **コマンドラインオプション**：最も優先度が高く、他のすべての設定を上書きします
2. **環境変数**：コマンドラインオプションがない場合に適用されます
3. **設定ファイル**：環境変数がない場合に適用されます
4. **デフォルト値**：他の設定がない場合に使用されるベースライン設定

この優先順位により、ユーザーは複数のレベルで設定をカスタマイズできます。一般的な設定は設定ファイルで管理し、特定の実行に対しては環境変数やコマンドラインオプションで上書きできます。

## 設定ファイル

### サポートされている形式

現在、設定ファイルとしては以下の形式がサポートされています：

- **YAML** (推奨): 読みやすく、構造化された設定ファイル形式です
- **JSON**: プログラムによる操作に適した代替形式です
- **INI**: シンプルなキー/値ペアの形式です（限定的なサポート）

例: `config.yaml`
```yaml
aws:
  region: ap-northeast-1
  model_id: anthropic.claude-3-5-sonnet-20240620-v1:0
```

### 設定ファイルの検索順序

ツールは以下の順序で設定ファイルを探します：

1. `--config` オプションで指定されたパス
2. カレントディレクトリの `config.yaml`
3. カレントディレクトリの `config/config.yaml`
4. ホームディレクトリの `.aws_availability/config.yaml`

最初に見つかった設定ファイルが読み込まれます。複数の設定ファイルがある場合、優先順位の高いファイルが使用されます。

### 設定ファイルの構造

設定ファイルは以下のセクションに分かれています：

```yaml
# AWS関連設定
aws:
  region: ap-northeast-1           # AWSリージョン
  model_id: anthropic.claude-3-5-sonnet-20240620-v1:0  # 使用するAI Modelのモデルタイプ

# 出力設定
output:
  directory: output                # 出力ディレクトリ
  default_json_filename: terraform_parsed.json  # 解析結果JSONファイル名
  default_report_filename: availability_report.json  # レポートJSONファイル名
  default_html_filename: availability_report.html  # HTMLレポートファイル名

# アプリケーション設定
app:
  language: ja                     # 言語設定（ja/en）
  debug: false                     # デバッグモード
```

## 環境変数

環境変数を使用すると、設定ファイルの値を上書きしたり、設定ファイルなしで設定したりできます。

### サポートされている環境変数

以下の環境変数がサポートされています：

| 環境変数 | 説明 | デフォルト値 |
|---|---|---|
| `AWS_REGION` | AWSリージョン | `ap-northeast-1` |
| `AWS_MODEL_ID` | 使用するAIモデル | `anthropic.claude-3-5-sonnet-20240620-v1:0` |
| `OUTPUT_DIRECTORY` | 出力ディレクトリのパス | `output` |
| `OUTPUT_JSON_FILENAME` | 解析結果JSONファイル名 | `terraform_parsed.json` |
| `OUTPUT_REPORT_FILENAME` | レポートJSONファイル名 | `availability_report.json` |
| `OUTPUT_HTML_FILENAME` | HTMLレポートファイル名 | `availability_report.html` |
| `APP_LANGUAGE` | アプリケーション言語 (`ja`/`en`) | `ja` |
| `APP_DEBUG` | デバッグモード (`true`/`false`) | `false` |

### .envファイル

環境変数は `.env` ファイルに保存することもできます。このファイルはプロジェクトのルートディレクトリに配置します。

サンプル `.env` ファイル：
```
AWS_REGION=us-east-1
AWS_MODEL_ID=anthropic.claude-3-5-sonnet-20240620-v1:0
OUTPUT_DIRECTORY=custom_output
APP_LANGUAGE=en
APP_DEBUG=true
```

## コマンドラインオプション

コマンドラインオプションを使用すると、特定の実行に対して設定を簡単に上書きできます。

```bash
terraform-availability \
  --region us-east-1 \
  --model-id anthropic.claude-3-5-sonnet-20240620-v1:0 \
  --output-dir custom_output \
  --language en \
  --debug
```

使用可能なすべてのコマンドラインオプションを表示するには：

```bash
terraform-availability --help
```

設定関連のヘルプのみを表示するには：

```bash
terraform-availability --config-help
```

## 設定カスタマイズの例

### リージョンとモデルIDの変更

**設定ファイル** (`config.yaml`):
```yaml
aws:
  region: us-west-2
  model_id: anthropic.claude-3-5-sonnet-20240620-v1:0
```

**環境変数**:
```bash
export AWS_REGION=us-west-2
export AWS_MODEL_ID=anthropic.claude-3-5-sonnet-20240620-v1:0
```

**コマンドライン**:
```bash
terraform-availability --region us-west-2 --model-id anthropic.claude-3-5-sonnet-20240620-v1:0
```

### 出力ディレクトリの変更

**設定ファイル** (`config.yaml`):
```yaml
output:
  directory: custom_output
```

**環境変数**:
```bash
export OUTPUT_DIRECTORY=custom_output
```

**コマンドライン**:
```bash
terraform-availability --output-dir custom_output
```

### 言語設定の変更

**設定ファイル** (`config.yaml`):
```yaml
app:
  language: en
```

**環境変数**:
```bash
export APP_LANGUAGE=en
```

**コマンドライン**:
```bash
terraform-availability --language en
```

### デバッグモードの有効化

**設定ファイル** (`config.yaml`):
```yaml
app:
  debug: true
```

**環境変数**:
```bash
export APP_DEBUG=true
```

**コマンドライン**:
```bash
terraform-availability --debug
```

## 現在の設定値の確認

現在の実行環境で使用されている設定値を確認するには：

```bash
terraform-availability --show-config
```

このコマンドは、設定の優先順位に従って現在有効なすべての設定値を表示します。これは、複数の設定ソースがある場合に実際にどの設定が使用されているかを確認するのに役立ちます。 