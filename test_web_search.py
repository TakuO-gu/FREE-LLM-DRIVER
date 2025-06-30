#!/usr/bin/env python3
"""
Web検索機能の単体テスト
"""

import asyncio
import sys
from pathlib import Path

# プロジェクトルートをパスに追加
sys.path.insert(0, str(Path(__file__).parent))

from src.tools.web_tools import WebSearcher

async def test_web_search():
    """Web検索機能テスト"""
    print("🔍 Web検索機能テスト")
    
    searcher = WebSearcher(safe_mode=True)
    
    # 基本検索テスト
    print("\n1. 基本検索テスト:")
    results = searcher.search_web("Python programming language", max_results=3)
    
    for i, result in enumerate(results, 1):
        print(f"  {i}. {result['title']}")
        print(f"     出典: {result['source']}")
        print(f"     内容: {result['snippet'][:100]}...")
        if result['url']:
            print(f"     URL: {result['url']}")
        print()
    
    # 日本語検索テスト
    print("\n2. 日本語検索テスト:")
    results_jp = searcher.search_web("Python とは", max_results=3)
    
    for i, result in enumerate(results_jp, 1):
        print(f"  {i}. {result['title']}")
        print(f"     出典: {result['source']}")
        print(f"     内容: {result['snippet'][:100]}...")
        if result['url']:
            print(f"     URL: {result['url']}")
        print()

if __name__ == "__main__":
    asyncio.run(test_web_search())