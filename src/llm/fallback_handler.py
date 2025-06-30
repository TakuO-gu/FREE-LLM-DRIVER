"""
フォールバック処理システム
プロバイダー障害時の自動切り替えとエラーハンドリングを管理
"""

import logging
import asyncio
from typing import List, Dict, Optional, Callable, Any
from datetime import datetime, timedelta
from enum import Enum

class FailureType(Enum):
    """障害タイプの定義"""
    RATE_LIMIT = "rate_limit"
    API_ERROR = "api_error"
    NETWORK_ERROR = "network_error"
    AUTHENTICATION_ERROR = "auth_error"
    QUOTA_EXCEEDED = "quota_exceeded"
    SERVICE_UNAVAILABLE = "service_unavailable"
    UNKNOWN_ERROR = "unknown_error"

class ProviderHealth:
    """プロバイダーの健全性管理"""
    
    def __init__(self, name: str):
        self.name = name
        self.failure_count = 0
        self.last_failure_time: Optional[datetime] = None
        self.consecutive_failures = 0
        self.total_requests = 0
        self.successful_requests = 0
        self.is_temporarily_disabled = False
        self.disable_until: Optional[datetime] = None
        
    def record_success(self):
        """成功の記録"""
        self.total_requests += 1
        self.successful_requests += 1
        self.consecutive_failures = 0
        
        # 一時的無効化を解除
        if self.is_temporarily_disabled and datetime.now() > (self.disable_until or datetime.now()):
            self.is_temporarily_disabled = False
            self.disable_until = None
            logging.info(f"✅ {self.name}: 一時的無効化を解除")
    
    def record_failure(self, failure_type: FailureType = FailureType.UNKNOWN_ERROR):
        """失敗の記録"""
        self.total_requests += 1
        self.failure_count += 1
        self.consecutive_failures += 1
        self.last_failure_time = datetime.now()
        
        # 連続失敗回数に基づく一時的無効化
        if self.consecutive_failures >= 5:
            disable_duration = min(300, 30 * (2 ** (self.consecutive_failures - 5)))  # 最大5分
            self.is_temporarily_disabled = True
            self.disable_until = datetime.now() + timedelta(seconds=disable_duration)
            
            logging.warning(f"⚠️ {self.name}: 連続失敗により{disable_duration}秒間無効化")
    
    def is_healthy(self) -> bool:
        """健全性チェック"""
        if self.is_temporarily_disabled:
            if datetime.now() > (self.disable_until or datetime.now()):
                self.is_temporarily_disabled = False
                self.disable_until = None
                return True
            return False
        
        return True
    
    def get_success_rate(self) -> float:
        """成功率取得"""
        if self.total_requests == 0:
            return 1.0
        return self.successful_requests / self.total_requests

