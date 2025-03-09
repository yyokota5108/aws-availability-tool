import json
import argparse
import boto3
import sys
import os
import time
from typing import Dict, Any, List, Optional
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.syntax import Syntax
from rich.layout import Layout
from rich.spinner import Spinner
from rich.text import Text
from rich import box
from export_terraform_json import ensure_output_directory

# Richコンソールを初期化
console = Console()

class AvailabilityChecker:
    """Terraformリソースの可用性をチェックするクラス"""
    
    def __init__(self, bedrock_client=None, model_id="anthropic.claude-3-5-sonnet-20240620-v1:0"):
        """
        初期化メソッド
        
        Args:
            bedrock_client: Bedrock クライアント（指定がなければ新規作成）
            model_id: 使用するBedrockモデルID
        """
        self.bedrock_client = bedrock_client or boto3.client(
            service_name="bedrock-runtime",
            region_name=os.environ.get("AWS_REGION", "ap-northeast-1")
        )
        self.model_id = model_id
    
    def load_terraform_json(self, json_file: str) -> Dict[str, Any]:
        """
        TerraformのJSONファイルを読み込む
        
        Args:
            json_file: JSONファイルのパス
            
        Returns:
            解析されたJSONデータ
        """
        try:
            with open(json_file, 'r') as f:
                data = json.load(f)
            return data
        except Exception as e:
            console.print(f"[bold red]エラー: JSONファイルの読み込みに失敗しました: {e}[/bold red]")
            sys.exit(1)
    
    def analyze_with_bedrock(self, terraform_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Bedrockを使用してTerraformリソースの可用性を分析
        
        Args:
            terraform_data: 分析対象のTerraformデータ
            
        Returns:
            分析結果
        """
        console.print("[bold blue]ステップ2: Bedrockによる可用性分析[/bold blue]")
        console.print("Bedrockを使用してリソースの可用性を分析中...")
        
        # プロンプトの作成
        prompt = self._create_availability_prompt(terraform_data)
        
        # Bedrockリクエストの作成
        request_body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 4096,
            "temperature": 0.2,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        }
        
        start_time = time.time()
        
        try:
            # Bedrockへリクエスト送信
            response = self.bedrock_client.invoke_model(
                modelId=self.model_id,
                body=json.dumps(request_body)
            )
            
            # レスポンスのデコード
            response_body = json.loads(response.get('body').read().decode('utf-8'))
            analysis_text = response_body.get('content', [{}])[0].get('text', '')
            
            elapsed_time = time.time() - start_time
            console.print(f"分析完了: [bold green]{elapsed_time:.1f}秒[/bold green]")
            
            # JSON部分を抽出して解析
            try:
                # まず、JSON全体をパースしてみる
                try:
                    # 最初に単純にJSONとしてパースを試みる
                    analysis_result = json.loads(analysis_text)
                    return analysis_result
                except json.JSONDecodeError:
                    # 単純なJSONではない場合、JSONブロックを探す
                    json_start = analysis_text.find('```json')
                    if json_start >= 0:
                        json_end = analysis_text.rfind('```')
                        json_text = analysis_text[json_start + 7:json_end].strip()
                    else:
                        # ```jsonが見つからない場合、{から始まるJSONを探す
                        json_start = analysis_text.find('{')
                        json_end = analysis_text.rfind('}') + 1
                        if json_start >= 0 and json_end > json_start:
                            json_text = analysis_text[json_start:json_end].strip()
                        else:
                            # JSONが見つからない場合
                            return {"raw_analysis": analysis_text}
                    
                    # JSON解析を試みる
                    try:
                        analysis_result = json.loads(json_text)
                        return analysis_result
                    except json.JSONDecodeError as je:
                        # JSON解析に失敗した場合のデバッグ情報
                        if os.environ.get("DEBUG") == "1":
                            console.print(f"[bold red]JSON解析エラー: {je}[/bold red]")
                            console.print(f"解析対象テキスト: {json_text[:100]}...")
                        return {"raw_analysis": analysis_text}
            except Exception as e:
                # 何らかの予期せぬエラーが発生した場合
                if os.environ.get("DEBUG") == "1":
                    console.print(f"[bold red]解析エラー: {e}[/bold red]")
                return {"raw_analysis": analysis_text}
                
        except Exception as e:
            console.print(f"[bold red]エラー: Bedrockによる分析に失敗しました: {e}[/bold red]")
            return {"error": str(e)}
    
    def _create_availability_prompt(self, terraform_data: Dict[str, Any]) -> str:
        """
        可用性分析のためのプロンプトを作成
        
        Args:
            terraform_data: 分析対象のTerraformデータ
            
        Returns:
            プロンプト文字列
        """
        prompt = """
# AWSリソースの可用性分析

あなたはAWSソリューションアーキテクトとして、高可用性システムの設計と評価の専門家です。以下のTerraformコードを分析し、AWS Well-Architected Frameworkの信頼性の柱とベストプラクティスに基づいた可用性評価を行ってください。

## 分析対象

以下の点を重点的に分析し、JSON形式で結果を返してください:

1. マルチAZ構成になっているか（該当するサービスの場合）
2. 単一障害点(SPOF)が存在するか
3. サービス冗長性の確保（該当する場合、バックアップを含む）
4. スケーリング機構の設定は適切か
5. バックアップや復旧メカニズムの有無
6. タイムアウト設定とリトライ機構
7. 障害復旧時間目標（RTO）と復旧ポイント目標（RPO）
8. サービスレベル目標（SLO）達成のための構成
9. 可用性向上のための具体的な改善提案（コスト効率を考慮）
10. サービス固有の可用性ベストプラクティス

## ステータス定義

各項目の評価ステータスは以下の基準で判断してください:

- **GOOD**: 高可用性が確保されており、AWSベストプラクティスに完全に従っている
- **WARNING**: 部分的に高可用性が確保されているが、改善の余地がある
- **CRITICAL**: 高可用性が確保されておらず、単一障害点が存在する
- **NOT_APPLICABLE**: 該当するリソースが存在しない、または評価対象外

## 可用性スコアの算出基準

可用性スコア（0-100点）は以下の配点に基づいて算出してください:
- マルチAZ/冗長構成: 25点
- 単一障害点の排除: 25点
- スケーリング設定: 15点
- バックアップ/復旧メカニズム: 15点
- タイムアウト/リトライ設定: 10点
- 他の可用性向上施策: 10点

各項目のステータスに応じて点数を割り当て:
- GOOD: 配点の100%
- WARNING: 配点の50%
- CRITICAL: 0点
- NOT_APPLICABLE: 他の項目で按分

## リソースタイプ別の評価基準

以下のAWSリソースタイプごとに具体的な評価を行ってください:

### コンピューティングサービス
#### EC2インスタンス
- マルチAZ配置されているか
- Auto Scalingグループに所属しているか
- インスタンスヘルスチェックが設定されているか

#### Lambda
- 同時実行数の制限は適切か
- タイムアウト設定は適切か
- エラー処理とリトライ設定があるか
- 関数のコールド/ウォームスタートを考慮した設計か
- デッドレターキューが設定されているか

#### ECS/Fargate
- タスク定義のヘルスチェックは適切か
- サービスの複数AZへのデプロイ設定
- キャパシティプロバイダー戦略の設計

### データベースサービス
#### RDSデータベース
- マルチAZ設定が有効か
- リードレプリカが設定されているか
- 適切なバックアップ設定があるか

#### DynamoDB
- グローバルテーブルまたはバックアップ戦略があるか
- 適切なキャパシティモードを使用しているか
- DAXなどのキャッシングが考慮されているか

#### ElastiCache (Redis/Memcached)
- マルチAZ/クラスターモードの設定
- フェイルオーバー機能が有効か
- バックアップ戦略

### ロードバランシングと通信
#### ELB/ALB/NLB
- クロスゾーン負荷分散が有効か
- ヘルスチェックが適切に設定されているか
- 複数のAZにターゲットが分散されているか

#### API Gateway
- スロットリング設定は適切か
- キャッシュ機能が有効化されているか
- ステージ配備戦略（カナリアデプロイなど）
- バックエンドのタイムアウト設定

### メッセージングとキューイング
#### SQS
- デッドレターキューが設定されているか
- 可視性タイムアウトは適切か
- FIFOキューが必要な場合、適切に設定されているか

#### SNS
- トピックのクロスリージョン配信設定
- 配信再試行ポリシー
- メッセージフィルタリングの設定

#### EventBridge/CloudWatch Events
- イベントルールの冗長性
- デッドレターキューの設定
- リトライポリシー

### ストレージ
#### S3
- バージョニングが有効か
- クロスリージョンレプリケーションの設定
- ライフサイクルポリシーの設定

#### EFS/FSx
- バックアップ戦略
- マウントターゲットの複数AZ配置
- スループットとIO性能の設定

### ネットワーキング
#### VPC
- サブネットの複数AZ配置
- ルートテーブルとNATゲートウェイの冗長性
- VPCエンドポイントの設定

#### Route 53
- ヘルスチェックと障害時のフェイルオーバー設定
- ルーティングポリシーは適切か
- DNSフェイルオーバーの設定

### コンテナサービス
#### ECR
- イメージスキャンが有効か
- イメージライフサイクルポリシーの設定

#### EKS
- コントロールプレーンの冗長性
- ワーカーノードの複数AZ配置
- クラスタースケーリングの設定

### サーバーレスとイベント駆動
#### Step Functions
- エラーハンドリングの設定
- ステートマシンの冗長性
- タイムアウト設定

### キャッシュとCDN
#### CloudFront
- オリジンフェイルオーバーの設定
- エッジロケーションの活用
- キャッシュ設定とTTL

## 分析対象のJSON

```json
{terraform_json}
```

## 分析結果の出力形式

以下のJSON形式で結果を返してください:

```json
{
  "availability_score": 0-100の数値（可用性の総合スコア）,
  "multi_az_redundancy_configuration": {
    "status": "GOOD"|"WARNING"|"CRITICAL"|"NOT_APPLICABLE",
    "description": "説明",
    "resources": ["問題のあるリソースのリスト"]
  },
  "single_points_of_failure": {
    "status": "GOOD"|"WARNING"|"CRITICAL",
    "description": "説明",
    "resources": ["問題のあるリソースのリスト"]
  },
  "scaling_configuration": {
    "status": "GOOD"|"WARNING"|"CRITICAL"|"NOT_APPLICABLE",
    "description": "説明",
    "resources": ["問題のあるリソースのリスト"]
  },
  "backup_recovery_mechanisms": {
    "status": "GOOD"|"WARNING"|"CRITICAL"|"NOT_APPLICABLE",
    "description": "説明",
    "resources": ["問題のあるリソースのリスト"]
  },
  "timeout_retry_configurations": {
    "status": "GOOD"|"WARNING"|"CRITICAL"|"NOT_APPLICABLE",
    "description": "説明",
    "resources": ["問題のあるリソースのリスト"]
  },
  "recovery_time_objectives": {
    "estimated_rto": "推定されるRTO（例：「~30分」）",
    "estimated_rpo": "推定されるRPO（例：「~15分」）",
    "status": "GOOD"|"WARNING"|"CRITICAL",
    "description": "説明"
  },
  "service_level_objectives": {
    "estimated_availability": "推定される可用性（例：「99.95%」）",
    "status": "GOOD"|"WARNING"|"CRITICAL",
    "description": "現在の構成で達成可能なSLOと改善点の説明"
  },
  "cost_efficiency": {
    "status": "GOOD"|"WARNING"|"CRITICAL",
    "description": "コスト効率と可用性のバランスについての評価"
  },
  "service_specific_recommendations": {
    "compute": {
      "ec2": ["EC2に関する推奨事項"],
      "lambda": ["Lambdaに関する推奨事項"],
      "ecs": ["ECS/Fargateに関する推奨事項"]
    },
    "database": {
      "rds": ["RDSに関する推奨事項"],
      "dynamodb": ["DynamoDBに関する推奨事項"],
      "elasticache": ["ElastiCacheに関する推奨事項"]
    },
    "networking": {
      "elb": ["ELB/ALB/NLBに関する推奨事項"],
      "api_gateway": ["API Gatewayに関する推奨事項"],
      "route53": ["Route 53に関する推奨事項"],
      "vpc": ["VPCに関する推奨事項"]
    },
    "messaging": {
      "sqs": ["SQSに関する推奨事項"],
      "sns": ["SNSに関する推奨事項"],
      "eventbridge": ["EventBridgeに関する推奨事項"]
    },
    "storage": {
      "s3": ["S3に関する推奨事項"],
      "efs": ["EFS/FSxに関する推奨事項"]
    },
    "serverless": {
      "step_functions": ["Step Functionsに関する推奨事項"]
    },
    "cdn_caching": {
      "cloudfront": ["CloudFrontに関する推奨事項"]
    },
    "containers": {
      "ecr": ["ECRに関する推奨事項"],
      "eks": ["EKSに関する推奨事項"]
    },
    "other": ["その他のサービスに関する推奨事項"]
  },
  "improvement_suggestions": [
    {
      "priority": "HIGH"|"MEDIUM"|"LOW",
      "description": "提案の説明",
      "resources": ["関連リソースのリスト"],
      "implementation_example": "Terraformコードの実装サンプル（該当する場合）",
      "cost_impact": "LOW"|"MEDIUM"|"HIGH",
      "availability_impact": "LOW"|"MEDIUM"|"HIGH"
    }
  ],
  "overall_assessment": "全体的な評価と推奨事項の要約"
}
```

JSONのみを返してください。説明や前置き、後書きは不要です。
"""
        
        # JSONデータを文字列に変換してプロンプトに埋め込む
        terraform_json_str = json.dumps(terraform_data, indent=2)
        final_prompt = prompt.replace("{terraform_json}", terraform_json_str)
        
        return final_prompt
    
    def print_analysis_results(self, results: Dict[str, Any]) -> None:
        """
        分析結果を整形して表示
        
        Args:
            results: 分析結果
        """
        # まず結果がJSONオブジェクトを含む文字列である場合の処理
        if "raw_analysis" in results:
            raw_analysis = results["raw_analysis"]
            
            # 文字列内のJSONを検出して解析を試みる
            try:
                # {}で囲まれた部分を探す
                json_start = raw_analysis.find('{')
                json_end = raw_analysis.rfind('}') + 1
                
                if json_start >= 0 and json_end > json_start:
                    json_str = raw_analysis[json_start:json_end]
                    
                    try:
                        # JSONとして解析
                        parsed_json = json.loads(json_str)
                        
                        # この解析したJSONで元の結果を置き換え、以降の処理を続行
                        results = parsed_json
                        if os.environ.get("DEBUG") == "1":
                            console.print("[bold green]文字列内のJSONを正常に解析しました[/bold green]")
                    except json.JSONDecodeError:
                        # JSONとして解析できない場合はそのまま表示
                        console.print(Panel(raw_analysis, 
                                    title="[bold]可用性分析結果[/bold]", 
                                    border_style="blue"))
                        return
                else:
                    # JSONが見つからない場合はそのまま表示
                    console.print(Panel(raw_analysis, 
                                title="[bold]可用性分析結果[/bold]", 
                                border_style="blue"))
                    return
            except Exception as e:
                # エラーが発生した場合はそのまま表示
                if os.environ.get("DEBUG") == "1":
                    console.print(f"[bold red]解析エラー: {e}[/bold red]")
                console.print(Panel(raw_analysis, 
                            title="[bold]可用性分析結果[/bold]", 
                            border_style="blue"))
                return
                    
        if "error" in results:
            console.print(f"[bold red]分析エラー: {results['error']}[/bold red]")
            return
        
        # デバッグモードの場合のみ生のJSONを表示
        if os.environ.get("DEBUG") == "1":
            formatted_json = json.dumps(results, indent=2, ensure_ascii=False)
            console.print(Panel(Syntax(formatted_json, "json"), 
                             title="[bold]JSON結果[/bold]", 
                             border_style="blue"))
        
        # ヘッダーと可用性スコアの表示
        console.print("\n[bold white on blue]AWSリソース可用性分析結果[/bold white on blue]", justify="center")
        
        # 可用性スコアの表示
        score = results.get("availability_score", 0)
        score_color = "green" if score >= 80 else "yellow" if score >= 50 else "red"
        
        score_panel = Panel(
            f"[bold {score_color}]{score}/100[/bold {score_color}]",
            title="[bold]可用性スコア[/bold]",
            border_style=score_color,
            padding=(1, 2)
        )
        console.print(score_panel)
        
        # 主要なステータス項目をテーブルで表示
        status_table = Table(title="[bold]主要評価項目[/bold]", box=box.ROUNDED)
        status_table.add_column("評価項目", style="cyan", width=30)
        status_table.add_column("ステータス", style="bold", width=15)
        status_table.add_column("説明", style="green")
        
        # 評価項目のマッピング
        status_items = [
            ("multi_az_redundancy_configuration", "マルチAZ/冗長構成"),
            ("single_points_of_failure", "単一障害点"),
            ("scaling_configuration", "スケーリング構成"),
            ("backup_recovery_mechanisms", "バックアップと復旧"),
            ("timeout_retry_configurations", "タイムアウトとリトライ"),
        ]
        
        for key, display_name in status_items:
            if key in results:
                item = results[key]
                status = item.get("status", "UNKNOWN")
                status_style = {
                    "GOOD": "green",
                    "WARNING": "yellow",
                    "CRITICAL": "red",
                    "NOT_APPLICABLE": "blue"
                }.get(status, "white")
                
                status_table.add_row(
                    display_name,
                    f"[{status_style}]{status}[/{status_style}]",
                    item.get("description", "")
                )
        
        console.print(status_table)
        
        # 問題リソースを表示
        for key, display_name in status_items:
            if key in results and "resources" in results[key] and results[key]["resources"]:
                resources = results[key]["resources"]
                status = results[key].get("status", "UNKNOWN")
                
                if status in ["WARNING", "CRITICAL"]:
                    status_color = "yellow" if status == "WARNING" else "red"
                    resource_panel = Panel(
                        "\n".join([f"• {res}" for res in resources]),
                        title=f"[bold]{display_name}の問題リソース[/bold]",
                        border_style=status_color,
                        padding=(1, 2)
                    )
                    console.print(resource_panel)
        
        # 復旧目標の表示
        if "recovery_time_objectives" in results:
            rto_info = results["recovery_time_objectives"]
            rto_table = Table(title="[bold]復旧目標[/bold]", box=box.ROUNDED)
            rto_table.add_column("項目", style="cyan")
            rto_table.add_column("値", style="green")
            
            rto_table.add_row("推定RTO", rto_info.get("estimated_rto", "不明"))
            rto_table.add_row("推定RPO", rto_info.get("estimated_rpo", "不明"))
            
            status = rto_info.get("status", "UNKNOWN")
            status_style = {
                "GOOD": "green",
                "WARNING": "yellow",
                "CRITICAL": "red"
            }.get(status, "white")
            
            rto_table.add_row("ステータス", f"[{status_style}]{status}[/{status_style}]")
            rto_table.add_row("説明", rto_info.get("description", ""))
            
            console.print(rto_table)
        
        # サービスレベル目標の表示
        if "service_level_objectives" in results:
            slo_info = results["service_level_objectives"]
            slo_panel = Panel(
                f"推定可用性: [bold]{slo_info.get('estimated_availability', '不明')}[/bold]\n\n" +
                slo_info.get("description", ""),
                title="[bold]サービスレベル目標(SLO)[/bold]",
                border_style="blue",
                padding=(1, 2)
            )
            console.print(slo_panel)
        
        # コスト効率の表示
        if "cost_efficiency" in results:
            cost_info = results["cost_efficiency"]
            status = cost_info.get("status", "UNKNOWN")
            status_style = {
                "GOOD": "green",
                "WARNING": "yellow",
                "CRITICAL": "red"
            }.get(status, "white")
            
            cost_panel = Panel(
                f"ステータス: [{status_style}]{status}[/{status_style}]\n\n" +
                cost_info.get("description", ""),
                title="[bold]コスト効率評価[/bold]",
                border_style="cyan",
                padding=(1, 2)
            )
            console.print(cost_panel)
        
        # サービス固有の推奨事項
        if "service_specific_recommendations" in results:
            rec_data = results["service_specific_recommendations"]
            
            # サービスカテゴリごとにグループ化
            for category, category_data in rec_data.items():
                if category == "other" and isinstance(category_data, list) and category_data:
                    other_panel = Panel(
                        "\n".join([f"• {rec}" for rec in category_data]),
                        title="[bold]その他の推奨事項[/bold]",
                        border_style="blue",
                        padding=(1, 2)
                    )
                    console.print(other_panel)
                elif isinstance(category_data, dict):
                    for service, recommendations in category_data.items():
                        if recommendations:
                            service_display = {
                                "ec2": "EC2",
                                "rds": "RDS",
                                "lambda": "Lambda",
                                "dynamodb": "DynamoDB",
                                "elb": "ELB/ALB/NLB",
                                "api_gateway": "API Gateway",
                                "sqs": "SQS",
                                "sns": "SNS",
                                "s3": "S3",
                                # 他のサービスも必要に応じて追加
                            }.get(service, service.upper())
                            
                            service_panel = Panel(
                                "\n".join([f"• {rec}" for rec in recommendations]),
                                title=f"[bold]{service_display}の推奨事項[/bold]",
                                border_style="green",
                                padding=(1, 2)
                            )
                            console.print(service_panel)
        
        # 改善提案の表示
        if "improvement_suggestions" in results:
            suggestions = results["improvement_suggestions"]
            if suggestions:
                # 優先度でソート
                priority_order = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
                sorted_suggestions = sorted(
                    suggestions, 
                    key=lambda x: priority_order.get(x.get("priority", "LOW"), 3)
                )
                
                suggestion_table = Table(title="[bold]改善提案[/bold]", box=box.ROUNDED)
                suggestion_table.add_column("優先度", style="bold", width=10)
                suggestion_table.add_column("提案内容", style="cyan")
                suggestion_table.add_column("コスト影響", style="yellow", width=12)
                suggestion_table.add_column("可用性影響", style="green", width=12)
                
                for suggestion in sorted_suggestions:
                    priority = suggestion.get("priority", "LOW")
                    priority_style = {
                        "HIGH": "red",
                        "MEDIUM": "yellow",
                        "LOW": "green"
                    }.get(priority, "white")
                    
                    cost_impact = suggestion.get("cost_impact", "LOW")
                    cost_style = {
                        "HIGH": "red",
                        "MEDIUM": "yellow",
                        "LOW": "green"
                    }.get(cost_impact, "white")
                    
                    avail_impact = suggestion.get("availability_impact", "LOW")
                    avail_style = {
                        "HIGH": "green",
                        "MEDIUM": "yellow",
                        "LOW": "red"
                    }.get(avail_impact, "white")
                    
                    suggestion_table.add_row(
                        f"[{priority_style}]{priority}[/{priority_style}]",
                        suggestion.get("description", ""),
                        f"[{cost_style}]{cost_impact}[/{cost_style}]",
                        f"[{avail_style}]{avail_impact}[/{avail_style}]"
                    )
                
                console.print(suggestion_table)
                
                # 実装例を表示
                for i, suggestion in enumerate(sorted_suggestions):
                    if "implementation_example" in suggestion and suggestion["implementation_example"]:
                        impl_panel = Panel(
                            Syntax(suggestion["implementation_example"], "terraform", theme="monokai"),
                            title=f"[bold]実装例: {suggestion.get('description', f'提案 {i+1}')}[/bold]",
                            border_style="cyan",
                            padding=(1, 2)
                        )
                        console.print(impl_panel)
        
        # 総評の表示
        if "overall_assessment" in results:
            assessment = results["overall_assessment"]
            if assessment:
                assessment_panel = Panel(
                    Text(assessment, style="bold white"),
                    title="[bold]総合評価[/bold]",
                    border_style="blue",
                    padding=(1, 2)
                )
                console.print(assessment_panel)

    def export_as_html(self, results: Dict[str, Any], output_path: str) -> None:
        """
        分析結果をHTMLファイルとしてエクスポート
        
        Args:
            results: 分析結果
            output_path: 出力先HTMLファイルのパス
        """
        # まず結果がJSONオブジェクトを含む文字列である場合の処理
        if "raw_analysis" in results:
            raw_analysis = results["raw_analysis"]
            
            # 文字列内のJSONを検出して解析を試みる
            try:
                # {}で囲まれた部分を探す
                json_start = raw_analysis.find('{')
                json_end = raw_analysis.rfind('}') + 1
                
                if json_start >= 0 and json_end > json_start:
                    json_str = raw_analysis[json_start:json_end]
                    
                    try:
                        # JSONとして解析
                        parsed_json = json.loads(json_str)
                        
                        # この解析したJSONで元の結果を置き換え、以降の処理を続行
                        results = parsed_json
                        if os.environ.get("DEBUG") == "1":
                            console.print("[bold green]文字列内のJSONを正常に解析しました[/bold green]")
                    except json.JSONDecodeError:
                        # JSONとして解析できない場合はそのままHTMLに変換
                        html_content = self._generate_raw_html(raw_analysis)
                        with open(output_path, 'w', encoding='utf-8') as f:
                            f.write(html_content)
                        console.print(f"[bold green]HTMLファイルを生成しました: {output_path}[/bold green]")
                        return
                else:
                    # JSONが見つからない場合はそのままHTMLに変換
                    html_content = self._generate_raw_html(raw_analysis)
                    with open(output_path, 'w', encoding='utf-8') as f:
                        f.write(html_content)
                    console.print(f"[bold green]HTMLファイルを生成しました: {output_path}[/bold green]")
                    return
            except Exception as e:
                # エラーが発生した場合はそのままHTMLに変換
                if os.environ.get("DEBUG") == "1":
                    console.print(f"[bold red]解析エラー: {e}[/bold red]")
                html_content = self._generate_raw_html(raw_analysis)
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(html_content)
                console.print(f"[bold green]HTMLファイルを生成しました: {output_path}[/bold green]")
                return
        
        if "error" in results:
            html_content = self._generate_error_html(results['error'])
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            console.print(f"[bold green]HTMLファイルを生成しました: {output_path}[/bold green]")
            return
        
        # 構造化されたデータからHTMLを生成
        html_content = self._generate_structured_html(results)
        
        # HTMLファイルとして保存
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        console.print(f"[bold green]HTMLファイルを生成しました: {output_path}[/bold green]")
    
    def _generate_raw_html(self, raw_content: str) -> str:
        """
        生のテキストコンテンツをHTMLに変換
        
        Args:
            raw_content: 生のテキストコンテンツ
            
        Returns:
            HTML形式のコンテンツ
        """
        html = f"""<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AWS可用性分析結果</title>
    <style>
        body {{
            font-family: 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f7fa;
        }}
        header {{
            background: linear-gradient(135deg, #0033A0, #007bff);
            color: white;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 30px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            text-align: center;
        }}
        h1 {{
            margin: 0;
            font-size: 28px;
        }}
        .content-panel {{
            background-color: #fff;
            border-radius: 8px;
            padding: 25px;
            margin-bottom: 30px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            border-left: 5px solid #007bff;
            white-space: pre-wrap;
        }}
        footer {{
            text-align: center;
            margin-top: 30px;
            color: #777;
            font-size: 14px;
        }}
    </style>
</head>
<body>
    <header>
        <h1>AWS可用性分析結果</h1>
    </header>
    
    <div class="content-panel">
        {raw_content.replace('<', '&lt;').replace('>', '&gt;')}
    </div>
    
    <footer>
        <p>生成日時: {time.strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p>AWS可用性チェッカーによって生成されました</p>
    </footer>
</body>
</html>
"""
        return html
    
    def _generate_error_html(self, error_message: str) -> str:
        """
        エラーメッセージをHTMLに変換
        
        Args:
            error_message: エラーメッセージ
            
        Returns:
            HTML形式のエラーメッセージ
        """
        html = f"""<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AWS可用性分析エラー</title>
    <style>
        body {{
            font-family: 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f7fa;
        }}
        header {{
            background: linear-gradient(135deg, #d9534f, #c9302c);
            color: white;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 30px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            text-align: center;
        }}
        h1 {{
            margin: 0;
            font-size: 28px;
        }}
        .error-panel {{
            background-color: #fff;
            border-radius: 8px;
            padding: 25px;
            margin-bottom: 30px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            border-left: 5px solid #d9534f;
        }}
        footer {{
            text-align: center;
            margin-top: 30px;
            color: #777;
            font-size: 14px;
        }}
    </style>
</head>
<body>
    <header>
        <h1>AWS可用性分析エラー</h1>
    </header>
    
    <div class="error-panel">
        <h2>分析中にエラーが発生しました</h2>
        <p>{error_message}</p>
    </div>
    
    <footer>
        <p>生成日時: {time.strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p>AWS可用性チェッカーによって生成されました</p>
    </footer>
</body>
</html>
"""
        return html
    
    def _generate_structured_html(self, results: Dict[str, Any]) -> str:
        """
        構造化されたデータからHTMLを生成
        
        Args:
            results: 構造化された分析結果
            
        Returns:
            HTML形式のコンテンツ
        """
        # 可用性スコア
        score = results.get("availability_score", 0)
        score_color = "#4caf50" if score >= 80 else "#ff9800" if score >= 50 else "#f44336"
        
        # 主要評価項目の設定
        status_items = [
            ("multi_az_redundancy_configuration", "マルチAZ/冗長構成"),
            ("single_points_of_failure", "単一障害点"),
            ("scaling_configuration", "スケーリング構成"),
            ("backup_recovery_mechanisms", "バックアップと復旧"),
            ("timeout_retry_configurations", "タイムアウトとリトライ"),
        ]
        
        status_html = ""
        for key, display_name in status_items:
            if key in results:
                item = results[key]
                status = item.get("status", "UNKNOWN")
                status_colors = {
                    "GOOD": "#4caf50",
                    "WARNING": "#ff9800",
                    "CRITICAL": "#f44336",
                    "NOT_APPLICABLE": "#2196f3"
                }
                status_color = status_colors.get(status, "#9e9e9e")
                
                status_html += f"""
                <tr>
                    <td>{display_name}</td>
                    <td><span class="status-badge" style="background-color: {status_color};">{status}</span></td>
                    <td>{item.get("description", "")}</td>
                </tr>
                """
        
        # 問題リソースのHTML生成
        problem_resources_html = ""
        for key, display_name in status_items:
            if key in results and "resources" in results[key] and results[key]["resources"]:
                resources = results[key]["resources"]
                status = results[key].get("status", "UNKNOWN")
                
                if status in ["WARNING", "CRITICAL"]:
                    status_color = "#ff9800" if status == "WARNING" else "#f44336"
                    
                    problem_resources_html += f"""
                    <div class="card" style="border-left-color: {status_color};">
                        <h3>{display_name}の問題リソース</h3>
                        <ul>
                    """
                    
                    for res in resources:
                        problem_resources_html += f"<li>{res}</li>\n"
                    
                    problem_resources_html += """
                        </ul>
                    </div>
                    """
        
        # 復旧目標のHTML
        rto_html = ""
        if "recovery_time_objectives" in results:
            rto_info = results["recovery_time_objectives"]
            status = rto_info.get("status", "UNKNOWN")
            status_colors = {
                "GOOD": "#4caf50",
                "WARNING": "#ff9800",
                "CRITICAL": "#f44336"
            }
            status_color = status_colors.get(status, "#9e9e9e")
            
            rto_html = f"""
            <div class="card">
                <h3>復旧目標（RTO/RPO）</h3>
                <table class="info-table">
                    <tr>
                        <td>推定RTO</td>
                        <td>{rto_info.get("estimated_rto", "不明")}</td>
                    </tr>
                    <tr>
                        <td>推定RPO</td>
                        <td>{rto_info.get("estimated_rpo", "不明")}</td>
                    </tr>
                    <tr>
                        <td>ステータス</td>
                        <td><span class="status-badge" style="background-color: {status_color};">{status}</span></td>
                    </tr>
                    <tr>
                        <td>説明</td>
                        <td>{rto_info.get("description", "")}</td>
                    </tr>
                </table>
            </div>
            """
        
        # サービスレベル目標のHTML
        slo_html = ""
        if "service_level_objectives" in results:
            slo_info = results["service_level_objectives"]
            slo_html = f"""
            <div class="card">
                <h3>サービスレベル目標（SLO）</h3>
                <p><strong>推定可用性:</strong> {slo_info.get("estimated_availability", "不明")}</p>
                <p>{slo_info.get("description", "")}</p>
            </div>
            """
        
        # コスト効率のHTML
        cost_html = ""
        if "cost_efficiency" in results:
            cost_info = results["cost_efficiency"]
            status = cost_info.get("status", "UNKNOWN")
            status_colors = {
                "GOOD": "#4caf50",
                "WARNING": "#ff9800",
                "CRITICAL": "#f44336"
            }
            status_color = status_colors.get(status, "#9e9e9e")
            
            cost_html = f"""
            <div class="card">
                <h3>コスト効率評価</h3>
                <p><strong>ステータス:</strong> <span class="status-badge" style="background-color: {status_color};">{status}</span></p>
                <p>{cost_info.get("description", "")}</p>
            </div>
            """
        
        # サービス固有の推奨事項HTML
        recommendations_html = ""
        if "service_specific_recommendations" in results:
            rec_data = results["service_specific_recommendations"]
            
            for category, category_data in rec_data.items():
                if category == "other" and isinstance(category_data, list) and category_data:
                    recommendations_html += """
                    <div class="card">
                        <h3>その他の推奨事項</h3>
                        <ul>
                    """
                    
                    for rec in category_data:
                        recommendations_html += f"<li>{rec}</li>\n"
                    
                    recommendations_html += """
                        </ul>
                    </div>
                    """
                elif isinstance(category_data, dict):
                    for service, service_recommendations in category_data.items():
                        if service_recommendations:
                            service_display = {
                                "ec2": "EC2",
                                "rds": "RDS",
                                "lambda": "Lambda",
                                "dynamodb": "DynamoDB",
                                "elb": "ELB/ALB/NLB",
                                "api_gateway": "API Gateway",
                                "sqs": "SQS",
                                "sns": "SNS",
                                "s3": "S3",
                                # 他のサービスも必要に応じて追加
                            }.get(service, service.upper())
                            
                            recommendations_html += f"""
                            <div class="card">
                                <h3>{service_display}の推奨事項</h3>
                                <ul>
                            """
                            
                            for rec in service_recommendations:
                                recommendations_html += f"<li>{rec}</li>\n"
                            
                            recommendations_html += """
                                </ul>
                            </div>
                            """
        
        # 改善提案のHTML
        improvements_html = ""
        if "improvement_suggestions" in results:
            suggestions = results["improvement_suggestions"]
            if suggestions:
                # 優先度でソート
                priority_order = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
                sorted_suggestions = sorted(
                    suggestions, 
                    key=lambda x: priority_order.get(x.get("priority", "LOW"), 3)
                )
                
                improvements_html += """
                <div class="card">
                    <h3>改善提案</h3>
                    <table class="suggestions-table">
                        <thead>
                            <tr>
                                <th>優先度</th>
                                <th>提案内容</th>
                                <th>コスト影響</th>
                                <th>可用性影響</th>
                            </tr>
                        </thead>
                        <tbody>
                """
                
                for suggestion in sorted_suggestions:
                    priority = suggestion.get("priority", "LOW")
                    priority_colors = {
                        "HIGH": "#f44336",
                        "MEDIUM": "#ff9800",
                        "LOW": "#4caf50"
                    }
                    priority_color = priority_colors.get(priority, "#9e9e9e")
                    
                    cost_impact = suggestion.get("cost_impact", "LOW")
                    cost_colors = {
                        "HIGH": "#f44336",
                        "MEDIUM": "#ff9800",
                        "LOW": "#4caf50"
                    }
                    cost_color = cost_colors.get(cost_impact, "#9e9e9e")
                    
                    avail_impact = suggestion.get("availability_impact", "LOW")
                    avail_colors = {
                        "HIGH": "#4caf50",
                        "MEDIUM": "#ff9800",
                        "LOW": "#f44336"
                    }
                    avail_color = avail_colors.get(avail_impact, "#9e9e9e")
                    
                    improvements_html += f"""
                    <tr>
                        <td><span class="status-badge" style="background-color: {priority_color};">{priority}</span></td>
                        <td>{suggestion.get("description", "")}</td>
                        <td><span class="status-badge" style="background-color: {cost_color};">{cost_impact}</span></td>
                        <td><span class="status-badge" style="background-color: {avail_color};">{avail_impact}</span></td>
                    </tr>
                    """
                
                improvements_html += """
                        </tbody>
                    </table>
                </div>
                """
                
                # 実装例
                for i, suggestion in enumerate(sorted_suggestions):
                    if "implementation_example" in suggestion and suggestion["implementation_example"]:
                        implementation = suggestion["implementation_example"].replace('<', '&lt;').replace('>', '&gt;')
                        improvements_html += f"""
                        <div class="card">
                            <h3>実装例: {suggestion.get('description', f'提案 {i+1}')}</h3>
                            <pre class="code-block">{implementation}</pre>
                        </div>
                        """
        
        # 総評のHTML
        assessment_html = ""
        if "overall_assessment" in results:
            assessment = results.get("overall_assessment", "")
            if assessment:
                assessment_html = f"""
                <div class="card">
                    <h3>総合評価</h3>
                    <p>{assessment}</p>
                </div>
                """
        
        # 最終的なHTML生成
        html = f"""<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AWS可用性分析結果</title>
    <style>
        body {{
            font-family: 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f7fa;
        }}
        header {{
            background: linear-gradient(135deg, #0033A0, #007bff);
            color: white;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 30px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            text-align: center;
        }}
        h1 {{
            margin: 0;
            font-size: 28px;
        }}
        h2 {{
            color: #007bff;
            border-bottom: 2px solid #eee;
            padding-bottom: 10px;
            margin-top: 40px;
        }}
        h3 {{
            color: #333;
            margin-top: 0;
            margin-bottom: 15px;
        }}
        .dashboard {{
            display: flex;
            flex-wrap: wrap;
            gap: 20px;
            margin-bottom: 30px;
        }}
        .score-card {{
            background-color: white;
            border-radius: 8px;
            padding: 20px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            flex: 1;
            min-width: 250px;
            text-align: center;
        }}
        .score {{
            font-size: 48px;
            font-weight: bold;
            color: {score_color};
            margin: 10px 0;
        }}
        .card {{
            background-color: white;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            border-left: 5px solid #007bff;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 15px;
        }}
        .status-table {{
            margin-top: 20px;
        }}
        .status-table th, .status-table td {{
            padding: 12px 15px;
            border-bottom: 1px solid #eee;
            text-align: left;
        }}
        .status-table th {{
            background-color: #f8f9fa;
            font-weight: 600;
        }}
        .status-badge {{
            display: inline-block;
            padding: 4px 8px;
            border-radius: 4px;
            color: white;
            font-weight: bold;
            font-size: 12px;
        }}
        .info-table td {{
            padding: 8px 10px;
            border-bottom: 1px solid #eee;
        }}
        .info-table tr td:first-child {{
            font-weight: bold;
            width: 150px;
        }}
        .suggestions-table {{
            width: 100%;
            border-collapse: collapse;
        }}
        .suggestions-table th, .suggestions-table td {{
            padding: 12px 15px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        .suggestions-table th {{
            background-color: #f8f9fa;
            font-weight: 600;
        }}
        .code-block {{
            background-color: #272822;
            color: #f8f8f2;
            padding: 15px;
            border-radius: 4px;
            overflow-x: auto;
            font-family: 'Courier New', monospace;
            white-space: pre-wrap;
        }}
        footer {{
            text-align: center;
            margin-top: 30px;
            color: #777;
            font-size: 14px;
            padding-top: 20px;
            border-top: 1px solid #eee;
        }}
        @media (max-width: 768px) {{
            .dashboard {{
                flex-direction: column;
            }}
        }}
    </style>
</head>
<body>
    <header>
        <h1>AWS可用性分析結果</h1>
    </header>
    
    <div class="dashboard">
        <div class="score-card">
            <h3>可用性スコア</h3>
            <div class="score">{score}/100</div>
        </div>
    </div>
    
    <h2>主要評価項目</h2>
    <div class="card">
        <table class="status-table">
            <thead>
                <tr>
                    <th>評価項目</th>
                    <th>ステータス</th>
                    <th>説明</th>
                </tr>
            </thead>
            <tbody>
                {status_html}
            </tbody>
        </table>
    </div>
    
    {problem_resources_html}
    
    <h2>復旧目標と可用性</h2>
    {rto_html}
    {slo_html}
    
    <h2>コスト効率性</h2>
    {cost_html}
    
    <h2>サービス固有の推奨事項</h2>
    {recommendations_html}
    
    <h2>改善提案</h2>
    {improvements_html}
    
    <h2>総合評価</h2>
    {assessment_html}
    
    <footer>
        <p>生成日時: {time.strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p>AWS可用性チェッカーによって生成されました</p>
    </footer>
</body>
</html>
"""
        return html

def main():
    """メイン関数"""
    parser = argparse.ArgumentParser(description='AWSリソースの可用性チェッカー')
    parser.add_argument('json_file', help='分析対象のTerraform JSONファイル')
    parser.add_argument('--region', help='AWS リージョン', default=os.environ.get('AWS_REGION', 'ap-northeast-1'))
    parser.add_argument('--model', help='Bedrock モデルID', default='anthropic.claude-3-5-sonnet-20240620-v1:0')
    parser.add_argument('--output', help='結果を保存するJSONファイル')
    parser.add_argument('--html', help='結果をHTMLファイルとして出力するパス')
    parser.add_argument('--debug', action='store_true', help='デバッグモードを有効化', default=True)
    parser.add_argument('--no-debug', dest='debug', action='store_false', help='デバッグモードを無効化')
    parser.add_argument('--example', action='store_true', help='使用例を表示')
    
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
    
    # デバッグモードの設定
    if args.debug:
        os.environ["DEBUG"] = "1"
        console.print("[dim]デバッグモードが有効です[/dim]")
    
    # AWS リージョンの設定
    os.environ['AWS_REGION'] = args.region
    
    # ロゴ表示
    console.print("\n[bold blue]AWSリソース可用性チェッカー[/bold blue]")
    console.print("[dim]Terraform JSONをBedrockで解析し、可用性の問題を特定します[/dim]\n")
    
    # チェッカーの初期化
    console.print("[bold blue]ステップ1: 初期化[/bold blue]")
    checker = AvailabilityChecker(model_id=args.model)
    console.print(f"使用モデル: [bold]{args.model}[/bold]")
    
    # JSON読み込み
    console.print(f"Terraform JSONファイルを読み込み中: [bold]{args.json_file}[/bold]")
    terraform_data = checker.load_terraform_json(args.json_file)
    resource_count = sum(len(resources) if isinstance(resources, dict) else len(resources) if isinstance(resources, list) else 1 
                           for resources in terraform_data.values())
    
    # 分析
    start_time = time.time()
    results = checker.analyze_with_bedrock(terraform_data)
    elapsed_time = time.time() - start_time
    
    # 結果表示
    checker.print_analysis_results(results)
    
    # 実行時間の表示
    console.print(f"\n総実行時間: [bold green]{elapsed_time:.1f}秒[/bold green]")
    
    # 結果をJSONファイルとして保存（オプション）
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        console.print(f"[bold green]結果をJSONファイルに保存しました: {args.output}[/bold green]")
    
    # 結果をHTMLファイルとして保存（オプション）
    if args.html:
        checker.export_as_html(results, args.html)
    
    return results

def print_help_examples():
    """ヘルプと使用例を表示"""
    examples = """
=== 使用例 ===

基本的な使い方:
    python availability_checker.py terraform_plan.json

結果をJSONファイルに保存:
    python availability_checker.py terraform_plan.json --output results.json

結果をHTMLファイルに出力:
    python availability_checker.py terraform_plan.json --html results.html

JSONとHTMLの両方を出力:
    python availability_checker.py terraform_plan.json --output results.json --html results.html

異なるAWSリージョンを指定:
    python availability_checker.py terraform_plan.json --region us-east-1
"""
    console.print(Panel(examples, title="[bold]コマンドライン使用例[/bold]", border_style="cyan"))

if __name__ == "__main__":
    main() 