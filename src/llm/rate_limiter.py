"""
レート制限管理システム
各プロバイダーのAPI制限を管理し、効率的なリクエスト制御を行う
"""

import time
import logging
from typing import Dict, Optional
from datetime import datetime, timedelta
from collections import defaultdict, deque

class RateLimiter:
    """レート制限管理クラス"""
    
    def __init__(self):
        # リクエスト履歴の記録（プロバイダー別）
        self.request_history: Dict[str, deque] = defaultdict(lambda: deque())
        
        # プロバイダー別制限設定（デフォルト値）
        self.default_limits = {
            'google_gemini': {
                'requests_per_minute': 60,
                'requests_per_day': 1500,
                'requests_per_month': 45000
            },
            'groq_llama': {
                'requests_per_minute': 30,
                'requests_per_day': 14400,
                'requests_per_month': 432000
            },
            'together_ai': {
                'requests_per_minute': 10,
                'requests_per_day': 200,  # 月200を日割り
                'requests_per_month': 200
            }
        }
        
        # カスタム制限設定（外部設定で上書き可能）
        self.custom_limits: Dict[str, Dict[str, int]] = {}
        
        # 最後のリセット時刻
        self.last_daily_reset = datetime.now().date()
        self.last_monthly_reset = datetime.now().replace(day=1).date()
        
    def set_custom_limits(self, provider: str, limits: Dict[str, int]):
        """カスタム制限設定"""
        self.custom_limits[provider] = limits
        logging.info(f"📊 {provider} のカスタム制限を設定: {limits}")
    
    def _get_limits(self, provider: str) -> Dict[str, int]:
        """プロバイダーの制限値取得"""
        if provider in self.custom_limits:
            return self.custom_limits[provider]
        return self.default_limits.get(provider, {
            'requests_per_minute': 10,
            'requests_per_day': 100,
            'requests_per_month': 1000
        })
    
    def _cleanup_old_requests(self, provider: str):
        """古いリクエスト履歴をクリーンアップ"""
        now = datetime.now()
        history = self.request_history[provider]
        
        # 1分以上古いリクエストを削除
        while history and (now - history[0]).total_seconds() > 60:
            history.popleft()
    
    def can_make_request(self, provider: str) -> bool:
        """リクエスト可能性チェック"""
        now = datetime.now()
        limits = self._get_limits(provider)
        
        # 履歴クリーンアップ
        self._cleanup_old_requests(provider)
        
        history = self.request_history[provider]
        
        # 分次制限チェック
        minute_requests = len([req for req in history 
                              if (now - req).total_seconds() <= 60])
        if minute_requests >= limits.get('requests_per_minute', 60):
            logging.warning(f"⚠️ {provider}: 分次制限に達しました ({minute_requests}/{limits.get('requests_per_minute', 60)})")
            return False
        
        # 日次制限チェック
        today = now.date()
        daily_requests = len([req for req in history 
                             if req.date() == today])
        if daily_requests >= limits.get('requests_per_day', 1000):
            logging.warning(f"⚠️ {provider}: 日次制限に達しました ({daily_requests}/{limits.get('requests_per_day', 1000)})")
            return False
        
        # 月次制限チェック
        current_month = now.replace(day=1).date()
        monthly_requests = len([req for req in history 
                               if req.date() >= current_month])
        if monthly_requests >= limits.get('requests_per_month', 10000):
            logging.warning(f"⚠️ {provider}: 月次制限に達しました ({monthly_requests}/{limits.get('requests_per_month', 10000)})")
            return False
        
        return True
    
    def record_request(self, provider: str):
        """リクエスト実行の記録"""
        now = datetime.now()
        self.request_history[provider].append(now)
        
        # 履歴が長くなりすぎないように制限（最大30日分）
        if len(self.request_history[provider]) > 50000:  # 概算で30日分
            # 古い半分を削除
            history = self.request_history[provider]
            self.request_history[provider] = deque(list(history)[len(history)//2:])
        
        logging.debug(f"📈 {provider}: リクエスト記録 ({now})")
    
    def get_daily_requests(self, provider: str) -> int:
        """日次リクエスト数取得"""
        today = datetime.now().date()
        history = self.request_history[provider]
        
        return len([req for req in history if req.date() == today])
    
    def get_monthly_requests(self, provider: str) -> int:
        """月次リクエスト数取得"""
        current_month = datetime.now().replace(day=1).date()
        history = self.request_history[provider]
        
        return len([req for req in history if req.date() >= current_month])
    
    def get_status(self, provider: str) -> Dict[str, any]:
        """プロバイダーの制限状況取得"""
        limits = self._get_limits(provider)
        
        # 現在の使用量
        daily_usage = self.get_daily_requests(provider)
        monthly_usage = self.get_monthly_requests(provider)
        
        # 分次使用量
        now = datetime.now()
        history = self.request_history[provider]
        minute_usage = len([req for req in history 
                           if (now - req).total_seconds() <= 60])
        
        return {
            'limits': limits,
            'usage': {
                'minute': minute_usage,
                'daily': daily_usage,
                'monthly': monthly_usage
            },
            'remaining': {
                'minute': max(0, limits.get('requests_per_minute', 60) - minute_usage),
                'daily': max(0, limits.get('requests_per_day', 1000) - daily_usage),
                'monthly': max(0, limits.get('requests_per_month', 10000) - monthly_usage)
            },
            'can_request': self.can_make_request(provider)
        }
    
    def get_next_available_time(self, provider: str) -> Optional[datetime]:
        """次にリクエスト可能な時刻を取得"""
        if self.can_make_request(provider):
            return datetime.now()
        
        limits = self._get_limits(provider)
        now = datetime.now()
        history = self.request_history[provider]
        
        # 分次制限による待機時間
        minute_requests = [req for req in history 
                          if (now - req).total_seconds() <= 60]
        if len(minute_requests) >= limits.get('requests_per_minute', 60):
            # 最古のリクエストから1分後
            oldest_in_minute = min(minute_requests)
            next_minute = oldest_in_minute + timedelta(minutes=1, seconds=1)
            return next_minute
        
        # 日次制限の場合は明日まで
        today = now.date()
        daily_requests = len([req for req in history if req.date() == today])
        if daily_requests >= limits.get('requests_per_day', 1000):
            tomorrow = datetime.combine(today + timedelta(days=1), datetime.min.time())
            return tomorrow
        
        # 月次制限の場合は来月まで
        current_month = now.replace(day=1).date()
        monthly_requests = len([req for req in history if req.date() >= current_month])
        if monthly_requests >= limits.get('requests_per_month', 10000):
            if now.month == 12:
                next_month = datetime(now.year + 1, 1, 1)
            else:
                next_month = datetime(now.year, now.month + 1, 1)
            return next_month
        
        return datetime.now()
    
    def get_all_status(self) -> Dict[str, Dict[str, any]]:
        """全プロバイダーの状況取得"""
        status = {}
        
        for provider in list(self.request_history.keys()) + list(self.default_limits.keys()):
            status[provider] = self.get_status(provider)
        
        return status
    
    def reset_daily_counters(self):
        """日次カウンターのリセット（通常は自動実行されるが手動実行も可能）"""
        today = datetime.now().date()
        if today > self.last_daily_reset:
            logging.info(f"📅 日次カウンターをリセット: {today}")
            self.last_daily_reset = today
    
    def reset_monthly_counters(self):
        """月次カウンターのリセット（通常は自動実行されるが手動実行も可能）"""
        current_month = datetime.now().replace(day=1).date()
        if current_month > self.last_monthly_reset:
            logging.info(f"📅 月次カウンターをリセット: {current_month}")
            self.last_monthly_reset = current_month