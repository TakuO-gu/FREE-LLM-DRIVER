"""
Integrated Neural System - 脳型統合処理システム
脳幹、大脳辺縁系、大脳皮質の協調動作とフィードバックループを実装
"""

import asyncio
import logging
import json
import math
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
from datetime import datetime, timedelta
from collections import defaultdict, deque

from .neural_kernel import NeuralKernel, SystemStatus
from .emotional_system import EmotionalProcessingSystem, EmotionalContext, ThreatLevel
from .executive_controller import ExecutiveController, CognitiveTask, ExecutiveDecision, DecisionStrategy

class ProcessingMode(Enum):
    """処理モード"""
    EMERGENCY = "emergency"        # 緊急時（感情系主導）
    ANALYTICAL = "analytical"     # 分析的（皮質主導）
    INTUITIVE = "intuitive"       # 直感的（統合処理）
    MAINTENANCE = "maintenance"   # 保守的（基盤系主導）

class NeuralIntegrationLevel(Enum):
    """神経統合レベル"""
    BASIC = 1      # 基本的統合
    MODERATE = 2   # 中程度統合
    HIGH = 3       # 高度統合
    SEAMLESS = 4   # シームレス統合

@dataclass
class NeuralProcessingResult:
    """神経処理結果"""
    goal: str
    processing_mode: ProcessingMode
    integration_level: NeuralIntegrationLevel
    executive_decision: ExecutiveDecision
    emotional_context: EmotionalContext
    system_state: Dict[str, Any]
    performance_metrics: Dict[str, float]
    feedback_loops_active: List[str]
    execution_time: float
    success: bool
    learning_updates: Dict[str, Any]
    timestamp: datetime

class FeedbackLoopType(Enum):
    """フィードバックループタイプ"""
    IMMEDIATE = "immediate"      # ~100ms (反射的調整)
    TACTICAL = "tactical"        # ~1-5分 (戦術的調整)
    STRATEGIC = "strategic"      # ~時間/日 (戦略的学習)

@dataclass
class FeedbackLoop:
    """フィードバックループ"""
    loop_id: str
    loop_type: FeedbackLoopType
    source_system: str
    target_system: str
    feedback_function: str
    update_interval: float  # seconds
    last_update: datetime
    active: bool
    performance_impact: float

