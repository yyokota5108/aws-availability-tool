from tfparse import load_from_path
import sys
import json
import os

def ensure_output_directory(directory="output"):
    """出力ディレクトリが存在することを確認し、なければ作成する"""
    os.makedirs(directory, exist_ok=True)
    return directory

def export_terraform_to_json(terraform_path, output_file=None):
    """Terraformコードを解析し、結果をJSONファイルとして出力する"""
    try:
        # Terraformコードを解析
        parsed = load_from_path(terraform_path)
        print(f"Terraformコードの解析に成功しました！")
        
        # __tfmetaキーを削除
        if "__tfmeta" in parsed:
            del parsed["__tfmeta"]
            print("'__tfmeta'をエクスポート結果から除外しました。")
        
        # 出力ディレクトリを確保
        output_dir = ensure_output_directory()
        
        # 出力ファイル名が指定されていない場合は、デフォルトのファイル名を使用
        if output_file is None:
            output_file = os.path.join(output_dir, "terraform_parsed.json")
        else:
            # 出力ファイルのパスが絶対パスでない場合は、output_dirと結合
            if not os.path.isabs(output_file):
                output_file = os.path.join(output_dir, os.path.basename(output_file))
        
        # JSONファイルとして出力
        with open(output_file, 'w') as f:
            # インデントを付けて読みやすく出力
            json.dump(parsed, f, indent=2, default=str)
        
        print(f"解析結果をJSONファイルとして出力しました: {output_file}")
        
        # 解析結果の概要を表示
        resource_types = list(parsed.keys())
        print(f"\n検出されたリソースタイプ: {len(resource_types)}")
        print("リソースタイプ一覧:")
        for resource_type in resource_types:
            if isinstance(parsed[resource_type], list):
                count = len(parsed[resource_type])
            elif isinstance(parsed[resource_type], dict):
                count = len(parsed[resource_type].keys())
            else:
                count = 1
            print(f"  - {resource_type}: {count}個")
        
        return parsed, output_file
    except Exception as e:
        print(f"エラー: {e}")
        return None, None

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("使用方法: python export_terraform_json.py <terraform_directory_path> [output_file_path]")
        sys.exit(1)
    
    terraform_path = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    print(f"Terraformコードを解析中: {terraform_path}")
    export_terraform_to_json(terraform_path, output_file) 