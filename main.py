#!/usr/bin/env python3
"""
Free LLM Driver - メインエントリーポイント
無料オンラインLLM + Open Interpreter実装

使用例:
    python main.py --goal "Pythonでファイル管理ツールを作成"
    python main.py --interactive
    python main.py --status
"""

import asyncio
import argparse
import logging
import os
import sys
import yaml
from pathlib import Path
from typing import Dict, Any

# プロジェクトルートをパスに追加
sys.path.insert(0, str(Path(__file__).parent))

from src.llm.provider_manager import LLMProviderManager
from src.agent.orchestrator import LightweightOrchestrator
from src.utils.quota_tracker import QuotaTracker
from src.utils.auto_optimizer import AutoOptimizer
from src.core.neural_kernel import NeuralKernel
from src.core.emotional_system import EmotionalProcessingSystem
from src.core.executive_controller import ExecutiveController
from src.core.integrated_neural_system import IntegratedNeuralSystem
from dotenv import load_dotenv

class FreeLLMDriver:
    """Free LLM Driver メインアプリケーション"""
    
    def __init__(self, config_dir: str = "config"):
        self.config_dir = config_dir
        self.config = {}
        self.llm_manager = None
        self.orchestrator = None
        self.quota_tracker = None
        self.optimizer = None
        self.neural_kernel = None
        self.emotional_system = None
        self.executive_controller = None
        self.integrated_neural_system = None
        
        # ログ設定
        self._setup_logging()
        
        # 環境変数読み込み
        load_dotenv()
        
        # ログディレクトリ作成
        os.makedirs('logs', exist_ok=True)
    
    def _setup_logging(self):
        """ログ設定"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(sys.stdout),
                logging.FileHandler('logs/free_llm_driver.log', encoding='utf-8')
            ]
        )
        
        # 外部ライブラリのログレベルを下げる
        logging.getLogger('httpx').setLevel(logging.WARNING)
        logging.getLogger('openai').setLevel(logging.WARNING)
        logging.getLogger('google').setLevel(logging.WARNING)
    
    async def initialize(self) -> bool:
        """システム初期化"""
        try:
            logging.info("🚀 Free LLM Driver を初期化中...")
            
            # 設定ファイル読み込み
            if not self._load_config():
                return False
            
            # コンポーネント初期化
            self.quota_tracker = QuotaTracker()
            self.llm_manager = LLMProviderManager(self.config)
            
            if not await self.llm_manager.initialize():
                logging.error("❌ LLMプロバイダー管理システムの初期化に失敗")
                return False
            
            # オーケストレーター初期化
            orchestrator_config = self.config.get('optimization', {})
            self.orchestrator = LightweightOrchestrator(self.llm_manager, orchestrator_config)
            
            # 最適化エンジン初期化
            self.optimizer = AutoOptimizer(self.quota_tracker)
            
            # Neural Kernel初期化と起動
            self.neural_kernel = NeuralKernel()
            await self.neural_kernel.start_neural_kernel()
            logging.info("🧠 Neural Kernel 起動完了")
            
            # Emotional Processing System初期化
            self.emotional_system = EmotionalProcessingSystem()
            logging.info("💭 Emotional Processing System 初期化完了")
            
            # Executive Controller初期化
            self.executive_controller = ExecutiveController()
            logging.info("🎯 Executive Controller 初期化完了")
            
            # Integrated Neural System初期化と統合
            self.integrated_neural_system = IntegratedNeuralSystem()
            neural_integration_success = await self.integrated_neural_system.initialize_neural_systems(
                self.neural_kernel, self.emotional_system, self.executive_controller
            )
            
            if neural_integration_success:
                logging.info("🧠 統合神経システム初期化完了")
            else:
                logging.warning("⚠️ 統合神経システム初期化に一部問題が発生")
            
            logging.info("✅ システム初期化完了")
            return True
            
        except Exception as e:
            logging.error(f"❌ 初期化エラー: {e}")
            return False
    
    def _load_config(self) -> bool:
        """設定ファイル読み込み"""
        try:
            # プロバイダー設定
            providers_path = os.path.join(self.config_dir, 'providers.yaml')
            if os.path.exists(providers_path):
                with open(providers_path, 'r', encoding='utf-8') as f:
                    providers_config = yaml.safe_load(f)
                    self.config.update(providers_config)
                logging.info("✅ プロバイダー設定を読み込み")
            else:
                logging.warning(f"⚠️ プロバイダー設定ファイルが見つかりません: {providers_path}")
            
            # 制限設定
            limits_path = os.path.join(self.config_dir, 'limits.yaml')
            if os.path.exists(limits_path):
                with open(limits_path, 'r', encoding='utf-8') as f:
                    limits_config = yaml.safe_load(f)
                    self.config.update(limits_config)
                logging.info("✅ 制限設定を読み込み")
            else:
                logging.warning(f"⚠️ 制限設定ファイルが見つかりません: {limits_path}")
            
            return True
            
        except Exception as e:
            logging.error(f"❌ 設定ファイル読み込みエラー: {e}")
            return False
    
    async def execute_goal(self, goal: str) -> None:
        """目標実行"""
        try:
            logging.info(f"🎯 目標実行: {goal}")
            
            # 感情的評価による優先度調整
            if self.emotional_system:
                emotional_context = await self.emotional_system.evaluate_task_emotion(goal, "goal_execution")
                logging.info(f"💭 感情的評価: {emotional_context.state.value} "
                           f"(脅威レベル: {emotional_context.threat_level.name}, "
                           f"信頼度: {emotional_context.confidence:.2f})")
            
            # 実行前の最適化チェック
            recommendations = self.optimizer.generate_optimization_recommendations()
            if recommendations:
                logging.info("💡 最適化推奨事項があります:")
                for rec in recommendations[:3]:  # 上位3つ
                    logging.info(f"  - {rec.provider}: {rec.action} ({rec.priority})")
            
            # 目標実行
            result = await self.orchestrator.execute_goal(goal)
            
            # 感情的結果処理
            if self.emotional_system and hasattr(result, 'results') and result.results:
                for execution_result in result.results:
                    task_result = {
                        'success': execution_result.status.value == 'completed',
                        'execution_time': execution_result.execution_time,
                        'quality': 0.8 if execution_result.status.value == 'completed' else 0.2,
                        'task_type': 'goal_execution'
                    }
                    await self.emotional_system.process_task_outcome(
                        execution_result.task_id, goal, "goal_execution",
                        task_result, emotional_context
                    )
            
            # 使用量記録
            for execution_result in result.results:
                self.quota_tracker.log_request(
                    provider=execution_result.provider_used or 'unknown',
                    task_type='goal_execution',
                    success=execution_result.status.value == 'completed',
                    response_time=execution_result.execution_time
                )
            
            # 結果表示
            self._display_result(result)
            
        except Exception as e:
            logging.error(f"❌ 目標実行エラー: {e}")
    
    def _display_result(self, result) -> None:
        """結果表示"""
        print("\n" + "="*60)
        print("🎯 実行結果")
        print("="*60)
        
        print(f"目標: {result.goal}")
        print(f"総タスク数: {result.total_tasks}")
        print(f"完了タスク: {result.completed_tasks}")
        print(f"失敗タスク: {result.failed_tasks}")
        print(f"実行時間: {result.total_time:.1f}秒")
        print(f"成功: {'✅' if result.success else '❌'}")
        
        if result.summary:
            print(f"\nサマリー:\n{result.summary}")
        
        # 詳細結果（成功したもののみ）
        successful_results = [r for r in result.results if r.status.value == 'completed']
        if successful_results:
            print(f"\n📋 実行結果詳細 ({len(successful_results)}件):")
            for i, exec_result in enumerate(successful_results[:3], 1):  # 最大3件表示
                print(f"\n{i}. タスクID: {exec_result.task_id}")
                output = exec_result.output[:200] + "..." if len(exec_result.output) > 200 else exec_result.output
                print(f"   出力: {output}")
        
        print("\n" + "="*60)
    
    async def run_interactive_mode(self) -> None:
        """インタラクティブモード"""
        print("🚀 Free LLM Driver - インタラクティブモード")
        print("コマンド: /help, /status, /quit")
        print("-" * 50)
        
        while True:
            try:
                user_input = input("\n💭 目標を入力してください: ").strip()
                
                if not user_input:
                    continue
                    
                # コマンド処理
                if user_input.startswith('/'):
                    if user_input == '/quit' or user_input == '/exit':
                        print("👋 終了します")
                        break
                    elif user_input == '/help':
                        self._show_help()
                    elif user_input == '/status':
                        await self._show_status()
                    elif user_input == '/optimize':
                        await self._show_optimization()
                    elif user_input == '/neural':
                        await self._show_neural_status()
                    elif user_input == '/emotion':
                        await self._show_emotional_status()
                    elif user_input == '/brain':
                        await self._show_integrated_brain_status()
                    else:
                        print("❓ 未知のコマンドです。/help で使用可能コマンドを確認")
                    continue
                
                # 目標実行
                await self.execute_goal(user_input)
                
            except KeyboardInterrupt:
                print("\n👋 終了します")
                break
            except Exception as e:
                logging.error(f"❌ インタラクティブモードエラー: {e}")
    
    def _show_help(self) -> None:
        """ヘルプ表示"""
        print("""
