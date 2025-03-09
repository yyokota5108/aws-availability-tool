#!/usr/bin/env python3
"""
Terraform可用性チェックツール CLI

Terraformコードを解析してJSONに変換し、AWSリソースの可用性を評価するCLIツール
"""

import argparse
import os
import sys
import time

from rich.console import Console
from rich.panel import Panel

from src.terraform.terraform_exporter import TerraformExporter
from src.analysis.availability_checker import AvailabilityChecker

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
"""
    console.print(Panel(examples, title="[bold]コマンドライン使用例[/bold]", border_style="cyan"))


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
    parser.add_argument(
        "--region", help="AWS リージョン", default=os.environ.get("AWS_REGION", "ap-northeast-1")
    )
    parser.add_argument(
        "--model",
        help="Bedrock モデルID",
        default="anthropic.claude-3-5-sonnet-20240620-v1:0",
    )
    parser.add_argument(
        "--language", help="使用する言語（ja/en）", choices=["ja", "en"], default="ja"
    )
    parser.add_argument(
        "--skip-analysis", action="store_true", help="Bedrockによる分析をスキップし、JSONエクスポートのみを実行"
    )
    parser.add_argument("--debug", action="store_true", help="デバッグモードを有効化")
    parser.add_argument("--example", action="store_true", help="使用例を表示")

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

    # terraform_dirが指定されていない場合はヘルプを表示
    if args.terraform_dir is None:
        parser.print_help()
        print("\n")
        print_help_examples()
        return

    # デバッグモードの設定
    if args.debug:
        os.environ["DEBUG"] = "1"

    # AWS リージョンの設定
    os.environ["AWS_REGION"] = args.region

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

    # チェッカーの初期化
    checker = AvailabilityChecker(
        model_id=args.model, region_name=args.region, language=args.language, debug=args.debug
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