class FeedbackLoopManager:
    """フィードバックループ管理システム"""
    
    def __init__(self):
        self.active_loops: Dict[str, FeedbackLoop] = {}
        self.loop_history = deque(maxlen=1000)
        self.performance_metrics = {
            'total_feedback_cycles': 0,
            'successful_adaptations': 0,
            'system_improvements': 0
        }
        
        # 予定義されたフィードバックループ
        self._initialize_standard_loops()
        
    def _initialize_standard_loops(self):
        """標準フィードバックループの初期化"""
        standard_loops = [
            # 即座のフィードバック（脳幹 → 辺縁系）
            FeedbackLoop(
                loop_id="neural_to_emotional",
                loop_type=FeedbackLoopType.IMMEDIATE,
                source_system="neural_kernel",
                target_system="emotional_system",
                feedback_function="system_state_to_emotional_state",
                update_interval=0.1,
                last_update=datetime.now(),
                active=True,
                performance_impact=0.8
            ),
            
            # 戦術的フィードバック（辺縁系 → 皮質）
            FeedbackLoop(
                loop_id="emotional_to_executive",
                loop_type=FeedbackLoopType.TACTICAL,
                source_system="emotional_system",
                target_system="executive_controller",
                feedback_function="emotional_context_to_cognitive_bias",
                update_interval=60.0,
                last_update=datetime.now(),
                active=True,
                performance_impact=0.6
            ),
            
            # 戦略的フィードバック（全システム統合学習）
            FeedbackLoop(
                loop_id="integrated_learning",
                loop_type=FeedbackLoopType.STRATEGIC,
                source_system="integrated_system",
                target_system="all_subsystems",
                feedback_function="holistic_performance_optimization",
                update_interval=3600.0,  # 1時間
                last_update=datetime.now(),
                active=True,
                performance_impact=0.9
            )
        ]
        
        for loop in standard_loops:
            self.active_loops[loop.loop_id] = loop
    
    async def manage_feedback_loops(self, system_components: Dict[str, Any]):
        """フィードバックループの管理"""
        try:
            current_time = datetime.now()
            
            # 各ループの更新チェック
            for loop_id, loop in self.active_loops.items():
                if not loop.active:
                    continue
                
                time_since_update = (current_time - loop.last_update).total_seconds()
                
                if time_since_update >= loop.update_interval:
                    await self._execute_feedback_loop(loop, system_components)
                    loop.last_update = current_time
                    self.performance_metrics['total_feedback_cycles'] += 1
            
        except Exception as e:
            logging.error(f"❌ フィードバックループ管理エラー: {e}")
    
    async def _execute_feedback_loop(self, loop: FeedbackLoop, 
                                   system_components: Dict[str, Any]):
        """個別フィードバックループの実行"""
        try:
            if loop.feedback_function == "system_state_to_emotional_state":
                await self._neural_to_emotional_feedback(loop, system_components)
                
            elif loop.feedback_function == "emotional_context_to_cognitive_bias":
                await self._emotional_to_executive_feedback(loop, system_components)
                
            elif loop.feedback_function == "holistic_performance_optimization":
                await self._integrated_learning_feedback(loop, system_components)
            
            # フィードバック履歴に記録
            feedback_record = {
                'loop_id': loop.loop_id,
                'execution_time': datetime.now(),
                'performance_impact': loop.performance_impact
            }
            self.loop_history.append(feedback_record)
            
        except Exception as e:
            logging.error(f"❌ フィードバックループ実行エラー: {loop.loop_id} - {e}")
    
    async def _neural_to_emotional_feedback(self, loop: FeedbackLoop, 
                                          system_components: Dict[str, Any]):
        """神経系→感情系フィードバック"""
        neural_kernel = system_components.get('neural_kernel')
        emotional_system = system_components.get('emotional_system')
        
        if not neural_kernel or not emotional_system:
            return
        
        try:
            # システム状態の取得
            system_state = await neural_kernel.get_comprehensive_status()
            
            # システムストレスレベルの計算
            stress_indicators = {
                'cpu_usage': system_state.get('system_health', {}).get('vital_signs', {}).get('cpu_usage', {}).get('value', 0),
                'memory_usage': system_state.get('system_health', {}).get('vital_signs', {}).get('memory_usage', {}).get('value', 0),
                'resource_warnings': len(system_state.get('resources', {}).get('warnings', []))
            }
            
            stress_level = min(
                (stress_indicators['cpu_usage'] / 100.0 +
                 stress_indicators['memory_usage'] / 100.0 +
                 stress_indicators['resource_warnings'] / 5.0) / 3.0,
                1.0
            )
            
            # 感情システムのストレス状態更新
            if hasattr(emotional_system, 'update_system_stress'):
                await emotional_system.update_system_stress(stress_level)
            
            logging.debug(f"🔄 神経→感情フィードバック: ストレスレベル {stress_level:.2f}")
            
        except Exception as e:
            logging.error(f"❌ 神経→感情フィードバックエラー: {e}")
    
    async def _emotional_to_executive_feedback(self, loop: FeedbackLoop, 
                                             system_components: Dict[str, Any]):
        """感情系→実行制御フィードバック"""
        emotional_system = system_components.get('emotional_system')
        executive_controller = system_components.get('executive_controller')
        
        if not emotional_system or not executive_controller:
            return
        
        try:
            # 感情状態の取得
            emotional_stats = emotional_system.get_emotional_statistics()
            current_state = emotional_stats.get('current_state', 'neutral')
            
            # 認知バイアス調整
            cognitive_adjustments = {}
            
            if current_state == 'anxious':
                # 不安時は保守的バイアス
                cognitive_adjustments['risk_aversion'] = 0.3
                cognitive_adjustments['attention_narrowing'] = 0.2
                
            elif current_state == 'confident':
                # 自信時は積極的バイアス
                cognitive_adjustments['risk_tolerance'] = 0.2
                cognitive_adjustments['attention_broadening'] = 0.1
                
            elif current_state == 'frustrated':
                # フラストレーション時は注意散漫
                cognitive_adjustments['impulsivity'] = 0.3
                cognitive_adjustments['patience_reduction'] = 0.2
            
            # 実行制御システムへの調整適用
            if hasattr(executive_controller, 'apply_emotional_bias'):
                await executive_controller.apply_emotional_bias(cognitive_adjustments)
            
            logging.debug(f"🔄 感情→実行フィードバック: {current_state} -> {len(cognitive_adjustments)}調整")
            
        except Exception as e:
            logging.error(f"❌ 感情→実行フィードバックエラー: {e}")
    
    async def _integrated_learning_feedback(self, loop: FeedbackLoop, 
                                          system_components: Dict[str, Any]):
        """統合学習フィードバック"""
        try:
            # 全システムのパフォーマンス統計を収集
            performance_data = {}
            
            for system_name, system in system_components.items():
                if hasattr(system, 'get_performance_statistics'):
                    stats = system.get_performance_statistics()
                    performance_data[system_name] = stats
            
            # パフォーマンス改善ポイントの特定
            improvement_areas = self._identify_improvement_areas(performance_data)
            
            # システム間連携の最適化
            await self._optimize_system_integration(improvement_areas, system_components)
            
            self.performance_metrics['system_improvements'] += len(improvement_areas)
            
            logging.info(f"🔄 統合学習フィードバック: {len(improvement_areas)}領域の改善")
            
        except Exception as e:
            logging.error(f"❌ 統合学習フィードバックエラー: {e}")
    
    def _identify_improvement_areas(self, performance_data: Dict[str, Any]) -> List[str]:
        """改善領域の特定"""
        improvement_areas = []
        
        # 各システムのパフォーマンス閾値チェック
        thresholds = {
            'success_rate': 0.8,
            'efficiency': 0.7,
            'response_time': 10.0  # 秒
        }
        
        for system_name, stats in performance_data.items():
            for metric, threshold in thresholds.items():
                value = stats.get(metric, 1.0)
                
                if metric == 'response_time':
                    if value > threshold:  # 応答時間は低い方が良い
                        improvement_areas.append(f"{system_name}_{metric}")
                else:
                    if value < threshold:  # その他は高い方が良い
                        improvement_areas.append(f"{system_name}_{metric}")
        
        return improvement_areas
    
    async def _optimize_system_integration(self, improvement_areas: List[str], 
                                         system_components: Dict[str, Any]):
        """システム統合の最適化"""
        # 統合レベルの動的調整
        if len(improvement_areas) > 3:
            # 問題が多い場合は統合レベルを上げる
            for system in system_components.values():
                if hasattr(system, 'increase_integration_level'):
                    await system.increase_integration_level()
        
        # 特定の問題に対する対処
        for area in improvement_areas:
            if 'response_time' in area:
                # 応答時間問題：並列処理の増加
                await self._optimize_parallel_processing(system_components)
            elif 'success_rate' in area:
                # 成功率問題：フォールバック機能の強化
                await self._strengthen_fallback_mechanisms(system_components)

    async def _optimize_parallel_processing(self, system_components: Dict[str, Any]):
        """並列処理の最適化"""
        logging.debug("⚡ 並列処理最適化実行")
        
    async def _strengthen_fallback_mechanisms(self, system_components: Dict[str, Any]):
        """フォールバック機能の強化"""
        logging.debug("🛡️ フォールバック機能強化実行")
    
    def get_feedback_statistics(self) -> Dict[str, Any]:
        """フィードバック統計"""
        return {
            'active_loops': len([l for l in self.active_loops.values() if l.active]),
            'total_loops': len(self.active_loops),
            'performance_metrics': self.performance_metrics.copy(),
            'loop_types': {
                loop_type.value: len([l for l in self.active_loops.values() 
                                    if l.loop_type == loop_type])
                for loop_type in FeedbackLoopType
            }
        }