📚 Free LLM Driver ヘルプ

使用可能コマンド:
  /help      - このヘルプを表示
  /status    - システム状況を表示
  /optimize  - 最適化状況を表示
  /neural    - Neural Kernel状況を表示
  /emotion   - 感情システム状況を表示
  /brain     - 統合脳システム状況を表示
  /quit      - 終了

使用例:
  💭 Pythonでファイル管理ツールを作成
  💭 データ分析用のグラフを生成
  💭 ウェブページの要約を作成
        """)
    
    async def _show_status(self) -> None:
        """ステータス表示"""
        try:
            print("\n📊 システム状況")
            print("-" * 40)
            
            # プロバイダー状況
            provider_status = self.llm_manager.get_provider_status()
            print("\n🔌 プロバイダー状況:")
            for provider, status in provider_status.items():
                available = "✅" if status['available'] else "❌"
                print(f"  {provider}: {available} (今日: {status['requests_today']}リクエスト)")
            
            # オーケストレーター統計
            orch_stats = self.orchestrator.get_orchestrator_stats()
            print(f"\n🎯 実行統計:")
            print(f"  総ワークフロー: {orch_stats['total_workflows']}")
            print(f"  成功率: {orch_stats['success_rate']:.1f}%")
            print(f"  平均実行時間: {orch_stats['average_execution_time']:.1f}秒")
            
            # 使用量サマリー
            usage_summary = self.quota_tracker.get_usage_summary()
            print(f"\n📈 使用量サマリー:")
            print(f"  総リクエスト: {usage_summary['total_requests']}")
            
            if usage_summary['providers']:
                print("  プロバイダー別:")
                for provider, stats in usage_summary['providers'].items():
                    print(f"    {provider}: {stats['requests']}リクエスト (成功率: {stats['success_rate']:.1f}%)")
            
        except Exception as e:
            logging.error(f"❌ ステータス表示エラー: {e}")
    
    async def _show_optimization(self) -> None:
        """最適化状況表示"""
        try:
            print("\n🔧 最適化状況")
            print("-" * 40)
            
            # パフォーマンス分析
            analysis = self.optimizer.analyze_current_performance()
            health_emoji = "✅" if analysis['overall_health'] == 'good' else "⚠️" if analysis['overall_health'] == 'warning' else "❌"
            print(f"\n{health_emoji} システム全体: {analysis['overall_health']}")
            
            # 推奨事項
            recommendations = self.optimizer.generate_optimization_recommendations()
            if recommendations:
                print("\n💡 推奨事項:")
                for rec in recommendations[:5]:  # 上位5つ
                    priority_emoji = "🚨" if rec.priority == "緊急" else "⚠️" if rec.priority == "高" else "💡"
                    print(f"  {priority_emoji} {rec.provider}: {rec.action}")
                    print(f"     理由: {rec.reason}")
            
            # 使用量予測
            forecast = self.optimizer.get_usage_forecast(7)
            if forecast:
                print("\n📊 7日間使用量予測:")
                for provider, pred in forecast.items():
                    if pred:
                        usage_rate = pred['projected_usage_rate']
                        emoji = "🚨" if usage_rate >= 0.9 else "⚠️" if usage_rate >= 0.7 else "✅"
                        print(f"  {emoji} {provider}: {usage_rate*100:.1f}% 使用予想")
            
        except Exception as e:
            logging.error(f"❌ 最適化状況表示エラー: {e}")
    
    async def _show_neural_status(self) -> None:
        """Neural Kernel状況表示"""
        try:
            print("\n🧠 Neural Kernel 状況")
            print("-" * 40)
            
            if not self.neural_kernel:
                print("❌ Neural Kernel が初期化されていません")
                return
            
            # 包括的なシステム状態取得
            status = await self.neural_kernel.get_comprehensive_status()
            
            # Neural Kernel基本統計
            neural_stats = status.get('neural_kernel', {})
            running_status = "🟢 稼働中" if neural_stats.get('running') else "🔴 停止中"
            print(f"\nカーネル状態: {running_status}")
            
            uptime_seconds = neural_stats.get('uptime_seconds', 0)
            uptime_minutes = uptime_seconds / 60
            print(f"稼働時間: {uptime_minutes:.1f}分")
            print(f"ヘルスチェック回数: {neural_stats.get('total_health_checks', 0)}")
            print(f"緊急対応回数: {neural_stats.get('emergency_activations', 0)}")
            print(f"現在の状態: {neural_stats.get('current_status', 'unknown')}")
            
            # システムヘルス
            system_health = status.get('system_health', {})
            health_status = system_health.get('status', 'unknown')
            health_emoji = "🟢" if health_status == 'healthy' else "🟡" if health_status == 'warning' else "🔴"
            print(f"\n{health_emoji} システムヘルス: {health_status}")
            
            # バイタルサイン
            vital_signs = system_health.get('vital_signs', {})
            if vital_signs:
                print("\n📊 バイタルサイン:")
                for name, vs in vital_signs.items():
                    status_emoji = "🟢" if vs['status'] == 'healthy' else "🟡" if vs['status'] == 'warning' else "🔴"
                    print(f"  {status_emoji} {name}: {vs['value']:.1f}{vs['unit']} ({vs['status']})")
            
            # アラート
            alerts = system_health.get('alerts', [])
            if alerts:
                print("\n🚨 アラート:")
                for alert in alerts:
                    print(f"  - {alert}")
            
            # リソース使用量
            resources = status.get('resources', {})
            resource_warnings = resources.get('warnings', [])
            if resource_warnings:
                print("\n⚠️ リソース警告:")
                for warning in resource_warnings:
                    print(f"  - {warning}")
            else:
                print("\n✅ リソース使用量: 正常範囲内")
            
            # トレンド
            trend = system_health.get('trend', {})
            if trend.get('trend'):
                trend_emoji = "📈" if trend['trend'] == 'improving' else "📉" if trend['trend'] == 'degrading' else "📊"
                print(f"\n{trend_emoji} トレンド: {trend['trend']}")
            
        except Exception as e:
            logging.error(f"❌ Neural Kernel状況表示エラー: {e}")
    
    async def _show_emotional_status(self) -> None:
        """感情システム状況表示"""
        try:
            print("\n💭 感情処理システム状況")
            print("-" * 40)
            
            if not self.emotional_system:
                print("❌ 感情処理システムが初期化されていません")
                return
            
            # 感情システム統計
            stats = self.emotional_system.get_emotional_statistics()
            
            # 現在の感情状態
            current_state = stats.get('current_state', 'unknown')
            state_emoji = {
                'neutral': '😐',
                'positive': '😊',
                'negative': '😔',
                'anxious': '😰',
                'confident': '😎',
                'frustrated': '😤'
            }.get(current_state, '❓')
            
            print(f"\n{state_emoji} 現在の感情状態: {current_state}")
            
            # 脅威検知システム
            threat_stats = stats.get('threat_detector', {})
            learned_threats = threat_stats.get('learned_threats', 0)
            print(f"\n🔍 脅威検知システム:")
            print(f"  学習済み脅威パターン: {learned_threats}個")
            
            # 記憶システム
            memory_stats = stats.get('memory_manager', {})
            print(f"\n🧠 記憶システム:")
            print(f"  エピソード記憶: {memory_stats.get('episodic_memory_size', 0)}件")
            print(f"  意味記憶パターン: {memory_stats.get('semantic_patterns', 0)}個")
            print(f"  作業記憶: {memory_stats.get('working_memory_size', 0)}件")
            print(f"  総合成功率: {memory_stats.get('success_rate', 0.0):.1%}")
            print(f"  総経験数: {memory_stats.get('total_experiences', 0)}件")
            print(f"  記憶統合回数: {memory_stats.get('memory_consolidations', 0)}回")
            
            # 報酬システム
            reward_stats = stats.get('reward_system', {})
            print(f"\n🎯 報酬システム:")
            print(f"  報酬履歴: {reward_stats.get('reward_history_size', 0)}件")
            print(f"  期待報酬パターン: {reward_stats.get('expected_rewards', 0)}個")
            
            # 感情履歴
            emotional_history_size = stats.get('emotional_history_size', 0)
            print(f"\n📊 感情履歴: {emotional_history_size}件記録")
            
            # 最近の感情変化（可能であれば）
            if hasattr(self.emotional_system, 'emotional_history') and self.emotional_system.emotional_history:
                recent_emotions = list(self.emotional_system.emotional_history)[-5:]
                print(f"\n📈 最近の感情変化:")
                for i, emotion in enumerate(recent_emotions):
                    emotion_emoji = {
                        'neutral': '😐',
                        'positive': '😊', 
                        'negative': '😔',
                        'anxious': '😰',
                        'confident': '😎',
                        'frustrated': '😤'
                    }.get(emotion.state.value, '❓')
                    print(f"  {i+1}. {emotion_emoji} {emotion.state.value} "
                          f"(脅威: {emotion.threat_level.name}, 信頼度: {emotion.confidence:.2f})")
            
        except Exception as e:
            logging.error(f"❌ 感情システム状況表示エラー: {e}")
    
    async def _show_integrated_brain_status(self) -> None:
        """統合脳システム状況表示"""
        try:
            print("\n🧠 統合脳システム状況")
            print("-" * 40)
            
            if not self.integrated_neural_system:
                print("❌ 統合神経システムが初期化されていません")
                return
            
            # 統合統計の取得
            integration_stats = self.integrated_neural_system.get_integration_statistics()
            
            # 基本情報
            integration_level = integration_stats.get('current_integration_level', 'unknown')
            integration_emoji = {
                'BASIC': '🟡',
                'MODERATE': '🟠', 
                'HIGH': '🔴',
                'SEAMLESS': '🟢'
            }.get(integration_level, '❓')
            
            print(f"\n{integration_emoji} 統合レベル: {integration_level}")
            print(f"📊 処理履歴: {integration_stats.get('processing_history_size', 0)}件")
            print(f"📈 成功率: {integration_stats.get('success_rate', 0):.1%}")
            
            # 学習メトリクス
            learning_metrics = integration_stats.get('learning_metrics', {})
            print(f"\n📚 学習統計:")
            print(f"  総処理目標数: {learning_metrics.get('total_goals_processed', 0)}")
            print(f"  成功統合数: {learning_metrics.get('successful_integrations', 0)}")
            print(f"  緊急発動回数: {learning_metrics.get('emergency_activations', 0)}")
            print(f"  適応イベント: {learning_metrics.get('adaptation_events', 0)}")
            
            # フィードバックループ統計
            feedback_stats = integration_stats.get('feedback_statistics', {})
            active_loops = feedback_stats.get('active_loops', 0)
            total_loops = feedback_stats.get('total_loops', 0)
            
            print(f"\n🔄 フィードバックループ:")
            print(f"  アクティブループ: {active_loops}/{total_loops}")
            
            loop_types = feedback_stats.get('loop_types', {})
            for loop_type, count in loop_types.items():
                loop_emoji = {
                    'immediate': '⚡',
                    'tactical': '🎯',
                    'strategic': '🧠'
                }.get(loop_type, '🔄')
                print(f"  {loop_emoji} {loop_type}: {count}個")
            
            # 最近の処理モード
            recent_modes = integration_stats.get('recent_processing_modes', [])
            if recent_modes:
                print(f"\n🎭 最近の処理モード:")
                mode_counts = {}
                for mode in recent_modes[-10:]:  # 最新10件
                    mode_counts[mode] = mode_counts.get(mode, 0) + 1
                
                for mode, count in sorted(mode_counts.items(), key=lambda x: x[1], reverse=True):
                    mode_emoji = {
                        'emergency': '🚨',
                        'analytical': '🔍',
                        'intuitive': '💡',
                        'maintenance': '🔧'
                    }.get(mode, '❓')
                    print(f"  {mode_emoji} {mode}: {count}回")
            
            # システム統合健全性評価
            success_rate = integration_stats.get('success_rate', 0)
            if success_rate > 0.8:
                health_status = "✅ 統合脳システムは良好に動作しています"
            elif success_rate > 0.6:
                health_status = "⚠️ 統合脳システムは安定していますが改善余地があります"
            elif success_rate > 0.3:
                health_status = "🚨 統合脳システムの最適化が必要です"
            else:
                health_status = "💀 統合脳システムに重大な問題があります"
            
            print(f"\n{health_status}")
            
            # 推奨事項
            if active_loops < total_loops:
                print(f"\n💡 推奨事項:")
                print(f"  - 非アクティブなフィードバックループ（{total_loops - active_loops}個）の確認")
            
            if learning_metrics.get('emergency_activations', 0) > learning_metrics.get('total_goals_processed', 1) * 0.1:
                print(f"  - 緊急発動が頻繁です。システム負荷の軽減を検討してください")
            
            if success_rate < 0.7:
                print(f"  - 成功率が低いです。統合レベルの調整や学習データの見直しを推奨")
                
        except Exception as e:
            logging.error(f"❌ 統合脳システム状況表示エラー: {e}")
    
    async def cleanup(self):
        """クリーンアップ処理"""
        try:
            if self.neural_kernel:
                await self.neural_kernel.stop_neural_kernel()
                logging.info("🧠 Neural Kernel 停止完了")
        except Exception as e:
            logging.error(f"❌ クリーンアップエラー: {e}")

async def main():
    """メイン関数"""
    parser = argparse.ArgumentParser(
        description='Free LLM Driver - 無料オンラインLLM + Open Interpreter'
    )
    parser.add_argument('--goal', '-g', type=str, help='実行する目標')
    parser.add_argument('--interactive', '-i', action='store_true', help='インタラクティブモード')
    parser.add_argument('--status', '-s', action='store_true', help='システム状況表示')
    parser.add_argument('--optimize', '-o', action='store_true', help='最適化状況表示')
    parser.add_argument('--config', '-c', type=str, default='config', help='設定ディレクトリ')
    
    args = parser.parse_args()
    
    # アプリケーション初期化
    app = FreeLLMDriver(config_dir=args.config)
    
    if not await app.initialize():
        logging.error("❌ システム初期化に失敗しました")
        sys.exit(1)
    
    try:
        if args.status:
            await app._show_status()
        elif args.optimize:
            await app._show_optimization()
        elif args.goal:
            await app.execute_goal(args.goal)
        elif args.interactive:
            await app.run_interactive_mode()
        else:
            # デフォルトはインタラクティブモード
            print("使用方法: python main.py --help")
            print("インタラクティブモードを開始するには: python main.py -i")
            
    except KeyboardInterrupt:
        logging.info("👋 ユーザーによって中断されました")
    except Exception as e:
        logging.error(f"❌ 実行エラー: {e}")
        sys.exit(1)
    finally:
        # クリーンアップ処理
        if 'app' in locals():
            await app.cleanup()

if __name__ == "__main__":
    asyncio.run(main())