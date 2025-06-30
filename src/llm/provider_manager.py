"""
LLMプロバイダー管理システム
複数の無料LLMサービスを効率的に管理し、フォールバック機能を提供
"""

import asyncio
import os
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from collections import defaultdict

# プロバイダー別クライアント
try:
    import openai
except ImportError:
    openai = None

try:
    import google.generativeai as genai
except ImportError:
    genai = None

try:
    from groq import Groq
except ImportError:
    Groq = None

from .rate_limiter import RateLimiter
from .fallback_handler import FallbackHandler
from ..utils.cache_manager import ResponseCache

class LLMProvider:
    """基底LLMプロバイダークラス"""
    
    def __init__(self, name: str, config: Dict[str, Any]):
        self.name = name
        self.config = config
        self.client = None
        self.is_available = False
        
    async def initialize(self) -> bool:
        """プロバイダーの初期化"""
        raise NotImplementedError
        
    async def get_completion(self, prompt: str, **kwargs) -> str:
        """テキスト生成の実行"""
        raise NotImplementedError
        
    def is_healthy(self) -> bool:
        """プロバイダーの健全性チェック"""
        return self.is_available

class GoogleGeminiProvider(LLMProvider):
    """Google Gemini プロバイダー"""
    
    async def initialize(self) -> bool:
        try:
            if not genai:
                logging.error("google-generativeai パッケージがインストールされていません")
                return False
                
            api_key = os.getenv(self.config.get('api_key_env', 'GOOGLE_API_KEY'))
            if not api_key:
                logging.error("Google API キーが設定されていません")
                return False
                
            genai.configure(api_key=api_key)
            self.client = genai.GenerativeModel(self.config.get('model', 'gemini-1.5-flash'))
            self.is_available = True
            
            logging.info(f"✅ {self.name} プロバイダーが初期化されました")
            return True
            
        except Exception as e:
            logging.error(f"❌ {self.name} プロバイダーの初期化に失敗: {e}")
            return False
    
    async def get_completion(self, prompt: str, **kwargs) -> str:
        try:
            response = await asyncio.get_event_loop().run_in_executor(
                None, 
                lambda: self.client.generate_content(prompt)
            )
            return response.text
            
        except Exception as e:
            logging.error(f"Google Gemini エラー: {e}")
            raise

class GroqProvider(LLMProvider):
    """Groq プロバイダー"""
    
    async def initialize(self) -> bool:
        try:
            if not Groq:
                logging.error("groq パッケージがインストールされていません")
                return False
                
            api_key = os.getenv(self.config.get('api_key_env', 'GROQ_API_KEY'))
            if not api_key:
                logging.error("Groq API キーが設定されていません")
                return False
                
            self.client = Groq(api_key=api_key)
            self.is_available = True
            
            logging.info(f"✅ {self.name} プロバイダーが初期化されました")
            return True
            
        except Exception as e:
            logging.error(f"❌ {self.name} プロバイダーの初期化に失敗: {e}")
            return False
    
    async def get_completion(self, prompt: str, **kwargs) -> str:
        try:
            response = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.client.chat.completions.create(
                    model=self.config.get('model', 'llama3-70b-8192'),
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=self.config.get('max_tokens', 4096),
                    temperature=self.config.get('temperature', 0.3)
                )
            )
            return response.choices[0].message.content
            
        except Exception as e:
            logging.error(f"Groq エラー: {e}")
            raise

class TogetherAIProvider(LLMProvider):
    """Together AI プロバイダー"""
    
    async def initialize(self) -> bool:
        try:
            if not openai:
                logging.error("openai パッケージがインストールされていません")
                return False
                
            api_key = os.getenv(self.config.get('api_key_env', 'TOGETHER_API_KEY'))
            if not api_key:
                logging.error("Together AI API キーが設定されていません")
                return False
                
            self.client = openai.OpenAI(
                api_key=api_key,
                base_url=self.config.get('base_url', 'https://api.together.xyz/v1')
            )
            self.is_available = True
            
            logging.info(f"✅ {self.name} プロバイダーが初期化されました")
            return True
            
        except Exception as e:
            logging.error(f"❌ {self.name} プロバイダーの初期化に失敗: {e}")
            return False
    
    async def get_completion(self, prompt: str, **kwargs) -> str:
        try:
            response = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.client.chat.completions.create(
                    model=self.config.get('model', 'meta-llama/Llama-3-8b-chat-hf'),
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=self.config.get('max_tokens', 2048),
                    temperature=self.config.get('temperature', 0.5)
                )
            )
            return response.choices[0].message.content
            
        except Exception as e:
            logging.error(f"Together AI エラー: {e}")
            raise

