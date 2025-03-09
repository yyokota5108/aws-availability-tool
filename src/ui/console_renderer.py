"""
リッチコンソールに結果を表示するためのモジュール
"""

from typing import Dict, Any, List
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich import box


class ConsoleRenderer:
    """
    分析結果をコンソールに表示するクラス
    """

    def __init__(self) -> None:
        """
        ConsoleRendererの初期化
        """
        self.console = Console()

    def print_analysis_results(self, results: Dict[str, Any]) -> None:
        """
        分析結果をコンソールに表示

        Args:
            results: 表示する分析結果
        """
        # 解析に失敗した場合の処理
        if "error" in results:
            self.console.print(
                f"[bold red]エラー: 分析に失敗しました: {results['error']}[/bold red]"
            )
            return

        # 生のテキスト分析が含まれている場合
        if "raw_analysis" in results:
            self.console.print(
                Panel(
                    results["raw_analysis"],
                    title="[bold]分析結果（構造化されていません）[/bold]",
                    border_style="yellow",
                )
            )
            return

        # 概要
        if "overview" in results:
            self.console.print(
                Panel(results["overview"], title="[bold]概要[/bold]", border_style="blue")
            )

        # 可用性スコア
        if "availability_score" in results:
            score = results["availability_score"]
            color = "green" if score >= 80 else "yellow" if score >= 50 else "red"
            self.console.print(
                f"\n[bold]可用性スコア:[/bold] [bold {color}]{score}/100[/bold {color}]"
            )
            
        # 推奨SLO（存在する場合）
        if "suggested_slo" in results:
            self._print_suggested_slo(results["suggested_slo"])

        # 問題点
        if "findings" in results and results["findings"]:
            self._print_findings(results["findings"])

        # 推奨事項
        if "recommendations" in results and results["recommendations"]:
            self._print_recommendations(results["recommendations"])

    def _print_suggested_slo(self, slo: Dict[str, Any]) -> None:
        """
        推奨SLOを表示
        
        Args:
            slo: SLO情報の辞書
        """
        if "availability_target" in slo:
            self.console.print("\n[bold]推奨SLO（サービスレベル目標）:[/bold]")
            self.console.print(
                f"可用性目標: [bold cyan]{slo.get('availability_target', '')}[/bold cyan]"
            )
            if "rationale" in slo:
                self.console.print(f"根拠: {slo.get('rationale', '')}")

    def _print_findings(self, findings: List[Dict[str, Any]]) -> None:
        """
        問題点をテーブル形式で表示

        Args:
            findings: 問題点のリスト
        """
        self.console.print("\n[bold]検出された問題点:[/bold]")

        table = Table(box=box.ROUNDED)
        table.add_column("カテゴリ", style="cyan")
        table.add_column("重要度", style="bold")
        table.add_column("説明", style="white")
        table.add_column("推奨対応", style="green")
        table.add_column("実装難易度", style="yellow")
        table.add_column("リスク影響度", style="red")

        for finding in findings:
            severity = finding.get("severity", "")
            severity_style = self._get_severity_style(severity)
            
            effort = finding.get("effort", "")
            effort_style = self._get_severity_style(effort)
            
            risk_impact = finding.get("risk_impact", "")
            risk_style = self._get_severity_style(risk_impact)

            table.add_row(
                finding.get("category", ""),
                Text(severity, style=severity_style),
                finding.get("description", ""),
                finding.get("recommendation", ""),
                Text(effort, style=effort_style) if effort else "",
                Text(risk_impact, style=risk_style) if risk_impact else "",
            )

        self.console.print(table)

    def _print_recommendations(self, recommendations: List[Dict[str, Any]]) -> None:
        """
        推奨事項をパネル形式で表示

        Args:
            recommendations: 推奨事項のリスト
        """
        self.console.print("\n[bold]改善推奨事項:[/bold]")

        for i, rec in enumerate(recommendations, 1):
            priority = rec.get("priority", "")
            priority_style = self._get_severity_style(priority)
            
            effort = rec.get("effort", "")
            effort_text = f"[yellow]実装難易度: {effort}[/yellow]" if effort else ""
            
            cost_impact = rec.get("cost_impact", "")
            cost_text = f"[blue]コスト影響: {cost_impact}[/blue]" if cost_impact else ""
            
            metadata = " | ".join(filter(None, [
                f"[{priority_style}]優先度: {priority}[/{priority_style}]",
                effort_text,
                cost_text
            ]))

            title = f"[bold]推奨事項 {i}[/bold]" + (f": {metadata}" if metadata else "")
            content = rec.get("description", "")

            self.console.print(Panel(content, title=title, border_style="green"))

    def _get_severity_style(self, severity: str) -> str:
        """
        重要度に対応するスタイルを取得

        Args:
            severity: 重要度（高/中/低またはhigh/medium/low）

        Returns:
            対応するスタイル
        """
        severity = severity.lower()
        if severity in ["高", "high"]:
            return "bold red"
        elif severity in ["中", "medium"]:
            return "bold yellow"
        elif severity in ["低", "low"]:
            return "bold green"
        return "bold"
