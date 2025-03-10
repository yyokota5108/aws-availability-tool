"""
Bedrockへ送信するプロンプトを生成するモジュール
"""

from typing import Dict, Any, Optional
import json

from src.config import get_settings


class PromptGenerator:
    """
    Terraform解析用のプロンプトを生成するクラス
    """

    def __init__(self, language: Optional[str] = None):
        """
        PromptGeneratorの初期化

        Args:
            language: プロンプトの言語（Noneの場合は設定から取得）
        """
        settings = get_settings()
        self.language = language or settings["app"]["language"]

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
3. ロードバランサーの設定: 適切に設定されているか（該当する場合）
4. オートスケーリングの設定: 需要の変動に対応できるか（該当する場合）
5. サーバーレスアーキテクチャの高可用性:
   - Lambda関数の冗長性と並列実行設定
   - API Gatewayのスロットリングとステージ設定
   - DynamoDBのグローバルテーブルと読み書き容量
   - S3のクロスリージョンレプリケーション設定
   - Step Functionsのエラーハンドリングとリトライ設定
6. バックアップと復旧メカニズム: データ損失からの保護と復旧手段
7. タイムアウト設定とリトライ機構: 一時的な障害からの回復
8. リージョン間の復元力: 地理的な冗長性があるか
9. その他の可用性関連の設定

注意事項:
- VPC構成がある場合は、ネットワークの可用性についても評価してください。
- サーバーレス構成の場合は、Lambda、API Gateway、DynamoDB、S3などのサービスの設定を重点的に評価してください。
- 両方の要素が混在する場合は、それぞれの観点から評価してください。

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
      "description": "推奨事項の詳細説明"
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
3. Load Balancer Configuration: Are load balancers properly configured? (if applicable)
4. Auto Scaling Configuration: Can the system handle demand fluctuations? (if applicable)
5. Serverless Architecture High Availability:
   - Lambda function redundancy and concurrent execution settings
   - API Gateway throttling and stage settings
   - DynamoDB global tables and read/write capacity
   - S3 cross-region replication configuration
   - Step Functions error handling and retry settings
6. Backup and Recovery Mechanisms: Protection against data loss and recovery methods
7. Timeout Settings and Retry Mechanisms: Recovery from temporary failures
8. Cross-Region Resilience: Is there geographical redundancy?
9. Other availability-related configurations

Notes:
- If VPC configuration exists, evaluate network availability as well.
- For serverless configurations, focus on evaluating Lambda, API Gateway, DynamoDB, S3, and other relevant service settings.
- If both elements are present, evaluate from both perspectives.

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
      "description": "Detailed description of the recommendation"
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
        # JSONの整形（読みやすさのため）
        if terraform_data:
            return json.dumps(terraform_data, indent=2, ensure_ascii=False)
        return "{}"
