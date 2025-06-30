"""
ウェブツール
基本的なWeb検索とウェブページ取得機能
"""

import asyncio
import logging
import requests
from typing import Dict, List, Optional, Any
from urllib.parse import quote, urlparse
import json
import re

class WebSearcher:
    """ウェブ検索ツール"""
    
    def __init__(self, safe_mode: bool = True):
        self.safe_mode = safe_mode
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
    def search_web(self, query: str, max_results: int = 5) -> List[Dict[str, str]]:
        """ウェブ検索実行（DuckDuckGo Instant Answer API使用）"""
        try:
            # DuckDuckGo Instant Answer API（無料）
            search_url = f"https://api.duckduckgo.com/?q={quote(query)}&format=json&no_html=1&skip_disambig=1"
            
            response = self.session.get(search_url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            results = []
            
            # Abstract（要約）
            if data.get('Abstract'):
                results.append({
                    'title': data.get('Heading', 'DuckDuckGo結果'),
                    'snippet': data.get('Abstract', ''),
                    'url': data.get('AbstractURL', ''),
                    'source': 'DuckDuckGo'
                })
            
            # Related Topics
            for topic in data.get('RelatedTopics', [])[:max_results-1]:
                if isinstance(topic, dict) and topic.get('Text'):
                    results.append({
                        'title': topic.get('Text', '')[:100] + '...',
                        'snippet': topic.get('Text', ''),
                        'url': topic.get('FirstURL', ''),
                        'source': 'DuckDuckGo'
                    })
            
            # Definition
            if data.get('Definition'):
                results.append({
                    'title': f"定義: {data.get('DefinitionWord', '')}",
                    'snippet': data.get('Definition', ''),
                    'url': data.get('DefinitionURL', ''),
                    'source': 'Dictionary'
                })
            
            # Answer（直接回答）
            if data.get('Answer'):
                results.append({
                    'title': f"回答: {query}",
                    'snippet': data.get('Answer', ''),
                    'url': '',
                    'source': 'DuckDuckGo Answer'
                })
            
            return results[:max_results]
            
        except Exception as e:
            logging.error(f"❌ ウェブ検索エラー: {e}")
            return [{'title': 'エラー', 'snippet': f'検索エラー: {str(e)}', 'url': '', 'source': 'Error'}]
    
    def get_page_content(self, url: str, max_length: int = 2000) -> Dict[str, str]:
        """ウェブページの内容取得"""
        try:
            if not self._is_safe_url(url):
                return {
                    'content': 'セキュリティ上の理由でアクセスが制限されています',
                    'title': 'アクセス制限',
                    'error': 'Unsafe URL'
                }
            
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            # 簡単なHTML解析
            content = response.text
            
            # タイトル抽出
            title_match = re.search(r'<title[^>]*>(.*?)</title>', content, re.IGNORECASE | re.DOTALL)
            title = title_match.group(1).strip() if title_match else 'タイトルなし'
            
            # HTMLタグを除去
            text_content = re.sub(r'<[^>]+>', ' ', content)
            text_content = ' '.join(text_content.split())  # 空白正規化
            
            # 長さ制限
            if len(text_content) > max_length:
                text_content = text_content[:max_length] + '...'
            
            return {
                'content': text_content,
                'title': title,
                'url': url,
                'length': len(text_content)
            }
            
        except Exception as e:
            logging.error(f"❌ ページ取得エラー: {e}")
            return {
                'content': f'ページ取得エラー: {str(e)}',
                'title': 'エラー',
                'error': str(e)
            }
    
    def _is_safe_url(self, url: str) -> bool:
        """URL安全性チェック"""
        if not self.safe_mode:
            return True
        
        try:
            parsed = urlparse(url)
            
            # HTTPSまたはHTTPのみ許可
            if parsed.scheme not in ['http', 'https']:
                return False
            
            # ローカルアドレス禁止
            if parsed.hostname in ['localhost', '127.0.0.1', '0.0.0.0']:
                return False
            
            # プライベートIPアドレス禁止
            if parsed.hostname and (
                parsed.hostname.startswith('192.168.') or
                parsed.hostname.startswith('10.') or
                parsed.hostname.startswith('172.')
            ):
                return False
            
            return True
            
        except Exception:
            return False
    
    def search_and_summarize(self, query: str, llm_manager) -> str:
        """検索結果をLLMでまとめて返す"""
        try:
            # ウェブ検索実行
            search_results = self.search_web(query, max_results=3)
            
            if not search_results:
                return "検索結果が見つかりませんでした。"
            
            # 検索結果をテキスト形式に整理
            results_text = f"検索クエリ: {query}\n\n"
            for i, result in enumerate(search_results, 1):
                results_text += f"{i}. {result['title']}\n"
                results_text += f"   出典: {result['source']}\n"
                results_text += f"   内容: {result['snippet'][:300]}...\n"
                if result['url']:
                    results_text += f"   URL: {result['url']}\n"
                results_text += "\n"
            
            # LLMで要約
            summary_prompt = f"""
以下の検索結果を簡潔にまとめて、質問「{query}」に対する回答を作成してください：

{results_text}

要約は300文字以内で、重要なポイントを含めてください。
"""
            
            # 非同期実行を同期的に処理
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # 既に実行中のループがある場合
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(
                        lambda: asyncio.run(llm_manager.get_completion(summary_prompt, task_type="analysis"))
                    )
                    summary = future.result()
            else:
                summary = asyncio.run(llm_manager.get_completion(summary_prompt, task_type="analysis"))
            
            return f"🔍 検索結果まとめ:\n{summary}\n\n📚 参考リンク:\n" + \
                   "\n".join([f"- {r['title']}: {r['url']}" for r in search_results if r['url']])
            
        except Exception as e:
            logging.error(f"❌ 検索・要約エラー: {e}")
            return f"検索中にエラーが発生しました: {str(e)}"

class SimpleWebAPI:
    """シンプルなWeb API呼び出し"""
    
    def __init__(self):
        self.session = requests.Session()
    
    def get_json(self, url: str) -> Dict[str, Any]:
        """JSON APIからデータ取得"""
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logging.error(f"❌ API エラー: {e}")
            return {'error': str(e)}
    
    def get_weather_info(self, city: str = "Tokyo") -> str:
        """天気情報取得（サンプル）"""
        try:
            # OpenWeatherMap の無料API（要APIキー）または代替サービス
            # ここでは簡単な例として固定値を返す
            return f"⛅ {city}の現在の天気: 晴れ、気温: 22°C（注: リアルタイム天気APIは未設定）"
        except Exception as e:
            return f"天気情報の取得に失敗しました: {str(e)}"