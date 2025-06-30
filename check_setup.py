#!/usr/bin/env python3
"""
Free LLM Driver セットアップ確認スクリプト
システムの設定と依存関係を確認し、問題があれば修正方法を提案
"""

import os
import sys
import subprocess
import asyncio
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Optional

# ログ設定（簡易版）
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

class SetupChecker:
    """セットアップ確認クラス"""
    
    def __init__(self):
        self.issues = []
        self.warnings = []
        self.success_count = 0
        self.total_checks = 0
    
    def check_item(self, description: str, check_func, fix_suggestion: str = "") -> bool:
        """個別チェック実行"""
        self.total_checks += 1
        print(f"🔍 {description}... ", end="", flush=True)
        
        try:
            result = check_func()
            if result:
                print("✅")
                self.success_count += 1
                return True
            else:
                print("❌")
                self.issues.append(f"{description}: {fix_suggestion}")
                return False
        except Exception as e:
            print(f"❌ (エラー: {e})")
            self.issues.append(f"{description}: エラー - {e}")
            return False
    
    def check_warning(self, description: str, check_func, warning_message: str = "") -> bool:
        """警告レベルのチェック"""
        print(f"⚠️  {description}... ", end="", flush=True)
        
        try:
            result = check_func()
            if result:
                print("✅")
                return True
            else:
                print("⚠️ ")
                self.warnings.append(f"{description}: {warning_message}")
                return False
        except Exception as e:
            print(f"⚠️  (エラー: {e})")
            self.warnings.append(f"{description}: エラー - {e}")
            return False

def check_python_version() -> bool:
    """Python バージョンチェック"""
    version = sys.version_info
    return version.major >= 3 and version.minor >= 8

