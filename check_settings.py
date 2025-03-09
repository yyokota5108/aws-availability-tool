#!/usr/bin/env python3
"""
現在の設定を表示するシンプルなスクリプト
"""
import json
import sys
from src.config import get_settings

def main():
    # 設定を読み込む
    settings = get_settings()
    
    # 整形して表示
    print(json.dumps(settings, indent=2, ensure_ascii=False))
    
    # 特定の設定値を確認
    print("\n=== 重要な設定値 ===")
    print(f"AWS Region: {settings['aws']['region']}")
    print(f"Model ID: {settings['aws']['model_id']}")
    print(f"Output Directory: {settings['output']['directory']}")
    print(f"Language: {settings['app']['language']}")
    print(f"Debug Mode: {settings['app']['debug']}")

if __name__ == "__main__":
    main() 