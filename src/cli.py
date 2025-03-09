#!/usr/bin/env python3
"""
Terraform可用性チェックツール CLI

Terraformコードを解析してJSONに変換し、AWSリソースの可用性を評価するCLIツール
"""

import argparse
import os
import sys
import time
from typing import Optional

from rich.console import Console
from rich.panel import Panel

from src.terraform.terraform_exporter import TerraformExporter
from src.analysis.availability_checker import AvailabilityChecker
from src.config import get_settings, reset_settings

# Richコンソールを初期化
console = Console()


def print_help_examples() -> None:
    """ヘルプと使用例を表示"""
    examples = """
=== 使用例 ===

基本的な使い方:
    python -m src.cli ./terraform_project

Terraform解析結果をJSONファイルに保存:
    python -m src.cli ./terraform_project --json-output terraform_plan.json

可用性評価レポートをJSONファイルに保存:
    python -m src.cli ./terraform_project --report-output availability_report.json

可用性評価結果をHTMLファイルとして出力:
    python -m src.cli ./terraform_project --html availability_report.html

すべての出力形式を指定:
    python -m src.cli ./terraform_project --json-output terraform_plan.json \
        --report-output availability_report.json --html availability_report.html

異なるAWSリージョンを指定:
    python -m src.cli ./terraform_project --region us-east-1

Terraform解析のみを実行 (可用性分析をスキップ):
    python -m src.cli ./terraform_project --skip-analysis --json-output terraform_plan.json

設定ファイルの使用:
    python -m src.cli ./terraform_project --config path/to/config.yaml
"""
    console.print(Panel(examples, title="[bold]コマンドライン使用例[/bold]", border_style="cyan"))


def print_config_help() -> None:
    """設定ファイルとオプションの説明を表示"""
    config_help = """
=== 設定の優先順位 ===

設定は以下の優先順位で適用されます:
1. コマンドラインオプション
2. 環境変数
3. 指定された設定ファイル (--configオプション)
4. カレントディレクトリのconfig.yaml
5. ホームディレクトリの.aws_availability/config.yaml
6. デフォルト設定

=== 環境変数 ===

以下の環境変数がサポートされています:
- AWS_REGION: AWSリージョン
- AWS_MODEL_ID: BedrockモデルID
- OUTPUT_DIRECTORY: 出力ディレクトリ
- APP_LANGUAGE: 使用言語 (ja/en)
- APP_DEBUG: デバッグモード (true/false)

=== 設定ファイル形式 ===

config.yamlの例:
```yaml
aws:
  region: ap-northeast-1
  model_id: anthropic.claude-3-5-sonnet-20240620-v1:0
output:
  directory: output
app:
  language: ja
  debug: false
```
"""
    console.print(Panel(config_help, title="[bold]設定ヘルプ[/bold]", border_style="green"))


