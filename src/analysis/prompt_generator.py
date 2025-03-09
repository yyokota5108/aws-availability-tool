"""
Bedrockへ送信するプロンプトを生成するモジュール
"""

from typing import Dict, Any


class PromptGenerator:
    """
    Terraform解析用のプロンプトを生成するクラス
    """

    def __init__(self, language: str = "ja"):
        """
        PromptGeneratorの初期化

        Args:
            language: プロンプトの言語（デフォルトは日本語）
        """
        self.language = language

    def create_availability_prompt(self, terraform_data: Dict[str, Any]) -> str:
        """
        可用性分析のためのプロンプトを作成

        Args:
            terraform_data: 分析対象のTerraformデータ

        Returns:
            生成されたプロンプト
        """
        # Terraformデータをプロンプト用に整形
        terraform_json = self._format_terraform_data(terraform_data)

        # プロンプトテンプレート
        if self.language == "ja":
            system_prompt = f"""
AWSのTerraformコードの可用性を評価してください。AWS Well-Architected Frameworkの信頼性の柱に基づいて分析し、
インフラストラクチャの可用性を向上させる具体的な提案を提示してください。

以下のJSON形式のTerraformリソースを分析してください:

```json
{terraform_json}
```

評価項目:
1. マルチAZ構成: リソースが複数のアベイラビリティーゾーンにデプロイされているか
2. 単一障害点(SPOF): システム内に単一障害点が存在するか
3. ロードバランサーの設定: 適切に設定されているか
4. オートスケーリングの設定: 需要の変動に対応できるか
5. バックアップと復旧メカニズム: データ損失からの保護と復旧手段
6. タイムアウト設定とリトライ機構: 一時的な障害からの回復
7. その他の可用性関連の設定

分析結果を以下のJSON形式で提供してください:

```json
{{
  "overview": "インフラストラクチャの可用性に関する全体的な評価",
  "availability_score": 数値（0-100）,
  "findings": [
    {{
      "category": "カテゴリ名（例: マルチAZ構成、SPOF、バックアップなど）",
      "severity": "高/中/低",
      "description": "詳細な説明",
      "recommendation": "改善のための具体的な提案"
    }}
  ],
  "recommendations": [
    {{
      "priority": "高/中/低",
      "description": "推奨事項の詳細説明",
      "terraform_example": "実装例（Terraformコード）"
    }}
  ]
}}
```

高可用性の観点から重要な問題に焦点を当て、最も影響の大きい改善策を優先してください。
"""
        else:
            # 英語のプロンプト
            system_prompt = f"""
Please evaluate the availability of AWS resources defined in the Terraform code below.
Analyze based on the AWS Well-Architected Framework's Reliability pillar and provide
specific recommendations to improve the infrastructure's availability.

Analyze the following Terraform resources in JSON format:

```json
{terraform_json}
```

Evaluation criteria:
1. Multi-AZ Configuration: Are resources deployed across multiple Availability Zones?
2. Single Points of Failure (SPOF): Are there any single points of failure in the system?
3. Load Balancer Configuration: Are load balancers properly configured?
4. Auto Scaling Configuration: Can the system handle demand fluctuations?
5. Backup and Recovery Mechanisms: Protection against data loss and recovery methods
6. Timeout Settings and Retry Mechanisms: Recovery from temporary failures
7. Other availability-related configurations

Please provide your analysis in the following JSON format:

```json
{{
  "overview": "Overall assessment of the infrastructure's availability",
  "availability_score": numeric value (0-100),
  "findings": [
    {{
      "category": "Category name (e.g., Multi-AZ, SPOF, Backup, etc.)",
      "severity": "high/medium/low",
      "description": "Detailed description",
      "recommendation": "Specific recommendations for improvement"
    }}
  ],
  "recommendations": [
    {{
      "priority": "high/medium/low",
      "description": "Detailed description of the recommendation",
      "terraform_example": "Implementation example (Terraform code)"
    }}
  ]
}}
```

Focus on important issues from a high availability perspective and prioritize improvements
with the most significant impact.
"""

        return system_prompt

    def _format_terraform_data(self, terraform_data: Dict[str, Any]) -> str:
        """
        Terraformデータを読みやすい形式に整形

        Args:
            terraform_data: Terraformデータ

        Returns:
            整形されたJSONテキスト
        """
        import json

        # JSONの整形（読みやすさのため）
        if terraform_data:
            return json.dumps(terraform_data, indent=2, ensure_ascii=False)
        return "{}"
