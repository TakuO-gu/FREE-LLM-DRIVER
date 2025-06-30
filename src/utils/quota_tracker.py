"""
使用量追跡システム
API使用量とコストの詳細な監視・分析
"""

import json
import logging
import os
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from collections import defaultdict
from dataclasses import dataclass, asdict

@dataclass
class UsageRecord:
    """使用量記録"""
    timestamp: datetime
    provider: str
    task_type: str
    tokens_used: int
    response_time: float
    success: bool
    cost_estimate: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """辞書形式に変換"""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UsageRecord':
        """辞書から復元"""
        data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        return cls(**data)

class QuotaTracker:
    """使用量追跡管理"""
    
    def __init__(self, storage_path: str = "logs/usage_data.json"):
        self.storage_path = storage_path
        self.usage_records: List[UsageRecord] = []
        self.daily_usage: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))
        self.monthly_usage: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))
        
        # コスト推定（無料サービスなので基本0だが、参考用）
        self.cost_estimates = {
            'google_gemini': 0.0,  # 無料
            'groq_llama': 0.0,     # 無料
            'together_ai': 0.0     # 無料（制限内）
        }
        
        # 保存ディレクトリの作成
        self._ensure_storage_dir()
        
        # データの読み込み
        self._load_usage_data()
    
    def _ensure_storage_dir(self):
        """保存ディレクトリの確保"""
        storage_dir = os.path.dirname(self.storage_path)
        if storage_dir and not os.path.exists(storage_dir):
            os.makedirs(storage_dir)
    
    def _load_usage_data(self):
        """使用量データの読み込み"""
        try:
            if os.path.exists(self.storage_path):
                with open(self.storage_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                self.usage_records = [UsageRecord.from_dict(record) for record in data.get('records', [])]
                
                # 日次・月次使用量の再構築
                self._rebuild_usage_summaries()
                
                logging.info(f"📊 {len(self.usage_records)}件の使用量データを読み込み")
                
        except Exception as e:
            logging.error(f"❌ 使用量データ読み込みエラー: {e}")
            self.usage_records = []
    
    def _save_usage_data(self):
        """使用量データの保存"""
        try:
            data = {
                'records': [record.to_dict() for record in self.usage_records],
                'last_updated': datetime.now().isoformat()
            }
            
            with open(self.storage_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            logging.error(f"❌ 使用量データ保存エラー: {e}")
    
    def _rebuild_usage_summaries(self):
        """使用量サマリーの再構築"""
        self.daily_usage.clear()
        self.monthly_usage.clear()
        
        for record in self.usage_records:
            date_key = record.timestamp.date().isoformat()
            month_key = record.timestamp.strftime('%Y-%m')
            
            self.daily_usage[date_key][record.provider] += 1
            self.monthly_usage[month_key][record.provider] += 1
    
    def log_request(
        self,
        provider: str,
        task_type: str = "general",
        tokens_used: int = 0,
        response_time: float = 0.0,
        success: bool = True
    ):
        """リクエストの記録"""
        
        # 使用量記録作成
        record = UsageRecord(
            timestamp=datetime.now(),
            provider=provider,
            task_type=task_type,
            tokens_used=tokens_used,
            response_time=response_time,
            success=success,
            cost_estimate=self.cost_estimates.get(provider, 0.0)
        )
        
        # 記録追加
        self.usage_records.append(record)
        
        # サマリー更新
        date_key = record.timestamp.date().isoformat()
        month_key = record.timestamp.strftime('%Y-%m')
        
        self.daily_usage[date_key][provider] += 1
        self.monthly_usage[month_key][provider] += 1
        
        # 定期保存（10件ごと）
        if len(self.usage_records) % 10 == 0:
            self._save_usage_data()
        
        logging.debug(f"📈 使用量記録: {provider} ({task_type})")
    
    def get_daily_usage(self, provider: str, date: Optional[datetime] = None) -> Dict[str, Any]:
        """日次使用量取得"""
        target_date = date or datetime.now()
        date_key = target_date.date().isoformat()
        
        requests_count = self.daily_usage[date_key].get(provider, 0)
        
        # 詳細統計
        day_records = [
            r for r in self.usage_records 
            if r.provider == provider and r.timestamp.date() == target_date.date()
        ]
        
        if not day_records:
            return {
                'date': date_key,
                'provider': provider,
                'requests': 0,
                'tokens': 0,
                'success_rate': 0.0,
                'avg_response_time': 0.0
            }
        
        total_tokens = sum(r.tokens_used for r in day_records)
        successful_requests = sum(1 for r in day_records if r.success)
        success_rate = (successful_requests / len(day_records) * 100) if day_records else 0
        avg_response_time = sum(r.response_time for r in day_records) / len(day_records)
        
        return {
            'date': date_key,
            'provider': provider,
            'requests': requests_count,
            'tokens': total_tokens,
            'success_rate': round(success_rate, 1),
            'avg_response_time': round(avg_response_time, 2),
            'cost_estimate': sum(r.cost_estimate for r in day_records)
        }
    
    def get_monthly_usage(self, provider: str, month: Optional[datetime] = None) -> Dict[str, Any]:
        """月次使用量取得"""
        target_month = month or datetime.now()
        month_key = target_month.strftime('%Y-%m')
        
        requests_count = self.monthly_usage[month_key].get(provider, 0)
        
        # 詳細統計
        month_records = [
            r for r in self.usage_records 
            if r.provider == provider and r.timestamp.strftime('%Y-%m') == month_key
        ]
        
        if not month_records:
            return {
                'month': month_key,
                'provider': provider,
                'requests': 0,
                'tokens': 0,
                'success_rate': 0.0,
                'avg_response_time': 0.0
            }
        
        total_tokens = sum(r.tokens_used for r in month_records)
        successful_requests = sum(1 for r in month_records if r.success)
        success_rate = (successful_requests / len(month_records) * 100) if month_records else 0
        avg_response_time = sum(r.response_time for r in month_records) / len(month_records)
        
        return {
            'month': month_key,
            'provider': provider,
            'requests': requests_count,
            'tokens': total_tokens,
            'success_rate': round(success_rate, 1),
            'avg_response_time': round(avg_response_time, 2),
            'cost_estimate': sum(r.cost_estimate for r in month_records)
        }
    
    def get_usage_summary(self) -> Dict[str, Any]:
        """使用量全体サマリー"""
        if not self.usage_records:
            return {
                'total_requests': 0,
                'providers': {},
                'task_types': {},
                'time_range': {}
            }
        
        # プロバイダー別統計
        provider_stats = defaultdict(lambda: {'requests': 0, 'success': 0, 'tokens': 0})
        task_type_stats = defaultdict(int)
        
        for record in self.usage_records:
            provider_stats[record.provider]['requests'] += 1
            provider_stats[record.provider]['tokens'] += record.tokens_used
            if record.success:
                provider_stats[record.provider]['success'] += 1
            
            task_type_stats[record.task_type] += 1
        
        # 成功率計算
        for provider, stats in provider_stats.items():
            stats['success_rate'] = (stats['success'] / stats['requests'] * 100) if stats['requests'] > 0 else 0
        
        # 時間範囲
        earliest = min(r.timestamp for r in self.usage_records)
        latest = max(r.timestamp for r in self.usage_records)
        
        return {
            'total_requests': len(self.usage_records),
            'providers': dict(provider_stats),
            'task_types': dict(task_type_stats),
            'time_range': {
                'earliest': earliest.isoformat(),
                'latest': latest.isoformat(),
                'days': (latest.date() - earliest.date()).days + 1
            }
        }
    
    def get_quota_status(self, provider: str, limits: Dict[str, int]) -> Dict[str, Any]:
        """クォータ状況の取得"""
        today_usage = self.get_daily_usage(provider)
        month_usage = self.get_monthly_usage(provider)
        
        daily_limit = limits.get('requests_per_day', 1000)
        monthly_limit = limits.get('requests_per_month', 10000)
        
        daily_remaining = max(0, daily_limit - today_usage['requests'])
        monthly_remaining = max(0, monthly_limit - month_usage['requests'])
        
        daily_usage_percent = (today_usage['requests'] / daily_limit * 100) if daily_limit > 0 else 0
        monthly_usage_percent = (month_usage['requests'] / monthly_limit * 100) if monthly_limit > 0 else 0
        
        return {
            'provider': provider,
            'daily': {
                'used': today_usage['requests'],
                'limit': daily_limit,
                'remaining': daily_remaining,
                'usage_percent': round(daily_usage_percent, 1)
            },
            'monthly': {
                'used': month_usage['requests'],
                'limit': monthly_limit,
                'remaining': monthly_remaining,
                'usage_percent': round(monthly_usage_percent, 1)
            }
        }
    
    def get_performance_trends(self, days: int = 7) -> Dict[str, Any]:
        """パフォーマンストレンド分析"""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        recent_records = [r for r in self.usage_records if r.timestamp >= cutoff_date]
        
        if not recent_records:
            return {'message': '十分なデータがありません'}
        
        # 日別統計
        daily_stats = defaultdict(lambda: {'requests': 0, 'success': 0, 'avg_response_time': 0.0})
        
        for record in recent_records:
            date_key = record.timestamp.date().isoformat()
            daily_stats[date_key]['requests'] += 1
            if record.success:
                daily_stats[date_key]['success'] += 1
            
        # 成功率計算
        for date_key, stats in daily_stats.items():
            if stats['requests'] > 0:
                stats['success_rate'] = round(stats['success'] / stats['requests'] * 100, 1)
        
        return {
            'period_days': days,
            'total_requests': len(recent_records),
            'daily_breakdown': dict(daily_stats)
        }
    
    def export_usage_report(self, output_path: str = "logs/usage_report.json"):
        """使用量レポートのエクスポート"""
        try:
            report = {
                'generated_at': datetime.now().isoformat(),
                'summary': self.get_usage_summary(),
                'recent_trends': self.get_performance_trends(30),  # 30日間
                'provider_details': {}
            }
            
            # プロバイダー別詳細
            providers = set(r.provider for r in self.usage_records)
            for provider in providers:
                report['provider_details'][provider] = {
                    'daily': self.get_daily_usage(provider),
                    'monthly': self.get_monthly_usage(provider)
                }
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            
            logging.info(f"📊 使用量レポートをエクスポート: {output_path}")
            return output_path
            
        except Exception as e:
            logging.error(f"❌ レポートエクスポートエラー: {e}")
            return None
    
    def cleanup_old_records(self, days_to_keep: int = 90):
        """古い記録のクリーンアップ"""
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        
        original_count = len(self.usage_records)
        self.usage_records = [r for r in self.usage_records if r.timestamp >= cutoff_date]
        
        removed_count = original_count - len(self.usage_records)
        
        if removed_count > 0:
            # サマリーの再構築
            self._rebuild_usage_summaries()
            self._save_usage_data()
            
            logging.info(f"🗑️ {removed_count}件の古い記録を削除 ({days_to_keep}日以前)")
        
        return removed_count
    
    def force_save(self):
        """強制保存"""
        self._save_usage_data()
        logging.info("💾 使用量データを強制保存")