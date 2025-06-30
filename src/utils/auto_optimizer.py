"""
自動最適化システム
使用状況に基づくプロバイダー選択とパフォーマンス最適化
"""

import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum

from .quota_tracker import QuotaTracker

class OptimizationStrategy(Enum):
    """最適化戦略"""
    COST_EFFICIENT = "cost_efficient"      # コスト効率重視
    PERFORMANCE = "performance"             # パフォーマンス重視
    RELIABILITY = "reliability"             # 信頼性重視
    BALANCED = "balanced"                   # バランス重視

@dataclass
class OptimizationRecommendation:
    """最適化推奨事項"""
    provider: str
    action: str
    reason: str
    priority: str
    impact_estimate: str

class AutoOptimizer:
    """自動最適化エンジン"""
    
    def __init__(self, quota_tracker: QuotaTracker):
        self.quota_tracker = quota_tracker
        self.optimization_strategy = OptimizationStrategy.BALANCED
        
        # 最適化閾値設定
        self.thresholds = {
            'quota_warning': 0.8,      # 80%使用で警告
            'quota_critical': 0.95,    # 95%使用で緊急
            'success_rate_min': 0.85,  # 最小成功率85%
            'response_time_max': 10.0, # 最大レスポンス時間10秒
            'performance_degradation': 0.2  # 20%パフォーマンス低下で警告
        }
        
        # プロバイダー特性定義
        self.provider_characteristics = {
            'google_gemini': {
                'speed': 'medium',
                'reliability': 'high',
                'daily_limit': 1500,
                'monthly_limit': 45000,
                'best_for': ['complex_reasoning', 'general', 'analysis']
            },
            'groq_llama': {
                'speed': 'very_high',
                'reliability': 'high',
                'daily_limit': 14400,
                'monthly_limit': 432000,
                'best_for': ['code_generation', 'simple_task']
            },
            'together_ai': {
                'speed': 'medium',
                'reliability': 'medium',
                'daily_limit': 6,
                'monthly_limit': 200,
                'best_for': ['simple_task', 'backup']
            }
        }
    
    def analyze_current_performance(self) -> Dict[str, Any]:
        """現在のパフォーマンス分析"""
        
        analysis = {
            'overall_health': 'good',
            'provider_status': {},
            'bottlenecks': [],
            'recommendations': []
        }
        
        # プロバイダー別分析
        for provider, characteristics in self.provider_characteristics.items():
            provider_analysis = self._analyze_provider_performance(provider, characteristics)
            analysis['provider_status'][provider] = provider_analysis
            
            # 問題の特定
            if provider_analysis['status'] == 'warning':
                analysis['bottlenecks'].append(f"{provider}: {provider_analysis['issue']}")
            elif provider_analysis['status'] == 'critical':
                analysis['bottlenecks'].append(f"{provider}: {provider_analysis['issue']} (緊急)")
                analysis['overall_health'] = 'critical'
        
        # 全体的な健全性判定
        warning_count = sum(1 for status in analysis['provider_status'].values() if status['status'] == 'warning')
        critical_count = sum(1 for status in analysis['provider_status'].values() if status['status'] == 'critical')
        
        if critical_count > 0:
            analysis['overall_health'] = 'critical'
        elif warning_count > 1:
            analysis['overall_health'] = 'warning'
        
        return analysis
    
    def _analyze_provider_performance(self, provider: str, characteristics: Dict[str, Any]) -> Dict[str, Any]:
        """プロバイダー別パフォーマンス分析"""
        
        # 使用量状況
        daily_usage = self.quota_tracker.get_daily_usage(provider)
        monthly_usage = self.quota_tracker.get_monthly_usage(provider)
        
        daily_limit = characteristics.get('daily_limit', 1000)
        monthly_limit = characteristics.get('monthly_limit', 10000)
        
        daily_usage_rate = daily_usage['requests'] / daily_limit
        monthly_usage_rate = monthly_usage['requests'] / monthly_limit
        
        analysis = {
            'provider': provider,
            'status': 'good',
            'issue': None,
            'daily_usage_rate': round(daily_usage_rate, 3),
            'monthly_usage_rate': round(monthly_usage_rate, 3),
            'success_rate': daily_usage.get('success_rate', 100),
            'avg_response_time': daily_usage.get('avg_response_time', 0),
            'recommendations': []
        }
        
        # クォータ状況チェック
        if monthly_usage_rate >= self.thresholds['quota_critical']:
            analysis['status'] = 'critical'
            analysis['issue'] = '月次クォータ限界'
            analysis['recommendations'].append('使用量を大幅に削減するか、別のプロバイダーに切り替える')
            
        elif daily_usage_rate >= self.thresholds['quota_critical']:
            analysis['status'] = 'critical'
            analysis['issue'] = '日次クォータ限界'
            analysis['recommendations'].append('今日の使用を停止し、明日まで待機')
            
        elif monthly_usage_rate >= self.thresholds['quota_warning']:
            analysis['status'] = 'warning'
            analysis['issue'] = '月次クォータ警告'
            analysis['recommendations'].append('月末まで使用量を制限')
            
        elif daily_usage_rate >= self.thresholds['quota_warning']:
            analysis['status'] = 'warning'
            analysis['issue'] = '日次クォータ警告'
            analysis['recommendations'].append('今日の使用量を制限')
        
        # パフォーマンスチェック
        if analysis['success_rate'] < self.thresholds['success_rate_min'] * 100:
            if analysis['status'] == 'good':
                analysis['status'] = 'warning'
                analysis['issue'] = f'成功率低下 ({analysis["success_rate"]:.1f}%)'
            analysis['recommendations'].append('エラー原因を調査し、別のプロバイダーを検討')
        
        if analysis['avg_response_time'] > self.thresholds['response_time_max']:
            if analysis['status'] == 'good':
                analysis['status'] = 'warning'
                analysis['issue'] = f'レスポンス時間遅延 ({analysis["avg_response_time"]:.1f}s)'
            analysis['recommendations'].append('より高速なプロバイダーの使用を検討')
        
        return analysis
    
    def get_provider_recommendations(self, task_type: str = "general") -> List[str]:
        """タスクタイプに基づくプロバイダー推奨順序"""
        
        performance_analysis = self.analyze_current_performance()
        
        # 利用可能なプロバイダーをフィルタリング
        available_providers = []
        
        for provider, analysis in performance_analysis['provider_status'].items():
            if analysis['status'] != 'critical':
                # タスクタイプとの適合性スコア計算
                characteristics = self.provider_characteristics[provider]
                task_fit_score = self._calculate_task_fit_score(task_type, characteristics)
                
                # パフォーマンススコア計算
                performance_score = self._calculate_performance_score(analysis)
                
                # 総合スコア
                total_score = task_fit_score * 0.6 + performance_score * 0.4
                
                available_providers.append((provider, total_score, analysis))
        
        # スコア順にソート
        available_providers.sort(key=lambda x: x[1], reverse=True)
        
        return [provider for provider, _, _ in available_providers]
    
    def _calculate_task_fit_score(self, task_type: str, characteristics: Dict[str, Any]) -> float:
        """タスクフィットスコア計算"""
        best_for = characteristics.get('best_for', [])
        
        if task_type in best_for:
            return 1.0
        elif 'general' in best_for or task_type == 'general':
            return 0.7
        else:
            return 0.4
    
    def _calculate_performance_score(self, analysis: Dict[str, Any]) -> float:
        """パフォーマンススコア計算"""
        score = 1.0
        
        # 使用量ペナルティ
        if analysis['monthly_usage_rate'] > 0.8:
            score *= 0.5
        elif analysis['monthly_usage_rate'] > 0.6:
            score *= 0.7
        elif analysis['monthly_usage_rate'] > 0.4:
            score *= 0.9
        
        if analysis['daily_usage_rate'] > 0.8:
            score *= 0.3
        elif analysis['daily_usage_rate'] > 0.6:
            score *= 0.6
        elif analysis['daily_usage_rate'] > 0.4:
            score *= 0.8
        
        # 成功率ボーナス
        success_rate = analysis['success_rate'] / 100
        score *= success_rate
        
        # レスポンス時間ペナルティ
        response_time = analysis['avg_response_time']
        if response_time > 5:
            score *= 0.7
        elif response_time > 2:
            score *= 0.9
        
        return max(0.1, score)  # 最小値0.1
    
    def generate_optimization_recommendations(self) -> List[OptimizationRecommendation]:
        """最適化推奨事項の生成"""
        
        recommendations = []
        analysis = self.analyze_current_performance()
        
        for provider, provider_analysis in analysis['provider_status'].items():
            
            if provider_analysis['status'] == 'critical':
                recommendations.append(
                    OptimizationRecommendation(
                        provider=provider,
                        action="使用停止",
                        reason=provider_analysis['issue'],
                        priority="緊急",
                        impact_estimate="即座にクォータ問題を回避"
                    )
                )
                
            elif provider_analysis['status'] == 'warning':
                if 'クォータ' in provider_analysis['issue']:
                    recommendations.append(
                        OptimizationRecommendation(
                            provider=provider,
                            action="使用量制限",
                            reason=provider_analysis['issue'],
                            priority="高",
                            impact_estimate="クォータ超過を防止"
                        )
                    )
                else:
                    recommendations.append(
                        OptimizationRecommendation(
                            provider=provider,
                            action="パフォーマンス調査",
                            reason=provider_analysis['issue'],
                            priority="中",
                            impact_estimate="安定性向上"
                        )
                    )
        
        # 全体的な推奨事項
        if analysis['overall_health'] == 'critical':
            recommendations.insert(0,
                OptimizationRecommendation(
                    provider="システム全体",
                    action="緊急メンテナンス",
                    reason="複数のプロバイダーで問題発生",
                    priority="緊急",
                    impact_estimate="システム安定性の回復"
                )
            )
        
        return recommendations
    
    def optimize_provider_selection(self, current_selection: Dict[str, str]) -> Dict[str, str]:
        """プロバイダー選択の最適化"""
        
        optimized_selection = current_selection.copy()
        
        # タスクタイプ別に最適なプロバイダーを提案
        task_types = ['code_generation', 'complex_reasoning', 'simple_task', 'general']
        
        for task_type in task_types:
            recommended_providers = self.get_provider_recommendations(task_type)
            
            if recommended_providers and recommended_providers[0] != current_selection.get(task_type):
                optimized_selection[task_type] = recommended_providers[0]
                logging.info(f"🔧 {task_type}の推奨プロバイダーを{recommended_providers[0]}に変更")
        
        return optimized_selection
    
    def get_usage_forecast(self, days_ahead: int = 7) -> Dict[str, Any]:
        """使用量予測"""
        
        forecast = {}
        
        for provider in self.provider_characteristics.keys():
            # 過去の使用パターンから予測
            recent_usage = self.quota_tracker.get_performance_trends(days=7)
            
            if 'daily_breakdown' in recent_usage:
                daily_breakdown = recent_usage['daily_breakdown']
                
                if daily_breakdown:
                    # 単純な平均ベース予測
                    avg_daily_requests = sum(
                        day_data.get('requests', 0) 
                        for day_data in daily_breakdown.values()
                    ) / len(daily_breakdown)
                    
                    projected_usage = avg_daily_requests * days_ahead
                    
                    characteristics = self.provider_characteristics[provider]
                    monthly_limit = characteristics.get('monthly_limit', 10000)
                    
                    current_monthly = self.quota_tracker.get_monthly_usage(provider)['requests']
                    projected_monthly_usage = current_monthly + projected_usage
                    
                    usage_rate = projected_monthly_usage / monthly_limit
                    
                    forecast[provider] = {
                        'current_monthly_usage': current_monthly,
                        'projected_additional_usage': int(projected_usage),
                        'projected_monthly_total': int(projected_monthly_usage),
                        'monthly_limit': monthly_limit,
                        'projected_usage_rate': round(usage_rate, 3),
                        'days_until_limit': self._calculate_days_until_limit(provider, avg_daily_requests),
                        'recommendation': self._get_usage_recommendation(usage_rate)
                    }
        
        return forecast
    
    def _calculate_days_until_limit(self, provider: str, avg_daily_requests: float) -> Optional[int]:
        """制限到達までの日数計算"""
        
        if avg_daily_requests <= 0:
            return None
        
        characteristics = self.provider_characteristics[provider]
        monthly_limit = characteristics.get('monthly_limit', 10000)
        current_monthly = self.quota_tracker.get_monthly_usage(provider)['requests']
        
        remaining_requests = monthly_limit - current_monthly
        
        if remaining_requests <= 0:
            return 0
        
        days_until_limit = remaining_requests / avg_daily_requests
        
        return int(days_until_limit) if days_until_limit > 0 else 0
    
    def _get_usage_recommendation(self, usage_rate: float) -> str:
        """使用量推奨メッセージ"""
        
        if usage_rate >= 1.0:
            return "制限超過予想 - 使用量を大幅に削減してください"
        elif usage_rate >= 0.9:
            return "制限接近 - 使用量を制限してください"
        elif usage_rate >= 0.7:
            return "使用量注意 - 計画的な使用を推奨"
        elif usage_rate >= 0.5:
            return "適度な使用量 - 継続可能"
        else:
            return "余裕あり - 追加使用可能"
    
    def set_optimization_strategy(self, strategy: OptimizationStrategy):
        """最適化戦略の設定"""
        self.optimization_strategy = strategy
        logging.info(f"🎯 最適化戦略を{strategy.value}に設定")
    
    def generate_daily_report(self) -> str:
        """日次最適化レポート生成"""
        
        analysis = self.analyze_current_performance()
        recommendations = self.generate_optimization_recommendations()
        forecast = self.get_usage_forecast(7)
        
        report = "# 日次最適化レポート\n\n"
        report += f"生成日時: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        # 全体状況
        report += f"## システム状況: {analysis['overall_health'].upper()}\n\n"
        
        # プロバイダー状況
        report += "## プロバイダー状況\n\n"
        for provider, status in analysis['provider_status'].items():
            status_emoji = "✅" if status['status'] == 'good' else "⚠️" if status['status'] == 'warning' else "❌"
            report += f"{status_emoji} **{provider}**: {status['status']}"
            if status['issue']:
                report += f" - {status['issue']}"
            report += "\n"
        
        # 推奨事項
        if recommendations:
            report += "\n## 推奨事項\n\n"
            for rec in recommendations:
                priority_emoji = "🚨" if rec.priority == "緊急" else "⚠️" if rec.priority == "高" else "💡"
                report += f"{priority_emoji} **{rec.provider}**: {rec.action} - {rec.reason}\n"
        
        # 使用量予測
        report += "\n## 7日間使用量予測\n\n"
        for provider, pred in forecast.items():
            if pred:
                usage_rate = pred['projected_usage_rate']
                emoji = "🚨" if usage_rate >= 0.9 else "⚠️" if usage_rate >= 0.7 else "✅"
                report += f"{emoji} **{provider}**: {usage_rate*100:.1f}% ({pred['projected_monthly_total']}/{pred['monthly_limit']})\n"
        
        return report