def check_required_packages() -> bool:
    """必要パッケージの確認"""
    required_packages = [
        'openai', 'google-generativeai', 'groq', 
        'aiohttp', 'requests', 'pyyaml', 'python-dotenv'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    return len(missing_packages) == 0

def check_directory_structure() -> bool:
    """ディレクトリ構造チェック"""
    required_dirs = [
        'src', 'src/agent', 'src/llm', 'src/tools', 'src/utils', 'config'
    ]
    
    missing_dirs = []
    for dir_path in required_dirs:
        if not os.path.exists(dir_path):
            missing_dirs.append(dir_path)
    
    return len(missing_dirs) == 0

def check_config_files() -> bool:
    """設定ファイルチェック"""
    required_files = [
        'config/providers.yaml',
        'config/limits.yaml'
    ]
    
    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    return len(missing_files) == 0

def check_env_file() -> bool:
    """環境ファイルチェック"""
    return os.path.exists('.env')

def check_api_keys() -> bool:
    """APIキー設定チェック"""
    from dotenv import load_dotenv
    load_dotenv()
    
    required_keys = ['GOOGLE_API_KEY', 'GROQ_API_KEY', 'TOGETHER_API_KEY']
    missing_keys = []
    
    for key in required_keys:
        value = os.getenv(key)
        if not value or len(value) < 10:
            missing_keys.append(key)
    
    return len(missing_keys) == 0

async def check_api_connectivity() -> bool:
    """API接続テスト"""
    try:
        sys.path.insert(0, str(Path(__file__).parent))
        from src.llm.provider_manager import LLMProviderManager
        
        # 簡易設定でテスト
        config = {
            'providers': {
                'google_gemini': {
                    'model': 'gemini-1.5-flash',
                    'api_key_env': 'GOOGLE_API_KEY'
                }
            }
        }
        
        manager = LLMProviderManager(config)
        initialized = await manager.initialize()
        
        if initialized:
            # 簡単なテスト実行
            response = await manager.get_completion("Hello", task_type="simple_task")
            return len(response) > 0
        
        return False
        
    except Exception:
        return False

def check_write_permissions() -> bool:
    """書き込み権限チェック"""
    test_dirs = ['logs', '.cache']
    
    for test_dir in test_dirs:
        try:
            os.makedirs(test_dir, exist_ok=True)
            test_file = os.path.join(test_dir, 'test_write.tmp')
            with open(test_file, 'w') as f:
                f.write('test')
            os.remove(test_file)
        except Exception:
            return False
    
    return True

def create_missing_directories():
    """不足ディレクトリの作成"""
    dirs_to_create = [
        'logs', '.cache', 'src', 'src/agent', 'src/llm', 'src/tools', 'src/utils', 'config'
    ]
    
    created_dirs = []
    for dir_path in dirs_to_create:
        if not os.path.exists(dir_path):
            try:
                os.makedirs(dir_path, exist_ok=True)
                created_dirs.append(dir_path)
            except Exception as e:
                print(f"❌ ディレクトリ作成失敗 {dir_path}: {e}")
    
    if created_dirs:
        print(f"✅ ディレクトリを作成: {', '.join(created_dirs)}")

def copy_env_example():
    """環境ファイルのコピー"""
    if os.path.exists('.env.example') and not os.path.exists('.env'):
        try:
            import shutil
            shutil.copy('.env.example', '.env')
            print("✅ .env.example を .env にコピーしました")
            print("📝 .envファイルを編集してAPIキーを設定してください")
        except Exception as e:
            print(f"❌ .envファイルコピー失敗: {e}")

def install_missing_packages():
    """不足パッケージのインストール"""
    try:
        print("📦 不足パッケージをインストール中...")
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
        print("✅ パッケージインストール完了")
        return True
    except Exception as e:
        print(f"❌ パッケージインストール失敗: {e}")
        return False

async def main():
    """メイン確認処理"""
    print("🚀 Free LLM Driver セットアップ確認")
    print("="*50)
    
    checker = SetupChecker()
    
    # 基本チェック
    checker.check_item(
        "Python 3.8+ バージョン確認",
        check_python_version,
        "Python 3.8以上をインストールしてください"
    )
    
    checker.check_item(
        "ディレクトリ構造確認",
        check_directory_structure,
        "プロジェクトディレクトリが不完全です"
    )
    
    checker.check_item(
        "設定ファイル存在確認",
        check_config_files,
        "config/providers.yaml または config/limits.yaml が見つかりません"
    )
    
    checker.check_item(
        "書き込み権限確認",
        check_write_permissions,
        "logs または .cache ディレクトリへの書き込み権限がありません"
    )
    
    # パッケージチェック
    if not checker.check_item(
        "必要パッケージ確認",
        check_required_packages,
        "pip install -r requirements.txt を実行してください"
    ):
        print("\n📦 不足パッケージのインストールを試行...")
        if install_missing_packages():
            print("✅ パッケージインストール完了。再確認...")
            checker.check_item("必要パッケージ再確認", check_required_packages, "")
    
    # 環境設定チェック
    if not checker.check_item(
        ".env ファイル存在確認",
        check_env_file,
        ".env.example を .env にコピーしてAPIキーを設定してください"
    ):
        copy_env_example()
        checker.check_item(".env ファイル再確認", check_env_file, "")
    
    # APIキーチェック
    checker.check_warning(
        "APIキー設定確認",
        check_api_keys,
        ".envファイルでAPIキーを設定してください"
    )
    
    # API接続テスト（警告レベル）
    if os.path.exists('.env'):
        checker.check_warning(
            "API接続テスト",
            lambda: asyncio.run(check_api_connectivity()),
            "APIキーが正しく設定されていない可能性があります"
        )
    
    # 自動修正
    print("\n🔧 自動修正可能な問題を修正中...")
    create_missing_directories()
    
    # 結果サマリー
    print("\n" + "="*50)
    print("📊 確認結果サマリー")
    print("="*50)
    
    success_rate = (checker.success_count / checker.total_checks * 100) if checker.total_checks > 0 else 0
    print(f"✅ 成功: {checker.success_count}/{checker.total_checks} ({success_rate:.1f}%)")
    
    if checker.issues:
        print(f"\n❌ 修正が必要な問題 ({len(checker.issues)}件):")
        for i, issue in enumerate(checker.issues, 1):
            print(f"  {i}. {issue}")
    
    if checker.warnings:
        print(f"\n⚠️  警告 ({len(checker.warnings)}件):")
        for i, warning in enumerate(checker.warnings, 1):
            print(f"  {i}. {warning}")
    
    # 次のステップ案内
    print("\n📋 次のステップ:")
    
    if checker.issues:
        print("1. 上記の問題を修正してください")
        print("2. 修正後、再度このスクリプトを実行してください")
    else:
        if checker.warnings:
            print("1. 警告を確認し、必要に応じて設定を調整してください")
        print("2. python main.py -i でインタラクティブモードを開始")
        print("3. python main.py --status でシステム状況を確認")
        print("4. python main.py --goal \"テスト\" でサンプル実行")
    
    print("\n📚 詳細なドキュメント: README.md")
    print("🚀 Free LLM Driver の使用を開始できます！")

if __name__ == "__main__":
    asyncio.run(main())