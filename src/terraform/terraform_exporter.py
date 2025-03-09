"""
Terraformコードを解析してJSONに変換するモジュール
"""
import os
import json
from typing import Dict, Any, Tuple, Optional

class TerraformExporter:
    """
    Terraformコードを解析しJSONに変換するクラス
    """
    
    def __init__(self, output_dir: str = "output"):
        """
        TerraformExporterの初期化
        
        Args:
            output_dir: 出力ディレクトリのパス
        """
        self.output_dir = output_dir
        self._ensure_output_directory()
    
    def _ensure_output_directory(self) -> str:
        """
        出力ディレクトリが存在することを確認し、なければ作成する
        
        Returns:
            出力ディレクトリのパス
        """
        os.makedirs(self.output_dir, exist_ok=True)
        return self.output_dir
    
    def export_to_json(self, terraform_path: str, output_file: Optional[str] = None) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """
        Terraformコードを解析し、結果をJSONファイルとして出力する
        
        Args:
            terraform_path: Terraformプロジェクトのパス
            output_file: 出力JSONファイルのパス（指定がなければ自動生成）
            
        Returns:
            (解析結果のデータ, 出力ファイルのパス)のタプル
        """
        try:
            # Terraformライブラリの動的インポート
            # インストールされていない場合の処理のため
            try:
                from tfparse import load_from_path
            except ImportError:
                print("Error: tfparseライブラリがインストールされていません。")
                print("pip install tfparseを実行してインストールしてください。")
                return None, None
            
            # Terraformコードを解析
            parsed = load_from_path(terraform_path)
            print(f"Terraformコードの解析に成功しました！")
            
            # __tfmetaキーを削除
            if "__tfmeta" in parsed:
                del parsed["__tfmeta"]
                print("'__tfmeta'をエクスポート結果から除外しました。")
            
            # 出力ファイル名が指定されていない場合は、デフォルトのファイル名を使用
            if output_file is None:
                output_file = os.path.join(self.output_dir, "terraform_parsed.json")
            else:
                # 出力ファイルのパスが絶対パスでない場合は、output_dirと結合
                if not os.path.isabs(output_file):
                    output_file = os.path.join(self.output_dir, os.path.basename(output_file))
            
            # JSONファイルとして出力
            with open(output_file, 'w') as f:
                # インデントを付けて読みやすく出力
                json.dump(parsed, f, indent=2, default=str)
            
            print(f"解析結果をJSONファイルとして出力しました: {output_file}")
            
            # 解析結果の概要を表示
            self._print_summary(parsed)
            
            return parsed, output_file
        except Exception as e:
            print(f"エラー: {e}")
            return None, None
    
    def _print_summary(self, parsed_data: Dict[str, Any]) -> None:
        """
        解析結果の概要を表示
        
        Args:
            parsed_data: 解析されたTerraformデータ
        """
        resource_types = list(parsed_data.keys())
        print(f"\n検出されたリソースタイプ: {len(resource_types)}")
        print("リソースタイプ一覧:")
        for resource_type in resource_types:
            if isinstance(parsed_data[resource_type], list):
                count = len(parsed_data[resource_type])
            elif isinstance(parsed_data[resource_type], dict):
                count = len(parsed_data[resource_type].keys())
            else:
                count = 1
            print(f"  - {resource_type}: {count}個")
    
    def load_from_json(self, json_file: str) -> Optional[Dict[str, Any]]:
        """
        既存のJSONファイルからTerraformデータを読み込む
        
        Args:
            json_file: JSONファイルのパス
            
        Returns:
            読み込まれたTerraformデータ
        """
        try:
            with open(json_file, 'r') as f:
                data = json.load(f)
            return data
        except Exception as e:
            print(f"エラー: JSONファイルの読み込みに失敗しました: {e}")
            return None 