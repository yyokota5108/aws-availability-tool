"""
アプリケーション設定管理モジュール
"""
import os
from pathlib import Path
from typing import Any, Dict, Optional, cast
import yaml
from dotenv import load_dotenv

# .envファイルを読み込む（存在する場合）
load_dotenv()

# デフォルト設定
DEFAULT_SETTINGS = {
    # AWS関連設定
    "aws": {
        "region": "ap-northeast-1",
        "model_id": "anthropic.claude-3-5-sonnet-20240620-v1:0",
    },
    # 出力設定
    "output": {
        "directory": "output",
        "default_json_filename": "terraform_parsed.json",
        "default_report_filename": "availability_report.json",
        "default_html_filename": "availability_report.html",
    },
    # アプリケーション設定
    "app": {
        "language": "ja",
        "debug": False,
    },
}

# シングルトンインスタンス
_settings_instance: Optional[Dict[str, Any]] = None


def get_settings() -> Dict[str, Any]:
    """
    アプリケーション設定を取得する
    
    設定の優先順位:
    1. 環境変数
    2. 設定ファイル
    3. デフォルト値
    
    Returns:
        設定辞書
    """
    global _settings_instance
    
    if _settings_instance is not None:
        return _settings_instance
    
    # デフォルト設定をベースにする
    settings = DEFAULT_SETTINGS.copy()
    
    # 設定ファイルからの読み込み
    config_file = _get_config_file_path()
    if config_file.exists():
        try:
            with open(config_file, "r") as f:
                file_settings = yaml.safe_load(f)
                if file_settings:
                    # 設定をマージする
                    _deep_merge(settings, file_settings)
        except Exception as e:
            print(f"警告: 設定ファイルの読み込みに失敗しました: {e}")
    
    # 環境変数からの読み込み
    _override_from_env(settings)
    
    # シングルトンインスタンスを設定
    _settings_instance = settings
    return settings


def _get_config_file_path() -> Path:
    """
    設定ファイルのパスを取得する
    
    以下の順で検索:
    1. カレントディレクトリの config.yaml
    2. ユーザーホームディレクトリの .aws_availability/config.yaml
    
    Returns:
        設定ファイルのパス
    """
    # まず、カレントディレクトリ内のconfig.yamlを確認
    current_dir_config = Path("config.yaml")
    if current_dir_config.exists():
        return current_dir_config
    
    # 次に、カレントディレクトリ内のconfig/config.yamlを確認
    config_dir_config = Path("config/config.yaml")
    if config_dir_config.exists():
        return config_dir_config
    
    # 次に、ユーザーホームディレクトリの.aws_availability/config.yamlを確認
    home_dir = Path.home()
    home_config = home_dir / ".aws_availability" / "config.yaml"
    return home_config


def _deep_merge(target: Dict[str, Any], source: Dict[str, Any]) -> None:
    """
    2つの辞書を再帰的にマージする
    
    Args:
        target: マージ先の辞書（この辞書が更新される）
        source: マージ元の辞書
    """
    for key, value in source.items():
        if key in target and isinstance(target[key], dict) and isinstance(value, dict):
            _deep_merge(target[key], value)
        else:
            target[key] = value


def _override_from_env(settings: Dict[str, Any]) -> None:
    """
    環境変数から設定を上書きする
    
    環境変数の命名規則:
    - AWS_REGION: aws.region
    - AWS_MODEL_ID: aws.model_id
    - OUTPUT_DIRECTORY: output.directory
    - APP_LANGUAGE: app.language
    - APP_DEBUG: app.debug (true/false)
    
    Args:
        settings: 更新する設定辞書
    """
    # AWS設定
    if "AWS_REGION" in os.environ:
        settings["aws"]["region"] = os.environ["AWS_REGION"]
    if "AWS_MODEL_ID" in os.environ:
        settings["aws"]["model_id"] = os.environ["AWS_MODEL_ID"]
    
    # 出力設定
    if "OUTPUT_DIRECTORY" in os.environ:
        settings["output"]["directory"] = os.environ["OUTPUT_DIRECTORY"]
    
    # アプリケーション設定
    if "APP_LANGUAGE" in os.environ:
        settings["app"]["language"] = os.environ["APP_LANGUAGE"]
    if "APP_DEBUG" in os.environ:
        settings["app"]["debug"] = os.environ["APP_DEBUG"].lower() in ("true", "1", "yes")


def reset_settings() -> None:
    """
    設定をリセットする（主にテスト用）
    """
    global _settings_instance
    _settings_instance = None 