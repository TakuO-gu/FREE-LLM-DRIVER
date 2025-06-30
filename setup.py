#!/usr/bin/env python3
"""
Free LLM Driver - 無料オンラインLLM + Open Interpreter実装
"""

import os
import sys
from pathlib import Path

def setup_environment():
    """環境セットアップ"""
    print("🚀 Free LLM Driver セットアップを開始します...")
    
    # 必要なディレクトリの確認
    dirs_to_check = [
        'src', 'src/agent', 'src/llm', 'src/tools', 'src/utils', 'config'
    ]
    
    for dir_name in dirs_to_check:
        if not os.path.exists(dir_name):
            print(f"❌ ディレクトリが見つかりません: {dir_name}")
            return False
        else:
            print(f"✅ ディレクトリ確認: {dir_name}")
    
    # .envファイルの確認
    if not os.path.exists('.env'):
        print("⚠️  .envファイルが見つかりません。.env.exampleからコピーしてください。")
        if os.path.exists('.env.example'):
            import shutil
            shutil.copy('.env.example', '.env')
            print("✅ .env.exampleから.envファイルを作成しました")
        else:
            print("❌ .env.exampleファイルも見つかりません")
    
    print("✅ 環境セットアップが完了しました！")
    print("\n次のステップ:")
    print("1. .envファイルにAPIキーを設定してください")
    print("2. python -m pip install -r requirements.txt でパッケージをインストール")
    print("3. python main.py でアプリケーションを起動")
    
    return True

def check_api_keys():
    """APIキーの設定確認"""
    from dotenv import load_dotenv
    load_dotenv()
    
    required_keys = [
        'GOOGLE_API_KEY',
        'GROQ_API_KEY', 
        'TOGETHER_API_KEY'
    ]
    
    print("\n🔑 APIキー設定確認:")
    all_set = True
    
    for key in required_keys:
        value = os.getenv(key)
        if value and len(value) > 10:
            print(f"✅ {key}: 設定済み")
        else:
            print(f"❌ {key}: 未設定または無効")
            all_set = False
    
    if all_set:
        print("✅ 全てのAPIキーが設定されています")
    else:
        print("⚠️  一部のAPIキーが未設定です。.envファイルを確認してください。")
    
    return all_set

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "check":
        # APIキー確認モード
        try:
            check_api_keys()
        except ImportError:
            print("❌ python-dotenvがインストールされていません")
            print("pip install python-dotenv を実行してください")
    else:
        # 通常のセットアップモード
        setup_environment()