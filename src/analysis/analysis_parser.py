"""
Bedrockからのレスポンスを解析するモジュール
"""

import json
from typing import Dict, Any, cast

from rich.console import Console

# Richコンソールを初期化
console = Console()


class AnalysisParser:
    """
    Bedrockからの分析結果を解析するクラス
    """

    def __init__(self, debug: bool = False):
        """
        AnalysisParserの初期化

        Args:
            debug: デバッグモードを有効にするかどうか
        """
        self.debug = debug

    def parse(self, analysis_text: str) -> Dict[str, Any]:
        """
        Bedrockからのテキストレスポンスを解析し、構造化されたデータに変換

        Args:
            analysis_text: Bedrockからのレスポンステキスト

        Returns:
            解析された構造化データ
        """
        try:
            # まず、JSON全体をパースしてみる
            try:
                # 最初に単純にJSONとしてパースを試みる
                analysis_result = json.loads(analysis_text)
                return cast(Dict[str, Any], analysis_result)
            except json.JSONDecodeError:
                # 単純なJSONではない場合、JSONブロックを探す
                json_start = analysis_text.find("```json")
                if json_start >= 0:
                    json_end = analysis_text.rfind("```")
                    json_text = analysis_text[json_start + 7 : json_end].strip()
                else:
                    # ```jsonが見つからない場合、{から始まるJSONを探す
                    json_start = analysis_text.find("{")
                    json_end = analysis_text.rfind("}") + 1
                    if json_start >= 0 and json_end > json_start:
                        json_text = analysis_text[json_start:json_end].strip()
                    else:
                        # JSONが見つからない場合
                        return {"raw_analysis": analysis_text}

                # JSON解析を試みる
                try:
                    analysis_result = json.loads(json_text)
                    return cast(Dict[str, Any], analysis_result)
                except json.JSONDecodeError as je:
                    # JSON解析に失敗した場合のデバッグ情報
                    if self.debug:
                        console.print(f"[bold red]JSON解析エラー: {je}[/bold red]")
                        console.print(f"解析対象テキスト: {json_text[:100]}...")
                    return {"raw_analysis": analysis_text}
        except Exception as e:
            # 何らかの予期せぬエラーが発生した場合
            if self.debug:
                console.print(f"[bold red]解析エラー: {e}[/bold red]")
            return {"raw_analysis": analysis_text}

    def validate_analysis_results(self, results: Dict[str, Any]) -> bool:
        """
        分析結果が必要な形式に従っているかを検証

        Args:
            results: 検証する分析結果

        Returns:
            検証結果（True=有効、False=無効）
        """
        required_keys = ["overview", "availability_score", "findings", "recommendations"]

        # 必須キーの存在確認
        for key in required_keys:
            if key not in results:
                if self.debug:
                    console.print(
                        f"[bold yellow]警告: 分析結果に必須キー '{key}' がありません[/bold yellow]"
                    )
                return False

        # findingsの検証
        if not isinstance(results["findings"], list):
            if self.debug:
                console.print("[bold yellow]警告: 'findings'がリストではありません[/bold yellow]")
            return False

        # recommendationsの検証
        if not isinstance(results["recommendations"], list):
            if self.debug:
                console.print(
                    "[bold yellow]警告: 'recommendations'がリストではありません[/bold yellow]"
                )
            return False

        return True