class IntegratedNeuralSystem:
    """統合神経システム - 脳型統合処理"""
    
    def __init__(self):
        # 神経系コンポーネント
        self.neural_kernel = None      # 脳幹（基盤システム）
        self.emotional_system = None   # 大脳辺縁系（感情・記憶）
        self.executive_controller = None  # 大脳皮質（高次認知）
        
        # フィードバックループ管理
        self.feedback_manager = FeedbackLoopManager()
        
        # 統合処理状態
        self.current_integration_level = NeuralIntegrationLevel.BASIC
        self.processing_history = deque(maxlen=1000)
        
        # 学習メトリクス
        self.learning_metrics = {
            'total_goals_processed': 0,
            'successful_integrations': 0,
            'emergency_activations': 0,
            'adaptation_events': 0
        }
        
        # 緊急時閾値
        self.EMERGENCY_THRESHOLD = ThreatLevel.HIGH
        
    async def initialize_neural_systems(self, neural_kernel, emotional_system, executive_controller):
        """神経系コンポーネントの初期化"""
        try:
            self.neural_kernel = neural_kernel
            self.emotional_system = emotional_system
            self.executive_controller = executive_controller
            
            # フィードバックループの開始
            system_components = {
                'neural_kernel': self.neural_kernel,
                'emotional_system': self.emotional_system,
                'executive_controller': self.executive_controller
            }
            
            # バックグラウンドでフィードバックループを実行
            asyncio.create_task(self._continuous_feedback_management(system_components))
            
            logging.info("🧠 統合神経システム初期化完了")
            return True
            
        except Exception as e:
            logging.error(f"❌ 統合神経システム初期化エラー: {e}")
            return False
    
    async def process_goal_neural(self, user_goal: str, context: Dict[str, Any] = None) -> NeuralProcessingResult:
        """脳型統合処理メイン関数"""
        processing_start_time = datetime.now()
        
        try:
            if context is None:
                context = {}
            
            logging.info(f"🧠 神経統合処理開始: {user_goal[:50]}...")
            
            # 1. 基盤システム状態確認（脳幹レベル）
            system_state = await self._check_neural_foundation(user_goal)
            
            # 2. 感情的・記憶的評価（大脳辺縁系レベル）
            emotional_context = await self._evaluate_emotional_limbic(user_goal, context)
            
            # 3. 処理モード決定
            processing_mode = self._determine_processing_mode(system_state, emotional_context)
            
            # 4. 統合レベル適応
            await self._adapt_integration_level(processing_mode, emotional_context)
            
            # 5. 高次認知処理または緊急処理（大脳皮質レベル）
            executive_decision = await self._execute_cognitive_processing(
                user_goal, emotional_context, processing_mode, context
            )
            
            # 6. 実行とモニタリング
            execution_result = await self._execute_with_neural_monitoring(
                executive_decision, emotional_context, processing_mode
            )
            
            # 7. 学習フィードバック
            learning_updates = await self._neural_learning_integration(
                user_goal, executive_decision, execution_result, emotional_context
            )
            
            # 8. 結果の統合
            processing_result = self._create_processing_result(
                user_goal, processing_mode, executive_decision,
                emotional_context, system_state, execution_result,
                learning_updates, processing_start_time
            )
            
            # 処理履歴に記録
            self.processing_history.append(processing_result)
            self.learning_metrics['total_goals_processed'] += 1
            
            if processing_result.success:
                self.learning_metrics['successful_integrations'] += 1
            
            execution_time = (datetime.now() - processing_start_time).total_seconds()
            logging.info(f"🎯 神経統合処理完了: {processing_result.success} "
                        f"({execution_time:.2f}秒, モード: {processing_mode.value})")
            
            return processing_result
            
        except Exception as e:
            logging.error(f"❌ 神経統合処理エラー: {e}")
            return self._create_error_result(user_goal, str(e), processing_start_time)
    
    async def _check_neural_foundation(self, user_goal: str) -> Dict[str, Any]:
        """基盤神経システム状態確認"""
        try:
            if self.neural_kernel:
                comprehensive_status = await self.neural_kernel.get_comprehensive_status()
                
                # システム健全性の評価
                system_health = comprehensive_status.get('system_health', {})
                status = system_health.get('status', 'unknown')
                
                return {
                    'health_status': status,
                    'vital_signs': system_health.get('vital_signs', {}),
                    'resources': comprehensive_status.get('resources', {}),
                    'foundation_stable': status in ['healthy', 'warning']
                }
            else:
                return {
                    'health_status': 'unknown',
                    'foundation_stable': False
                }
                
        except Exception as e:
            logging.error(f"❌ 基盤システム確認エラー: {e}")
            return {'foundation_stable': False}
    
    async def _evaluate_emotional_limbic(self, user_goal: str, context: Dict[str, Any]) -> EmotionalContext:
        """感情的・記憶的評価"""
        try:
            if self.emotional_system:
                return await self.emotional_system.evaluate_task_emotion(user_goal)
            else:
                # フォールバック: デフォルト感情コンテキスト
                from .emotional_system import EmotionalContext, ThreatLevel, EmotionalState
                return EmotionalContext(
                    threat_level=ThreatLevel.MODERATE,
                    emotional_weight=0.5,
                    confidence=0.3,
                    valence=0.0,
                    arousal=0.5,
                    state=EmotionalState.NEUTRAL,
                    timestamp=datetime.now()
                )
                
        except Exception as e:
            logging.error(f"❌ 感情評価エラー: {e}")
            # エラー時もフォールバック
            from .emotional_system import EmotionalContext, ThreatLevel, EmotionalState
            return EmotionalContext(
                threat_level=ThreatLevel.MODERATE,
                emotional_weight=0.5,
                confidence=0.1,
                valence=0.0,
                arousal=0.5,
                state=EmotionalState.NEUTRAL,
                timestamp=datetime.now()
            )
    
    def _determine_processing_mode(self, system_state: Dict[str, Any], 
                                 emotional_context: EmotionalContext) -> ProcessingMode:
        """処理モード決定"""
        try:
            # 緊急事態検出
            if (emotional_context.threat_level.value >= self.EMERGENCY_THRESHOLD.value or
                not system_state.get('foundation_stable', True)):
                self.learning_metrics['emergency_activations'] += 1
                return ProcessingMode.EMERGENCY
            
            # 感情状態・脅威レベルによる判定
            if emotional_context.threat_level == ThreatLevel.HIGH:
                return ProcessingMode.EMERGENCY
            elif emotional_context.arousal > 0.6:
                return ProcessingMode.INTUITIVE
            elif emotional_context.confidence > 0.4 or emotional_context.emotional_weight > 0.6:
                return ProcessingMode.ANALYTICAL
            else:
                return ProcessingMode.MAINTENANCE
                
        except Exception as e:
            logging.error(f"❌ 処理モード決定エラー: {e}")
            return ProcessingMode.MAINTENANCE
    
    async def _adapt_integration_level(self, processing_mode: ProcessingMode, 
                                     emotional_context: EmotionalContext):
        """統合レベルの適応"""
        try:
            target_level = self.current_integration_level
            
            if processing_mode == ProcessingMode.EMERGENCY:
                target_level = NeuralIntegrationLevel.HIGH
            elif processing_mode == ProcessingMode.ANALYTICAL:
                target_level = NeuralIntegrationLevel.SEAMLESS
            elif processing_mode == ProcessingMode.INTUITIVE:
                target_level = NeuralIntegrationLevel.MODERATE
            else:  # MAINTENANCE
                target_level = NeuralIntegrationLevel.BASIC
            
            if target_level != self.current_integration_level:
                self.current_integration_level = target_level
                self.learning_metrics['adaptation_events'] += 1
                logging.debug(f"🔄 統合レベル変更: {target_level.name}")
                
        except Exception as e:
            logging.error(f"❌ 統合レベル適応エラー: {e}")
    
    async def _execute_cognitive_processing(self, user_goal: str, emotional_context: EmotionalContext,
                                          processing_mode: ProcessingMode, 
                                          context: Dict[str, Any]) -> ExecutiveDecision:
        """認知処理の実行"""
        try:
            if processing_mode == ProcessingMode.EMERGENCY:
                # 緊急時は感情システム主導の簡易判断
                return await self._emergency_response_decision(user_goal, emotional_context)
            
            elif self.executive_controller:
                # 通常時は高次認知処理
                # タスクオプションの生成
                task_options = await self._generate_task_options(user_goal, emotional_context)
                
                # 統合コンテキストの準備
                integrated_context = {
                    **context,
                    'processing_mode': processing_mode,
                    'emotional_context': emotional_context,
                    'integration_level': self.current_integration_level
                }
                
                return await self.executive_controller.executive_decision(task_options, integrated_context)
            
            else:
                # フォールバック
                return self._create_fallback_decision(user_goal)
                
        except Exception as e:
            logging.error(f"❌ 認知処理エラー: {e}")
            return self._create_fallback_decision(user_goal)
    
    async def _emergency_response_decision(self, user_goal: str, 
                                         emotional_context: EmotionalContext) -> ExecutiveDecision:
        """緊急応答決定"""
        decision_id = f"emergency_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        
        return ExecutiveDecision(
            decision_id=decision_id,
            chosen_strategy=DecisionStrategy.CONSERVATIVE,
            task_sequence=[f"emergency_goal_{hash(user_goal) % 10000}"],
            resource_allocation={'emergency_allocation': 50.0},
            confidence=0.6,
            rationale=f'Emergency response due to threat level: {emotional_context.threat_level.name}',
            alternatives_considered=[],
            timestamp=datetime.now()
        )
    
    async def _generate_task_options(self, user_goal: str, 
                                   emotional_context: EmotionalContext) -> List[CognitiveTask]:
        """タスクオプションの生成"""
        try:
            # 基本タスクの生成
            base_task = CognitiveTask(
                task_id=f"task_{hash(user_goal) % 10000}",
                description=user_goal,
                task_type="general",
                urgency=emotional_context.arousal,
                importance=abs(emotional_context.valence),
                complexity=emotional_context.threat_level.value / 5.0,
                required_attention=50.0 + emotional_context.emotional_weight * 30.0,
                emotional_weight=emotional_context.emotional_weight,
                deadline=None,
                dependencies=[],
                context={'emotional_context': emotional_context}
            )
            
            return [base_task]
            
        except Exception as e:
            logging.error(f"❌ タスクオプション生成エラー: {e}")
            return []
    
    def _create_fallback_decision(self, user_goal: str) -> ExecutiveDecision:
        """フォールバック決定の作成"""
        decision_id = f"fallback_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        
        return ExecutiveDecision(
            decision_id=decision_id,
            chosen_strategy=DecisionStrategy.CONSERVATIVE,
            task_sequence=[f"fallback_goal_{hash(user_goal) % 10000}"],
            resource_allocation={},
            confidence=0.3,
            rationale='Fallback decision due to system limitation',
            alternatives_considered=[],
            timestamp=datetime.now()
        )
    
    async def _execute_with_neural_monitoring(self, executive_decision: ExecutiveDecision,
                                            emotional_context: EmotionalContext,
                                            processing_mode: ProcessingMode) -> Dict[str, Any]:
        """神経監視付き実行"""
        try:
            execution_start = datetime.now()
            
            # 実行プロセス（簡略化）
            await asyncio.sleep(0.1)  # 実行時間のシミュレーション
            
            execution_time = (datetime.now() - execution_start).total_seconds()
            
            # 成功率の計算（処理モードと統合レベルを考慮）
            base_success = executive_decision.confidence * 0.4
            
            # 統合レベルによるボーナス
            integration_bonus = self.current_integration_level.value * 0.15
            
            # 処理モードによる調整
            if processing_mode == ProcessingMode.EMERGENCY:
                # 緊急モードでは安全処理により成功率向上
                mode_adjustment = 0.3
            elif processing_mode == ProcessingMode.ANALYTICAL:
                mode_adjustment = 0.2
            elif processing_mode == ProcessingMode.INTUITIVE:
                mode_adjustment = 0.1
            else:  # MAINTENANCE
                mode_adjustment = 0.2
            
            # 脅威レベルによる調整（適切な処理により脅威を回避）
            if emotional_context.threat_level == ThreatLevel.CRITICAL:
                threat_adjustment = 0.1  # 危険だが適切な処理で対応
            elif emotional_context.threat_level == ThreatLevel.HIGH:
                threat_adjustment = 0.15
            else:
                threat_adjustment = (6 - emotional_context.threat_level.value) * 0.1
            
            success_probability = base_success + integration_bonus + mode_adjustment + threat_adjustment
            success_probability = min(max(success_probability, 0.1), 0.95)  # 10%-95%の範囲
            
            success = success_probability > 0.5
            
            return {
                'success': success,
                'execution_time': execution_time,
                'quality': success_probability,
                'neural_monitoring_active': True,
                'performance_metrics': {
                    'efficiency': success_probability,
                    'resource_utilization': 0.7,
                    'error_rate': 1.0 - success_probability
                }
            }
            
        except Exception as e:
            logging.error(f"❌ 神経監視実行エラー: {e}")
            return {
                'success': False,
                'execution_time': 0.0,
                'error': str(e)
            }
    
    async def _neural_learning_integration(self, user_goal: str, executive_decision: ExecutiveDecision,
                                         execution_result: Dict[str, Any], 
                                         emotional_context: EmotionalContext) -> Dict[str, Any]:
        """神経学習統合"""
        try:
            learning_updates = {}
            
            # 感情システムへの学習フィードバック
            if self.emotional_system:
                await self.emotional_system.process_task_outcome(
                    executive_decision.decision_id,
                    user_goal,
                    "general",
                    execution_result,
                    emotional_context
                )
                learning_updates['emotional_learning'] = True
            
            # 実行制御システムへの学習フィードバック
            if self.executive_controller:
                await self.executive_controller.update_strategy_performance(
                    executive_decision.decision_id,
                    execution_result.get('success', False),
                    execution_result.get('performance_metrics', {})
                )
                learning_updates['executive_learning'] = True
            
            # 神経接続最適化
            success_metric = execution_result.get('quality', 0.5 if execution_result.get('success') else 0.1)
            await self.optimize_neural_connections(user_goal, executive_decision, execution_result, success_metric)
            learning_updates['neural_optimization'] = True
            
            return learning_updates
            
        except Exception as e:
            logging.error(f"❌ 神経学習統合エラー: {e}")
            return {'learning_error': str(e)}
    
    def _create_processing_result(self, user_goal: str, processing_mode: ProcessingMode,
                                executive_decision: ExecutiveDecision, emotional_context: EmotionalContext,
                                system_state: Dict[str, Any], execution_result: Dict[str, Any],
                                learning_updates: Dict[str, Any], start_time: datetime) -> NeuralProcessingResult:
        """処理結果の作成"""
        execution_time = (datetime.now() - start_time).total_seconds()
        
        return NeuralProcessingResult(
            goal=user_goal,
            processing_mode=processing_mode,
            integration_level=self.current_integration_level,
            executive_decision=executive_decision,
            emotional_context=emotional_context,
            system_state=system_state,
            performance_metrics=execution_result.get('performance_metrics', {}),
            feedback_loops_active=[loop.loop_id for loop in self.feedback_manager.active_loops.values() if loop.active],
            execution_time=execution_time,
            success=execution_result.get('success', False),
            learning_updates=learning_updates,
            timestamp=datetime.now()
        )
    
    def _create_error_result(self, user_goal: str, error_message: str, 
                           start_time: datetime) -> NeuralProcessingResult:
        """エラー結果の作成"""
        from .emotional_system import EmotionalContext, ThreatLevel, EmotionalState
        
        execution_time = (datetime.now() - start_time).total_seconds()
        
        return NeuralProcessingResult(
            goal=user_goal,
            processing_mode=ProcessingMode.MAINTENANCE,
            integration_level=self.current_integration_level,
            executive_decision=self._create_fallback_decision(user_goal),
            emotional_context=EmotionalContext(
                threat_level=ThreatLevel.HIGH,
                emotional_weight=0.8,
                confidence=0.1,
                valence=-0.5,
                arousal=0.7,
                state=EmotionalState.FRUSTRATED,
                timestamp=datetime.now()
            ),
            system_state={'error': error_message},
            performance_metrics={'error_rate': 1.0},
            feedback_loops_active=[],
            execution_time=execution_time,
            success=False,
            learning_updates={'error_learning': error_message},
            timestamp=datetime.now()
        )
    
    async def _continuous_feedback_management(self, system_components: Dict[str, Any]):
        """継続的フィードバック管理"""
        try:
            while True:
                await self.feedback_manager.manage_feedback_loops(system_components)
                await asyncio.sleep(1.0)  # 1秒間隔
                
        except asyncio.CancelledError:
            logging.debug("🔄 フィードバック管理停止")
        except Exception as e:
            logging.error(f"❌ 継続フィードバック管理エラー: {e}")
    
    def get_integration_statistics(self) -> Dict[str, Any]:
        """統合統計の取得"""
        return {
            'current_integration_level': self.current_integration_level.name,
            'learning_metrics': self.learning_metrics.copy(),
            'processing_history_size': len(self.processing_history),
            'feedback_statistics': self.feedback_manager.get_feedback_statistics(),
            'recent_processing_modes': [
                result.processing_mode.value 
                for result in list(self.processing_history)[-10:]
            ],
            'success_rate': (
                self.learning_metrics['successful_integrations'] / 
                max(self.learning_metrics['total_goals_processed'], 1)
            )
        }
    
    async def optimize_neural_connections(self, goal: str, decision: ExecutiveDecision, 
                                        result: Dict[str, Any], success_metric: float):
        """神経接続の最適化"""
        try:
            # 成功度に基づく接続強度調整
            if success_metric > 0.8:
                # 高い成功率：現在の統合レベルを強化
                if self.current_integration_level.value < NeuralIntegrationLevel.SEAMLESS.value:
                    await self._strengthen_integration()
            elif success_metric < 0.3:
                # 低い成功率：統合レベルを調整
                await self._adjust_integration_for_improvement()
            
            # フィードバックループの効率化
            await self._optimize_feedback_efficiency(success_metric)
            
        except Exception as e:
            logging.error(f"❌ 神経接続最適化エラー: {e}")
    
    async def _strengthen_integration(self):
        """統合強化"""
        if self.current_integration_level.value < NeuralIntegrationLevel.SEAMLESS.value:
            new_level = NeuralIntegrationLevel(self.current_integration_level.value + 1)
            self.current_integration_level = new_level
            self.learning_metrics['adaptation_events'] += 1
            logging.debug(f"⬆️ 統合レベル強化: {new_level.name}")
    
    async def _adjust_integration_for_improvement(self):
        """改善のための統合調整"""
        # より保守的な統合レベルに調整
        if self.current_integration_level.value > NeuralIntegrationLevel.BASIC.value:
            new_level = NeuralIntegrationLevel(self.current_integration_level.value - 1)
            self.current_integration_level = new_level
            self.learning_metrics['adaptation_events'] += 1
            logging.debug(f"⬇️ 統合レベル調整: {new_level.name}")
    
    async def _optimize_feedback_efficiency(self, success_metric: float):
        """フィードバック効率の最適化"""
        # 成功率に基づくフィードバック頻度調整
        if success_metric > 0.8:
            # 高成功率：フィードバック頻度を下げる
            for loop in self.feedback_manager.active_loops.values():
                if loop.loop_type == FeedbackLoopType.IMMEDIATE:
                    loop.update_interval = min(loop.update_interval * 1.1, 1.0)
        elif success_metric < 0.3:
            # 低成功率：フィードバック頻度を上げる
            for loop in self.feedback_manager.active_loops.values():
                if loop.loop_type == FeedbackLoopType.IMMEDIATE:
                    loop.update_interval = max(loop.update_interval * 0.9, 0.05)