class FallbackHandler:
    """フォールバック処理管理"""
    
    def __init__(self):
        self.provider_health: Dict[str, ProviderHealth] = {}
        self.max_retries = 3
        self.retry_delay = 2.0  # 秒
        self.circuit_breaker_threshold = 0.5  # 成功率50%未満で回路遮断
        
    def register_provider(self, provider_name: str):
        """プロバイダーの登録"""
        if provider_name not in self.provider_health:
            self.provider_health[provider_name] = ProviderHealth(provider_name)
            logging.info(f"📝 プロバイダー登録: {provider_name}")
    
    def record_success(self, provider_name: str):
        """成功の記録"""
        if provider_name not in self.provider_health:
            self.register_provider(provider_name)
        
        self.provider_health[provider_name].record_success()
        logging.debug(f"✅ {provider_name}: 成功記録")
    
    def record_failure(self, provider_name: str, error: Exception):
        """失敗の記録とタイプ分類"""
        if provider_name not in self.provider_health:
            self.register_provider(provider_name)
        
        failure_type = self._classify_error(error)
        self.provider_health[provider_name].record_failure(failure_type)
        
        logging.warning(f"❌ {provider_name}: 失敗記録 ({failure_type.value}) - {str(error)}")
    
    def _classify_error(self, error: Exception) -> FailureType:
        """エラーの分類"""
        error_message = str(error).lower()
        
        if "rate limit" in error_message or "429" in error_message:
            return FailureType.RATE_LIMIT
        elif "quota" in error_message or "exceeded" in error_message:
            return FailureType.QUOTA_EXCEEDED
        elif "authentication" in error_message or "unauthorized" in error_message or "401" in error_message:
            return FailureType.AUTHENTICATION_ERROR
        elif "network" in error_message or "connection" in error_message:
            return FailureType.NETWORK_ERROR
        elif "503" in error_message or "service unavailable" in error_message:
            return FailureType.SERVICE_UNAVAILABLE
        elif "api" in error_message:
            return FailureType.API_ERROR
        else:
            return FailureType.UNKNOWN_ERROR
    
    def is_provider_healthy(self, provider_name: str) -> bool:
        """プロバイダーの健全性チェック"""
        if provider_name not in self.provider_health:
            return True  # 未知のプロバイダーは健全とみなす
        
        health = self.provider_health[provider_name]
        
        # 基本的な健全性チェック
        if not health.is_healthy():
            return False
        
        # 成功率による回路遮断チェック
        if health.total_requests >= 10 and health.get_success_rate() < self.circuit_breaker_threshold:
            logging.warning(f"🔌 {provider_name}: 成功率低下により回路遮断 ({health.get_success_rate():.2f})")
            return False
        
        return True
    
    def get_healthy_providers(self, available_providers: List[str]) -> List[str]:
        """健全なプロバイダー一覧取得"""
        healthy_providers = []
        
        for provider in available_providers:
            if self.is_provider_healthy(provider):
                healthy_providers.append(provider)
        
        # 成功率でソート（高い順）
        healthy_providers.sort(key=lambda p: self.provider_health.get(p, ProviderHealth(p)).get_success_rate(), reverse=True)
        
        return healthy_providers
    
    async def execute_with_fallback(
        self,
        providers: List[str],
        execution_func: Callable[[str], Any],
        *args,
        **kwargs
    ) -> Any:
        """フォールバック付きでの実行"""
        
        healthy_providers = self.get_healthy_providers(providers)
        
        if not healthy_providers:
            raise Exception("利用可能な健全なプロバイダーがありません")
        
        last_exception = None
        
        for attempt, provider in enumerate(healthy_providers):
            try:
                logging.info(f"🎯 {provider} で実行を試行 (試行 {attempt + 1}/{len(healthy_providers)})")
                
                result = await execution_func(provider, *args, **kwargs)
                
                # 成功を記録
                self.record_success(provider)
                return result
                
            except Exception as e:
                last_exception = e
                self.record_failure(provider, e)
                
                # 最後のプロバイダーでない場合は次を試行
                if attempt < len(healthy_providers) - 1:
                    logging.info(f"🔄 {provider} で失敗、次のプロバイダーを試行...")
                    
                    # リトライ前の待機
                    if self.retry_delay > 0:
                        await asyncio.sleep(self.retry_delay)
                else:
                    logging.error(f"❌ 全てのプロバイダーで実行失敗")
        
        # 全てのプロバイダーで失敗した場合
        raise Exception(f"全てのプロバイダーで実行に失敗しました。最後のエラー: {last_exception}")
    
    def get_provider_status(self, provider_name: str) -> Dict[str, Any]:
        """プロバイダーの状態取得"""
        if provider_name not in self.provider_health:
            return {
                'registered': False,
                'healthy': True,
                'total_requests': 0,
                'success_rate': 1.0,
                'consecutive_failures': 0
            }
        
        health = self.provider_health[provider_name]
        
        return {
            'registered': True,
            'healthy': health.is_healthy(),
            'total_requests': health.total_requests,
            'successful_requests': health.successful_requests,
            'failure_count': health.failure_count,
            'success_rate': health.get_success_rate(),
            'consecutive_failures': health.consecutive_failures,
            'last_failure_time': health.last_failure_time,
            'is_temporarily_disabled': health.is_temporarily_disabled,
            'disable_until': health.disable_until
        }
    
    def get_all_status(self) -> Dict[str, Dict[str, Any]]:
        """全プロバイダーの状態取得"""
        return {
            provider: self.get_provider_status(provider)
            for provider in self.provider_health.keys()
        }
    
    def reset_provider_health(self, provider_name: str):
        """プロバイダーの健全性リセット"""
        if provider_name in self.provider_health:
            self.provider_health[provider_name] = ProviderHealth(provider_name)
            logging.info(f"🔄 {provider_name}: 健全性をリセット")
    
    def set_circuit_breaker_threshold(self, threshold: float):
        """回路遮断の閾値設定"""
        self.circuit_breaker_threshold = max(0.0, min(1.0, threshold))
        logging.info(f"🔌 回路遮断閾値を設定: {self.circuit_breaker_threshold}")
    
    def set_retry_config(self, max_retries: int, retry_delay: float):
        """リトライ設定"""
        self.max_retries = max(0, max_retries)
        self.retry_delay = max(0.0, retry_delay)
        logging.info(f"🔄 リトライ設定: 最大{self.max_retries}回, 間隔{self.retry_delay}秒")