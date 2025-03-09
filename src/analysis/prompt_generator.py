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

    def create_availability_prompt(self, terraform_data: Dict[str, Any], detailed_mode: bool = False) -> str:
        """
        可用性分析のためのプロンプトを作成

        Args:
            terraform_data: 分析対象のTerraformデータ
            detailed_mode: 詳細モードを有効にするかどうか（より詳細な分析）

        Returns:
            生成されたプロンプト
        """
        # Terraformデータをプロンプト用に整形
        terraform_json = self._format_terraform_data(terraform_data)
        
        # 主要なAWSリソースタイプを特定
        resource_types = self._identify_resource_types(terraform_data)
        
        # 詳細モードの場合、リソース固有の評価項目を追加
        resource_specific_criteria = ""
        if detailed_mode:
            resource_specific_criteria = self._get_resource_specific_criteria(resource_types)

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
7. ヘルスチェックとモニタリング: 問題の早期発見と対応
8. 災害復旧計画: リージョン障害からの回復手段
9. セキュリティと可用性のバランス: セキュリティ対策が可用性に与える影響
{resource_specific_criteria}

分析結果を以下のJSON形式で提供してください:

```json
{{
  "overview": "インフラストラクチャの可用性に関する全体的な評価",
  "availability_score": 数値（0-100）,
  "findings": [
    {{
      "category": "カテゴリ名（例: マルチAZ構成、SPOF、バックアップなど）",
      "severity": "high/medium/low",
      "description": "詳細な説明",
      "recommendation": "改善のための具体的な提案",
      "effort": "high/medium/low（実装の難易度）",
      "risk_impact": "high/medium/low（問題が及ぼす影響の大きさ）"
    }}
  ],
  "recommendations": [
    {{
      "priority": "high/medium/low",
      "description": "推奨事項の詳細説明",
      "effort": "high/medium/low（実装の難易度）",
      "terraform_example": "改善のためのTerraformコード例（該当する場合）",
      "cost_impact": "increase/neutral/decrease（コストへの影響）"
    }}
  ],
  "suggested_slo": {{
    "availability_target": "推奨される可用性の目標値（例: 99.9%）",
    "rationale": "この目標値を提案する理由"
  }}
}}
```

高可用性の観点から重要な問題に焦点を当て、最も影響の大きい改善策を優先してください。
各推奨事項には、可能な限り具体的なTerraformコード例を含めてください。
コスト効率と可用性のバランスを考慮し、過剰な冗長性は避けつつ、適切な耐障害性を持つ設計を提案してください。
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
7. Health Checks and Monitoring: Early detection and response to issues
8. Disaster Recovery Plan: Recovery methods from regional failures
9. Security and Availability Balance: How security measures affect availability
{resource_specific_criteria}

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
      "recommendation": "Specific recommendations for improvement",
      "effort": "high/medium/low (implementation difficulty)",
      "risk_impact": "high/medium/low (impact of the issue)"
    }}
  ],
  "recommendations": [
    {{
      "priority": "high/medium/low",
      "description": "Detailed description of the recommendation",
      "effort": "high/medium/low (implementation difficulty)",
      "terraform_example": "Example Terraform code for implementation (if applicable)",
      "cost_impact": "increase/neutral/decrease (impact on cost)"
    }}
  ],
  "suggested_slo": {{
    "availability_target": "Suggested availability target (e.g., 99.9%)",
    "rationale": "Rationale for this target"
  }}
}}
```

Focus on important issues from a high availability perspective and prioritize improvements
with the most significant impact. Include specific Terraform code examples where possible.
Consider the balance between cost efficiency and availability, avoiding excessive redundancy
while ensuring appropriate fault tolerance.
"""

        return system_prompt

    def _identify_resource_types(self, terraform_data: Dict[str, Any]) -> list:
        """
        Terraformデータから主要なAWSリソースタイプを特定

        Args:
            terraform_data: Terraformデータ

        Returns:
            特定されたリソースタイプのリスト
        """
        resource_types = set()
        
        # リソースの走査
        if "resource" in terraform_data:
            for resource_type, resources in terraform_data.get("resource", {}).items():
                if resource_type.startswith("aws_"):
                    resource_types.add(resource_type)
        
        return list(resource_types)

    def _get_resource_specific_criteria(self, resource_types: list) -> str:
        """
        特定のAWSリソースタイプに対する評価基準を取得

        Args:
            resource_types: 評価対象のリソースタイプのリスト

        Returns:
            リソース固有の評価基準テキスト
        """
        criteria_text = ""
        
        if self.language == "ja":
            if "aws_ec2_instance" in resource_types:
                criteria_text += "\n10. EC2特有の評価項目:\n   - インスタンスタイプは適切か\n   - ユーザーデータ（起動スクリプト）の冗長性\n   - EBSボリュームの設定（gp3, io2等）\n   - ENIの冗長構成"
            
            if "aws_rds_instance" in resource_types or "aws_rds_cluster" in resource_types:
                criteria_text += "\n11. RDS特有の評価項目:\n   - マルチAZ構成の有無\n   - リードレプリカの設定\n   - バックアップ保持期間の妥当性\n   - メンテナンスウィンドウとバックアップウィンドウの設定"
            
            if "aws_lambda_function" in resource_types:
                criteria_text += "\n12. Lambda特有の評価項目:\n   - タイムアウト設定の妥当性\n   - 同時実行数の設定\n   - デッドレターキューの設定\n   - リトライ設定"
            
            if "aws_dynamodb_table" in resource_types:
                criteria_text += "\n13. DynamoDB特有の評価項目:\n   - グローバルテーブルの設定\n   - オンデマンドキャパシティモードか\n   - バックアップ設定\n   - TTL設定"
        else:
            # 英語版
            if "aws_ec2_instance" in resource_types:
                criteria_text += "\n10. EC2-Specific Criteria:\n   - Appropriate instance type\n   - User data (launch script) redundancy\n   - EBS volume configuration (gp3, io2, etc.)\n   - ENI redundant configuration"
            
            if "aws_rds_instance" in resource_types or "aws_rds_cluster" in resource_types:
                criteria_text += "\n11. RDS-Specific Criteria:\n   - Multi-AZ configuration\n   - Read replica setup\n   - Backup retention period adequacy\n   - Maintenance and backup window configuration"
            
            if "aws_lambda_function" in resource_types:
                criteria_text += "\n12. Lambda-Specific Criteria:\n   - Timeout setting adequacy\n   - Concurrency setting\n   - Dead letter queue configuration\n   - Retry settings"
            
            if "aws_dynamodb_table" in resource_types:
                criteria_text += "\n13. DynamoDB-Specific Criteria:\n   - Global tables configuration\n   - On-demand capacity mode\n   - Backup settings\n   - TTL settings"
        
        return criteria_text

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