def main() -> None:
    """メイン関数"""
    parser = argparse.ArgumentParser(
        description="AWSリソースの可用性チェックツール (Terraform解析 + Bedrockによる可用性評価)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "terraform_dir", help="Terraformプロジェクトのディレクトリパス", nargs="?"
    )  # オプショナルに変更
    parser.add_argument("--json-output", help="Terraform解析結果を保存するJSONファイルパス")
    parser.add_argument("--report-output", help="可用性評価レポートを保存するJSONファイルパス")
    parser.add_argument("--html", help="可用性評価結果をHTMLファイルとして出力するパス")
    parser.add_argument("--region", help="AWS リージョン")
    parser.add_argument("--model", help="Bedrock モデルID")
    parser.add_argument("--language", help="使用する言語（ja/en）", choices=["ja", "en"])
    parser.add_argument(
        "--skip-analysis", action="store_true", help="Bedrockによる分析をスキップし、JSONエクスポートのみを実行"
    )
    parser.add_argument("--debug", action="store_true", help="デバッグモードを有効化")
    parser.add_argument("--detailed", action="store_true", help="詳細分析モードを有効化（リソース固有の分析を含む）")
    parser.add_argument("--example", action="store_true", help="使用例を表示")
    parser.add_argument("--config", help="設定ファイルのパス")
    parser.add_argument("--config-help", action="store_true", help="設定関連のヘルプを表示")

    # コマンドライン引数がない場合は使用例を表示
    if len(sys.argv) == 1:
        parser.print_help()
        print("\n")
        print_help_examples()
        return

    args = parser.parse_args()

    # 使用例の表示
    if args.example:
        print_help_examples()
        return

    # 設定ヘルプの表示
    if args.config_help:
        print_config_help()
        return

    # 設定の初期化（configファイルのパスが指定されている場合は環境変数に設定）
    if args.config:
        os.environ["CONFIG_FILE"] = args.config

    # 設定を読み込む
    settings = get_settings()

    # コマンドラインオプションで上書き
    if args.debug:
        settings["app"]["debug"] = True
        os.environ["APP_DEBUG"] = "true"

    if args.region:
        settings["aws"]["region"] = args.region
        os.environ["AWS_REGION"] = args.region

    if args.model:
        settings["aws"]["model_id"] = args.model
        os.environ["AWS_MODEL_ID"] = args.model

    if args.language:
        settings["app"]["language"] = args.language
        os.environ["APP_LANGUAGE"] = args.language

    # terraform_dirが指定されていない場合はヘルプを表示
    if args.terraform_dir is None:
        parser.print_help()
        print("\n")
        print_help_examples()
        return

    # ロゴ表示
    console.print("\n[bold blue]AWS Terraform可用性チェックツール[/bold blue]")
    console.rule()

    # ステップ1: Terraformコードを解析してJSONに変換
    console.print("\n[bold]ステップ1: Terraformコードの解析[/bold]")
    console.print(f"Terraformプロジェクトのパス: [bold]{args.terraform_dir}[/bold]")

    # Terraformエクスポーターの初期化
    terraform_exporter = TerraformExporter()

    start_time = time.time()
    terraform_data, json_file = terraform_exporter.export_to_json(
        args.terraform_dir, args.json_output
    )

    if terraform_data is None:
        console.print("[bold red]エラー: Terraformコードの解析に失敗しました。終了します。[/bold red]")
        sys.exit(1)

    export_time = time.time() - start_time
    console.print(f"解析完了: [bold green]{export_time:.1f}秒[/bold green]")

    # Bedrockによる分析をスキップする場合はここで終了
    if args.skip_analysis:
        console.print(
            "\n[bold yellow]注意: --skip-analysisが指定されたため、可用性分析はスキップされました。[/bold yellow]"
        )
        console.print(f"JSONファイルを確認してください: [bold]{json_file}[/bold]")
        sys.exit(0)

    # ステップ2: Bedrockによる可用性分析
    console.print("\n[bold]ステップ2: Bedrockによる可用性分析[/bold]")

    # チェッカーの初期化（コマンドラインオプションが優先）
    checker = AvailabilityChecker(
        model_id=args.model,
        region_name=args.region,
        language=args.language,
        debug=args.debug if args.debug else None,
        detailed_mode=args.detailed,
    )

    # 分析実行
    analysis_start_time = time.time()
    analysis_results = checker.analyze_with_bedrock(terraform_data)
    analysis_time = time.time() - analysis_start_time

    console.print(f"分析完了: [bold green]{analysis_time:.1f}秒[/bold green]")

    # 結果表示
    checker.print_analysis_results(analysis_results)

    # 結果の保存（JSON）
    if args.report_output:
        report_file = checker.save_json_report(analysis_results, args.report_output)
        console.print(f"\n可用性評価レポートを保存しました: [bold]{report_file}[/bold]")

    # HTML形式で出力
    if args.html:
        html_file = checker.export_as_html(analysis_results, args.html)
        console.print(f"\n可用性評価レポートをHTMLファイルに保存しました: [bold]{html_file}[/bold]")

    # 総実行時間
    total_time = export_time + analysis_time
    console.print(f"\n総実行時間: [bold green]{total_time:.1f}秒[/bold green]")


if __name__ == "__main__":
    main()
