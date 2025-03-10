"""
AWS Bedrock APIとのインタラクションを担当するモジュール
"""

import json
import os
import time
from typing import Dict, Any, Optional

import boto3
from rich.console import Console

from src.config import get_settings

# Richコンソールを初期化
console = Console()


class BedrockClient:
    """
    AWS BedrockとのAPIインタラクションを処理するクラス
    """

    def __init__(
        self,
        bedrock_client: Any = None,
        model_id: Optional[str] = None,
        region_name: Optional[str] = None,
    ) -> None:
        """
        BedrockClientの初期化

        Args:
            bedrock_client: 既存のboto3 Bedrock clientインスタンス（指定がなければ新規作成）
            model_id: 使用するBedrockモデルID（Noneの場合は設定から取得）
            region_name: AWSリージョン名（Noneの場合は設定から取得）
        """
        settings = get_settings()
        self.region_name = region_name or settings["aws"]["region"]
        self.bedrock_client = bedrock_client or boto3.client(
            service_name="bedrock-runtime", region_name=self.region_name
        )
        self.model_id = model_id or settings["aws"]["model_id"]

    def invoke(
        self, prompt: str, max_tokens: int = 4096, temperature: float = 0.2
    ) -> Dict[str, Any]:
        """
        Bedrockモデルを呼び出す

        Args:
            prompt: Bedrockモデルに送信するプロンプト
            max_tokens: 生成するトークンの最大数
            temperature: 生成テキストのランダム性（0.0-1.0）

        Returns:
            モデルからのレスポンス
        """
        # Bedrockリクエストの作成
        request_body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": [{"role": "user", "content": prompt}],
        }

        start_time = time.time()

        try:
            # Bedrockへリクエスト送信
            response = self.bedrock_client.invoke_model(
                modelId=self.model_id, body=json.dumps(request_body)
            )

            # レスポンスのデコード
            response_body = json.loads(response.get("body").read().decode("utf-8"))
            analysis_text = response_body.get("content", [{}])[0].get("text", "")

            elapsed_time = time.time() - start_time
            console.print(f"Bedrock呼び出し完了: [bold green]{elapsed_time:.1f}秒[/bold green]")

            return {"text": analysis_text, "elapsed_time": elapsed_time}

        except Exception as e:
            console.print(f"[bold red]エラー: Bedrockの呼び出しに失敗しました: {e}[/bold red]")
            return {"error": str(e)}