class LLMProviderManager:
    """LLMプロバイダー管理システム"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.providers: Dict[str, LLMProvider] = {}
        self.rate_limiter = RateLimiter()
        self.fallback_handler = FallbackHandler()
        self.cache = ResponseCache()
        
        # プロバイダー優先順位
        self.provider_priority = [
            "google_gemini",
            "groq_llama", 
            "together_ai"
        ]
        
        # タスクタイプ別最適プロバイダー
        self.task_provider_map = {
            "code_generation": "groq_llama",
            "complex_reasoning": "google_gemini", 
            "simple_task": "together_ai",
            "general": "google_gemini"
        }
        
    async def initialize(self) -> bool:
        """全プロバイダーの初期化"""
        logging.info("🚀 LLMプロバイダー管理システムを初期化中...")
        
        # プロバイダー設定から各プロバイダーを初期化
        provider_configs = self.config.get('providers', {})
        
        for provider_name, provider_config in provider_configs.items():
            try:
                if provider_name == 'google_gemini':
                    provider = GoogleGeminiProvider(provider_name, provider_config)
                elif provider_name == 'groq_llama':
                    provider = GroqProvider(provider_name, provider_config)
                elif provider_name == 'together_ai':
                    provider = TogetherAIProvider(provider_name, provider_config)
                else:
                    logging.warning(f"未知のプロバイダー: {provider_name}")
                    continue
                    
                if await provider.initialize():
                    self.providers[provider_name] = provider
                    logging.info(f"✅ {provider_name} プロバイダー初期化完了")
                else:
                    logging.warning(f"⚠️ {provider_name} プロバイダー初期化失敗")
                    
            except Exception as e:
                logging.error(f"❌ {provider_name} プロバイダー初期化エラー: {e}")
        
        if not self.providers:
            logging.error("❌ 利用可能なプロバイダーがありません")
            return False
            
        logging.info(f"✅ {len(self.providers)}個のプロバイダーが利用可能です")
        return True
    
    def _select_provider(self, task_type: str = "general") -> Optional[str]:
        """タスクタイプに基づく最適プロバイダー選択"""
        
        # タスクタイプに基づく最適プロバイダー
        preferred_provider = self.task_provider_map.get(task_type, "google_gemini")
        
        # 最適プロバイダーが利用可能かチェック
        if (preferred_provider in self.providers and 
            self.providers[preferred_provider].is_healthy() and
            self.rate_limiter.can_make_request(preferred_provider)):
            return preferred_provider
        
        # フォールバック: 優先順位順にチェック
        for provider_name in self.provider_priority:
            if (provider_name in self.providers and 
                self.providers[provider_name].is_healthy() and
                self.rate_limiter.can_make_request(provider_name)):
                return provider_name
        
        return None
    
    async def get_completion(self, prompt: str, task_type: str = "general", **kwargs) -> str:
        """最適なプロバイダーでLLM推論実行"""
        
        # キャッシュチェック
        cached_response = self.cache.get_cached_response(prompt)
        if cached_response:
            logging.info("💰 キャッシュからレスポンスを取得")
            return cached_response
        
        # 最適プロバイダー選択
        selected_provider = self._select_provider(task_type)
        
        if not selected_provider:
            raise Exception("利用可能なプロバイダーがありません")
        
        try:
            # プロバイダーでリクエスト実行
            provider = self.providers[selected_provider]
            response = await provider.get_completion(prompt, **kwargs)
            
            # レート制限更新
            self.rate_limiter.record_request(selected_provider)
            
            # キャッシュ保存
            self.cache.cache_response(prompt, response)
            
            logging.info(f"✅ {selected_provider} でレスポンス生成完了")
            return response
            
        except Exception as e:
            logging.error(f"❌ {selected_provider} でエラー発生: {e}")
            
            # フォールバック実行
            return await self._fallback_request(prompt, task_type, excluded=[selected_provider])
    
    async def _fallback_request(self, prompt: str, task_type: str, excluded: List[str] = None) -> str:
        """フォールバック実行"""
        if excluded is None:
            excluded = []
            
        logging.info("🔄 フォールバック実行中...")
        
        for provider_name in self.provider_priority:
            if (provider_name not in excluded and
                provider_name in self.providers and
                self.providers[provider_name].is_healthy()):
                
                try:
                    provider = self.providers[provider_name]
                    response = await provider.get_completion(prompt)
                    
                    self.rate_limiter.record_request(provider_name)
                    self.cache.cache_response(prompt, response)
                    
                    logging.info(f"✅ フォールバック成功: {provider_name}")
                    return response
                    
                except Exception as e:
                    logging.error(f"❌ フォールバック失敗 {provider_name}: {e}")
                    continue
        
        raise Exception("全てのプロバイダーでリクエストが失敗しました")
    
    def get_provider_status(self) -> Dict[str, Dict[str, Any]]:
        """プロバイダーの状態取得"""
        status = {}
        
        for name, provider in self.providers.items():
            status[name] = {
                'available': provider.is_healthy(),
                'requests_today': self.rate_limiter.get_daily_requests(name),
                'rate_limit_status': self.rate_limiter.get_status(name)
            }
        
        return status