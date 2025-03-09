"""
Terraformリソースの可用性チェックを行うメインモジュール
"""

from typing import Dict, Any, Optional

from src.client.bedrock_client import BedrockClient
from src.analysis.prompt_generator import PromptGenerator
from src.analysis.analysis_parser import AnalysisParser
from src.ui.console_renderer import ConsoleRenderer
from src.reporting.report_generator import ReportGenerator
from src.config import get_settings


class AvailabilityChecker:
    """
    Terraformリソースの可用性をチェックするメインクラス
    """

    def __init__(
        self,
        model_id: Optional[str] = None,
        region_name: Optional[str] = None,
        language: Optional[str] = None,
        debug: Optional[bool] = None,
        detailed_mode: Optional[bool] = None,
    ) -> None:
        """
        AvailabilityCheckerの初期化
        
        Args:
            model_id: 使用するBedrockモデルID（Noneの場合は設定から取得）
            region_name: AWSリージョン名（Noneの場合は設定から取得）
            language: 使用言語（Noneの場合は設定から取得）
            debug: デバッグモードを有効にするかどうか（Noneの場合は設定から取得）
            detailed_mode: 詳細分析モードを有効にするかどうか（Noneの場合は設定から取得）
        """
        settings = get_settings()
        
        # デバッグ設定
        self.debug = debug if debug is not None else settings["app"]["debug"]
        
        # 詳細モード設定
        self.detailed_mode = detailed_mode if detailed_mode is not None else settings["app"].get("detailed_mode", False)
        
        # 各コンポーネントの初期化
        self.bedrock_client = BedrockClient(model_id=model_id, region_name=region_name)
        self.prompt_generator = PromptGenerator(language=language)
        self.analysis_parser = AnalysisParser(debug=self.debug)
        self.console_renderer = ConsoleRenderer()
        self.report_generator = ReportGenerator(output_dir=settings["output"]["directory"])

    def analyze_with_bedrock(self, terraform_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Bedrockを使用してTerraformリソースの可用性を分析
        
        Args:
            terraform_data: 分析対象のTerraformデータ
            
        Returns:
            分析結果
        """
        # プロンプトの作成
        prompt = self.prompt_generator.create_availability_prompt(
            terraform_data, 
            detailed_mode=self.detailed_mode
        )

        # Bedrockを使用して分析
        response = self.bedrock_client.invoke(prompt)

        # エラーチェック
        if "error" in response:
            return {"error": response["error"]}

        # レスポンスの解析
        analysis_text = response["text"]
        analysis_result = self.analysis_parser.parse(analysis_text)

        # 検証
        if not self.analysis_parser.validate_analysis_results(analysis_result):
            # 検証に失敗した場合は生のテキストを返す
            return {"raw_analysis": analysis_text}

        return analysis_result

    def print_analysis_results(self, results: Dict[str, Any]) -> None:
        """
        分析結果をコンソールに表示
        
        Args:
            results: 表示する分析結果
        """
        self.console_renderer.print_analysis_results(results)

    def save_json_report(self, results: Dict[str, Any], output_file: str) -> str:
        """
        分析結果をJSONファイルとして保存
        
        Args:
            results: 保存する分析結果
            output_file: 出力ファイルのパス
            
        Returns:
            保存したファイルのフルパス
        """
        return self.report_generator.save_json_report(results, output_file)

    def export_as_html(self, results: Dict[str, Any], output_file: str) -> str:
        """
        分析結果をHTMLファイルとして出力
        
        Args:
            results: HTMLに変換する分析結果
            output_file: 出力HTMLファイルのパス
            
        Returns:
            保存したファイルのフルパス
        """
        return self.report_generator.export_as_html(results, output_file)
