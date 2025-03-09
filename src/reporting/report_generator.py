"""
分析結果のレポートを生成するモジュール
"""
import os
import json
from typing import Dict, Any, Optional, List

class ReportGenerator:
    """
    分析結果からレポートを生成するクラス
    """
    
    def __init__(self, output_dir: str = "output"):
        """
        ReportGeneratorの初期化
        
        Args:
            output_dir: 出力ディレクトリのパス
        """
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def save_json_report(self, results: Dict[str, Any], output_file: str) -> str:
        """
        分析結果をJSONファイルとして保存
        
        Args:
            results: 保存する分析結果
            output_file: 出力ファイルのパス
            
        Returns:
            保存したファイルのフルパス
        """
        # 出力ファイルパスの調整
        if not os.path.isabs(output_file):
            output_file = os.path.join(self.output_dir, os.path.basename(output_file))
            
        # JSONファイルとして保存
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
            
        return output_file
    
    def export_as_html(self, results: Dict[str, Any], output_file: str) -> str:
        """
        分析結果をHTMLファイルとして出力
        
        Args:
            results: HTMLに変換する分析結果
            output_file: 出力HTMLファイルのパス
            
        Returns:
            保存したファイルのフルパス
        """
        # 出力ファイルパスの調整
        if not os.path.isabs(output_file):
            output_file = os.path.join(self.output_dir, os.path.basename(output_file))
        
        # HTML生成
        html_content = self._generate_html(results)
        
        # ファイルに保存
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return output_file
    
    def _generate_html(self, results: Dict[str, Any]) -> str:
        """
        分析結果からHTMLを生成
        
        Args:
            results: HTML形式に変換する分析結果
            
        Returns:
            生成されたHTML文字列
        """
        # 解析に失敗した場合
        if "error" in results:
            return self._generate_error_html(results["error"])
        
        # 生のテキスト分析が含まれている場合
        if "raw_analysis" in results:
            return self._generate_raw_analysis_html(results["raw_analysis"])
        
        # ヘッダー部分の生成
        html = """<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AWS Terraform可用性分析レポート</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        header {
            background-color: #0066cc;
            color: white;
            padding: 20px;
            border-radius: 5px;
            margin-bottom: 20px;
        }
        h1, h2, h3 {
            margin-top: 0;
        }
        .score-container {
            text-align: center;
            margin: 30px 0;
        }
        .score {
            font-size: 48px;
            font-weight: bold;
        }
        .score-high {
            color: #28a745;
        }
        .score-medium {
            color: #ffc107;
        }
        .score-low {
            color: #dc3545;
        }
        .overview {
            background-color: #f8f9fa;
            border-left: 5px solid #0066cc;
            padding: 15px;
            margin-bottom: 30px;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 30px;
        }
        th, td {
            border: 1px solid #ddd;
            padding: 12px;
            text-align: left;
        }
        th {
            background-color: #f2f2f2;
        }
        tr:nth-child(even) {
            background-color: #f9f9f9;
        }
        .severity-high, .priority-high {
            color: #dc3545;
            font-weight: bold;
        }
        .severity-medium, .priority-medium {
            color: #ffc107;
            font-weight: bold;
        }
        .severity-low, .priority-low {
            color: #28a745;
            font-weight: bold;
        }
        .recommendation {
            background-color: #f8f9fa;
            border: 1px solid #ddd;
            border-radius: 5px;
            padding: 15px;
            margin-bottom: 20px;
        }
        .recommendation h3 {
            margin-top: 0;
            border-bottom: 2px solid #0066cc;
            padding-bottom: 10px;
        }
        pre {
            background-color: #f5f5f5;
            padding: 15px;
            border-radius: 5px;
            overflow-x: auto;
        }
        footer {
            margin-top: 50px;
            text-align: center;
            color: #777;
            font-size: 0.9em;
        }
    </style>
</head>
<body>
    <header>
        <h1>AWS Terraform可用性分析レポート</h1>
        <p>AWS Well-Architected Frameworkの信頼性の柱に基づく評価</p>
    </header>
"""
        
        # 可用性スコアの生成
        if "availability_score" in results:
            score = results["availability_score"]
            score_class = "score-high" if score >= 80 else "score-medium" if score >= 50 else "score-low"
            
            html += f"""
    <div class="score-container">
        <h2>可用性スコア</h2>
        <div class="score {score_class}">{score}/100</div>
    </div>
"""
        
        # 概要の生成
        if "overview" in results:
            html += f"""
    <section>
        <h2>概要</h2>
        <div class="overview">
            <p>{results["overview"]}</p>
        </div>
    </section>
"""
        
        # 問題点テーブルの生成
        if "findings" in results and results["findings"]:
            html += self._generate_findings_html(results["findings"])
        
        # 推奨事項の生成
        if "recommendations" in results and results["recommendations"]:
            html += self._generate_recommendations_html(results["recommendations"])
        
        # フッターと終了タグの生成
        html += """
    <footer>
        <p>レポート生成: AWS Terraform可用性チェックツール</p>
    </footer>
</body>
</html>
"""
        
        return html
    
    def _generate_findings_html(self, findings: List[Dict[str, Any]]) -> str:
        """
        問題点のHTMLテーブルを生成
        
        Args:
            findings: 問題点のリスト
            
        Returns:
            生成されたHTML文字列
        """
        html = """
    <section>
        <h2>検出された問題点</h2>
        <table>
            <thead>
                <tr>
                    <th>カテゴリ</th>
                    <th>重要度</th>
                    <th>説明</th>
                    <th>推奨対応</th>
                </tr>
            </thead>
            <tbody>
"""
        
        for finding in findings:
            severity = finding.get("severity", "")
            severity_class = self._get_severity_class(severity)
            
            html += f"""
                <tr>
                    <td>{finding.get("category", "")}</td>
                    <td class="{severity_class}">{severity}</td>
                    <td>{finding.get("description", "")}</td>
                    <td>{finding.get("recommendation", "")}</td>
                </tr>
"""
        
        html += """
            </tbody>
        </table>
    </section>
"""
        
        return html
    
    def _generate_recommendations_html(self, recommendations: List[Dict[str, Any]]) -> str:
        """
        推奨事項のHTMLを生成
        
        Args:
            recommendations: 推奨事項のリスト
            
        Returns:
            生成されたHTML文字列
        """
        html = """
    <section>
        <h2>改善推奨事項</h2>
"""
        
        for i, rec in enumerate(recommendations, 1):
            priority = rec.get("priority", "")
            priority_class = self._get_severity_class(priority)
            
            html += f"""
        <div class="recommendation">
            <h3>推奨事項 {i}: <span class="{priority_class}">優先度: {priority}</span></h3>
            <p>{rec.get("description", "")}</p>
"""
            
            if "terraform_example" in rec and rec["terraform_example"]:
                html += f"""
            <h4>実装例:</h4>
            <pre><code>{rec["terraform_example"]}</code></pre>
"""
            
            html += """
        </div>
"""
        
        html += """
    </section>
"""
        
        return html
    
    def _generate_error_html(self, error: str) -> str:
        """
        エラーメッセージのHTMLを生成
        
        Args:
            error: エラーメッセージ
            
        Returns:
            生成されたHTML文字列
        """
        return f"""<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AWS Terraform可用性分析エラー</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }}
        .error {{
            background-color: #f8d7da;
            border: 1px solid #f5c6cb;
            color: #721c24;
            padding: 20px;
            border-radius: 5px;
            margin: 20px 0;
        }}
    </style>
</head>
<body>
    <h1>AWS Terraform可用性分析エラー</h1>
    <div class="error">
        <h2>分析実行中にエラーが発生しました</h2>
        <p>{error}</p>
    </div>
</body>
</html>
"""
    
    def _generate_raw_analysis_html(self, raw_analysis: str) -> str:
        """
        生のテキスト分析のHTMLを生成
        
        Args:
            raw_analysis: 生の分析テキスト
            
        Returns:
            生成されたHTML文字列
        """
        return f"""<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AWS Terraform可用性分析レポート</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }}
        .raw-analysis {{
            white-space: pre-wrap;
            background-color: #f8f9fa;
            border: 1px solid #ddd;
            padding: 20px;
            border-radius: 5px;
        }}
    </style>
</head>
<body>
    <h1>AWS Terraform可用性分析レポート</h1>
    <div class="raw-analysis">
        {raw_analysis}
    </div>
</body>
</html>
"""
    
    def _get_severity_class(self, severity: str) -> str:
        """
        重要度に対応するCSSクラスを取得
        
        Args:
            severity: 重要度（高/中/低またはhigh/medium/low）
            
        Returns:
            対応するCSSクラス
        """
        severity = severity.lower()
        if severity in ["高", "high"]:
            return "severity-high"
        elif severity in ["中", "medium"]:
            return "severity-medium"
        elif severity in ["低", "low"]:
            return "severity-low"
        return "" 