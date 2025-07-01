"""
Executive Controller System - 前頭前皮質を模倣した高次認知制御システム
作業記憶、注意管理、競合解決、メタ認知的監視機能を統合
"""

import asyncio
import logging
import heapq
import math
from typing import Dict, Any, List, Optional, Tuple, Union
from dataclasses import dataclass, asdict
from enum import Enum
from datetime import datetime, timedelta
from collections import defaultdict, deque
import json

class CognitiveLoadLevel(Enum):
    """認知負荷レベル"""
    LOW = 1
    MODERATE = 2
    HIGH = 3
    OVERLOAD = 4

class AttentionType(Enum):
    """注意の種類"""
    FOCUSED = "focused"        # 集中的注意
    DIVIDED = "divided"        # 分割注意
    SUSTAINED = "sustained"    # 持続的注意
    SELECTIVE = "selective"    # 選択的注意

class DecisionStrategy(Enum):
    """意思決定戦略"""
    RATIONAL = "rational"      # 合理的分析
    INTUITIVE = "intuitive"    # 直感的判断
    HYBRID = "hybrid"          # 混合型
    EMOTIONAL = "emotional"    # 感情主導
    CONSERVATIVE = "conservative"  # 保守的

@dataclass
class CognitiveTask:
    """認知タスク"""
    task_id: str
    description: str
    task_type: str
    urgency: float  # 0-1
    importance: float  # 0-1
    complexity: float  # 0-1
    required_attention: float  # 0-100
    emotional_weight: float  # 0-1
    deadline: Optional[datetime]
    dependencies: List[str]
    context: Dict[str, Any]

@dataclass
class AttentionResource:
    """注意リソース"""
    total_capacity: float
    allocated: float
    available: float
    efficiency: float  # 現在の効率
    fatigue_level: float  # 疲労度

@dataclass
class ExecutiveDecision:
    """実行決定"""
    decision_id: str
    chosen_strategy: DecisionStrategy
    task_sequence: List[str]
    resource_allocation: Dict[str, float]
    confidence: float
    rationale: str
    alternatives_considered: List[Dict[str, Any]]
    timestamp: datetime

class WorkingMemory:
    """作業記憶システム"""
    
    def __init__(self, capacity: int = 7):  # Miller's magic number ±2
        self.capacity = capacity
        self.phonological_loop = deque(maxlen=capacity)  # 言語情報
        self.visuospatial_sketchpad = deque(maxlen=capacity)  # 視空間情報
        self.episodic_buffer = deque(maxlen=capacity)  # エピソード情報
        self.central_executive_state = {}
        
        # 作業記憶の統計
        self.usage_stats = {
            'total_items_processed': 0,
            'current_load': 0,
            'peak_load': 0,
            'interference_events': 0
        }
    
    def add_item(self, item: Any, memory_type: str = "episodic") -> bool:
        """作業記憶への項目追加"""
        try:
            current_time = datetime.now()
            memory_item = {
                'content': item,
                'timestamp': current_time,
                'access_count': 0,
                'importance': getattr(item, 'importance', 0.5)
            }
            
            if memory_type == "phonological":
                if len(self.phonological_loop) >= self.capacity:
                    self._handle_capacity_overflow("phonological")
                self.phonological_loop.append(memory_item)
                
            elif memory_type == "visuospatial":
                if len(self.visuospatial_sketchpad) >= self.capacity:
                    self._handle_capacity_overflow("visuospatial")
                self.visuospatial_sketchpad.append(memory_item)
                
            else:  # episodic
                if len(self.episodic_buffer) >= self.capacity:
                    self._handle_capacity_overflow("episodic")
                self.episodic_buffer.append(memory_item)
            
            self.usage_stats['total_items_processed'] += 1
            self._update_load_stats()
            
            return True
            
        except Exception as e:
            logging.error(f"❌ 作業記憶追加エラー: {e}")
            return False
    
    def retrieve_item(self, query: str, memory_type: str = "episodic") -> Optional[Any]:
        """作業記憶からの項目検索"""
        try:
            target_buffer = self._get_buffer(memory_type)
            
            for item in reversed(target_buffer):  # 最新から検索
                if self._matches_query(item['content'], query):
                    item['access_count'] += 1
                    return item['content']
            
            return None
            
        except Exception as e:
            logging.error(f"❌ 作業記憶検索エラー: {e}")
            return None
    
    def get_current_context(self) -> Dict[str, Any]:
        """現在の作業記憶コンテキスト"""
        return {
            'phonological_items': len(self.phonological_loop),
            'visuospatial_items': len(self.visuospatial_sketchpad),
            'episodic_items': len(self.episodic_buffer),
            'total_load': self.get_cognitive_load(),
            'efficiency': self._calculate_efficiency(),
            'executive_state': self.central_executive_state.copy()
        }
    
    def get_cognitive_load(self) -> float:
        """現在の認知負荷を計算"""
        total_items = (
            len(self.phonological_loop) + 
            len(self.visuospatial_sketchpad) + 
            len(self.episodic_buffer)
        )
        return min(total_items / (self.capacity * 3), 1.0)
    
    def _get_buffer(self, memory_type: str):
        """メモリタイプに対応するバッファを取得"""
        if memory_type == "phonological":
            return self.phonological_loop
        elif memory_type == "visuospatial":
            return self.visuospatial_sketchpad
        else:
            return self.episodic_buffer
    
    def _handle_capacity_overflow(self, memory_type: str):
        """容量オーバーフロー時の処理"""
        self.usage_stats['interference_events'] += 1
        # LRU (Least Recently Used) ベースで古い項目を削除
        # dequeの性質上、自動的に古い項目が削除される
    
    def _matches_query(self, content: Any, query: str) -> bool:
        """クエリとコンテンツのマッチング"""
        content_str = str(content).lower()
        return query.lower() in content_str
    
    def _calculate_efficiency(self) -> float:
        """作業記憶の効率を計算"""
        load = self.get_cognitive_load()
        # 適度な負荷で効率が最大になる逆U字カーブ
        optimal_load = 0.6
        if load <= optimal_load:
            return load / optimal_load
        else:
            return max(0.1, 1.0 - (load - optimal_load) / (1.0 - optimal_load))
    
    def _update_load_stats(self):
        """負荷統計の更新"""
        current_load = self.get_cognitive_load()
        self.usage_stats['current_load'] = current_load
        self.usage_stats['peak_load'] = max(self.usage_stats['peak_load'], current_load)

class AttentionManager:
    """注意管理システム"""
    
    def __init__(self, total_attention_capacity: float = 100.0):
        self.attention_resource = AttentionResource(
            total_capacity=total_attention_capacity,
            allocated=0.0,
            available=total_attention_capacity,
            efficiency=1.0,
            fatigue_level=0.0
        )
        
        self.active_tasks: Dict[str, CognitiveTask] = {}
        self.priority_queue = []  # heapqを使用
        self.attention_history = deque(maxlen=1000)
        
        # 注意のタイプ別パフォーマンス
        self.attention_performance = {
            AttentionType.FOCUSED: 1.0,
            AttentionType.DIVIDED: 0.7,
            AttentionType.SUSTAINED: 0.8,
            AttentionType.SELECTIVE: 0.9
        }
    
    async def allocate_attention(self, tasks: List[CognitiveTask]) -> Dict[str, float]:
        """注意リソースの動的配分"""
        try:
            allocations = {}
            
            # タスクの優先度計算
            prioritized_tasks = []
            for task in tasks:
                priority = await self._calculate_priority(task)
                heapq.heappush(prioritized_tasks, (-priority, task))  # 最大ヒープ
            
            # リソース配分
            remaining_attention = self.attention_resource.available
            
            while prioritized_tasks and remaining_attention > 0:
                neg_priority, task = heapq.heappop(prioritized_tasks)
                priority = -neg_priority
                
                # 必要リソースと利用可能リソースを比較
                required = min(task.required_attention, remaining_attention)
                
                # 注意タイプの決定
                attention_type = self._determine_attention_type(task, len(self.active_tasks))
                efficiency = self.attention_performance[attention_type]
                
                # 効率を考慮した実効配分
                effective_allocation = required * efficiency
                allocations[task.task_id] = effective_allocation
                
                # リソース更新
                remaining_attention -= required
                self.active_tasks[task.task_id] = task
                
                # 履歴記録
                self.attention_history.append({
                    'task_id': task.task_id,
                    'allocated': effective_allocation,
                    'attention_type': attention_type.value,
                    'timestamp': datetime.now()
                })
            
            # リソース状態更新
            self._update_attention_resource(allocations)
            
            logging.debug(f"🎯 注意配分完了: {len(allocations)}タスクに配分")
            return allocations
            
        except Exception as e:
            logging.error(f"❌ 注意配分エラー: {e}")
            return {}
    
    async def _calculate_priority(self, task: CognitiveTask) -> float:
        """タスク優先度の計算"""
        # アイゼンハワーマトリクス + 感情的重み
        urgency_importance = task.urgency * task.importance
        
        # 締切による緊急度調整
        deadline_pressure = 0.0
        if task.deadline:
            time_to_deadline = (task.deadline - datetime.now()).total_seconds()
            if time_to_deadline > 0:
                # 時間が少ないほど優先度UP
                deadline_pressure = max(0, 1.0 - time_to_deadline / (24 * 3600))  # 1日を基準
        
        # 感情的重みの考慮
        emotional_boost = task.emotional_weight * 0.3
        
        # 複雑性による調整（複雑なタスクは早めに着手）
        complexity_factor = task.complexity * 0.2
        
        # 総合優先度
        total_priority = (
            urgency_importance * 0.5 +
            deadline_pressure * 0.3 +
            emotional_boost +
            complexity_factor
        )
        
        return min(total_priority, 1.0)
    
    def _determine_attention_type(self, task: CognitiveTask, active_task_count: int) -> AttentionType:
        """注意タイプの決定"""
        if active_task_count == 0:
            return AttentionType.FOCUSED
        elif active_task_count == 1:
            return AttentionType.SELECTIVE
        elif task.complexity > 0.7:
            return AttentionType.SUSTAINED
        else:
            return AttentionType.DIVIDED
    
    def _update_attention_resource(self, allocations: Dict[str, float]):
        """注意リソース状態の更新"""
        total_allocated = sum(allocations.values())
        self.attention_resource.allocated = total_allocated
        self.attention_resource.available = self.attention_resource.total_capacity - total_allocated
        
        # 疲労度の更新（高負荷で疲労蓄積）
        load_ratio = total_allocated / self.attention_resource.total_capacity
        if load_ratio > 0.8:
            self.attention_resource.fatigue_level += 0.1
        elif load_ratio < 0.3:
            self.attention_resource.fatigue_level = max(0, self.attention_resource.fatigue_level - 0.05)
        
        # 効率の計算（疲労度の影響）
        self.attention_resource.efficiency = max(0.1, 1.0 - self.attention_resource.fatigue_level)
    
    async def release_attention(self, task_id: str):
        """注意リソースの解放"""
        if task_id in self.active_tasks:
            task = self.active_tasks[task_id]
            released_amount = task.required_attention
            
            del self.active_tasks[task_id]
            self.attention_resource.available += released_amount
            self.attention_resource.allocated -= released_amount
            
            logging.debug(f"🔓 注意解放: {task_id} -> {released_amount}リソース")
    
    def get_attention_statistics(self) -> Dict[str, Any]:
        """注意管理統計"""
        return {
            'total_capacity': self.attention_resource.total_capacity,
            'allocated': self.attention_resource.allocated,
            'available': self.attention_resource.available,
            'efficiency': self.attention_resource.efficiency,
            'fatigue_level': self.attention_resource.fatigue_level,
            'active_tasks': len(self.active_tasks),
            'attention_history_size': len(self.attention_history)
        }

class ConflictResolver:
    """競合解決システム"""
    
    def __init__(self):
        self.resolution_strategies = {
            'resource_conflict': self._resolve_resource_conflict,
            'priority_conflict': self._resolve_priority_conflict,
            'temporal_conflict': self._resolve_temporal_conflict,
            'strategy_conflict': self._resolve_strategy_conflict
        }
        
        self.conflict_history = deque(maxlen=500)
        
    async def resolve_conflict(self, conflicting_options: List[Dict[str, Any]], 
                             context: Dict[str, Any]) -> Dict[str, Any]:
        """競合の解決"""
        try:
            # 競合の種類を特定
            conflict_type = self._identify_conflict_type(conflicting_options, context)
            
            # 対応する解決戦略を実行
            resolution_strategy = self.resolution_strategies.get(
                conflict_type, self._resolve_generic_conflict
            )
            
            resolved_decision = await resolution_strategy(conflicting_options, context)
            
            # 競合履歴に記録
            conflict_record = {
                'conflict_type': conflict_type,
                'options_count': len(conflicting_options),
                'resolution': resolved_decision,
                'timestamp': datetime.now()
            }
            self.conflict_history.append(conflict_record)
            
            logging.info(f"⚖️ 競合解決: {conflict_type} -> {resolved_decision.get('strategy', 'unknown')}")
            return resolved_decision
            
        except Exception as e:
            logging.error(f"❌ 競合解決エラー: {e}")
            # フォールバック: 最初のオプションを選択
            return conflicting_options[0] if conflicting_options else {}
    
    def _identify_conflict_type(self, options: List[Dict[str, Any]], 
                               context: Dict[str, Any]) -> str:
        """競合タイプの特定"""
        # リソース競合の検出
        total_required_resources = sum(
            option.get('required_resources', 0) for option in options
        )
        available_resources = context.get('available_resources', 100)
        
        if total_required_resources > available_resources:
            return 'resource_conflict'
        
        # 優先度競合の検出
        priorities = [option.get('priority', 0) for option in options]
        if len(set(priorities)) < len(priorities) * 0.5:  # 半数以上が同じ優先度
            return 'priority_conflict'
        
        # 時間的競合の検出
        deadlines = [option.get('deadline') for option in options if option.get('deadline')]
        if len(deadlines) > 1:
            return 'temporal_conflict'
        
        # 戦略競合の検出
        strategies = [option.get('strategy') for option in options]
        if len(set(strategies)) == len(strategies):  # 全て異なる戦略
            return 'strategy_conflict'
        
        return 'generic_conflict'
    
    async def _resolve_resource_conflict(self, options: List[Dict[str, Any]], 
                                       context: Dict[str, Any]) -> Dict[str, Any]:
        """リソース競合の解決"""
        # 効率性でソート
        efficiency_sorted = sorted(
            options, 
            key=lambda x: x.get('expected_value', 0) / max(x.get('required_resources', 1), 1),
            reverse=True
        )
        return efficiency_sorted[0]
    
    async def _resolve_priority_conflict(self, options: List[Dict[str, Any]], 
                                       context: Dict[str, Any]) -> Dict[str, Any]:
        """優先度競合の解決"""
        # セカンダリ基準（感情的重み、複雑性など）で判定
        secondary_sorted = sorted(
            options,
            key=lambda x: (
                x.get('emotional_weight', 0) * 0.4 +
                x.get('urgency', 0) * 0.6
            ),
            reverse=True
        )
        return secondary_sorted[0]
    
    async def _resolve_temporal_conflict(self, options: List[Dict[str, Any]], 
                                       context: Dict[str, Any]) -> Dict[str, Any]:
        """時間的競合の解決"""
        # 締切が最も近いものを優先
        deadline_sorted = sorted(
            options,
            key=lambda x: x.get('deadline', datetime.max)
        )
        return deadline_sorted[0]
    
    async def _resolve_strategy_conflict(self, options: List[Dict[str, Any]], 
                                       context: Dict[str, Any]) -> Dict[str, Any]:
        """戦略競合の解決"""
        # コンテキストに最も適した戦略を選択
        system_state = context.get('system_state', {})
        
        if system_state.get('stress_level', 0) > 0.7:
            # 高ストレス時は保守的戦略を優先
            for option in options:
                if option.get('strategy') == 'conservative':
                    return option
        
        # デフォルトは合理的戦略
        for option in options:
            if option.get('strategy') == 'rational':
                return option
        
        return options[0]  # フォールバック
    
    async def _resolve_generic_conflict(self, options: List[Dict[str, Any]], 
                                      context: Dict[str, Any]) -> Dict[str, Any]:
        """汎用的競合解決"""
        # 多基準意思決定分析（MCDA）
        weights = {
            'priority': 0.3,
            'expected_value': 0.25,
            'confidence': 0.2,
            'emotional_weight': 0.15,
            'efficiency': 0.1
        }
        
        scored_options = []
        for option in options:
            score = sum(
                option.get(criterion, 0) * weight
                for criterion, weight in weights.items()
            )
            scored_options.append((score, option))
        
        scored_options.sort(reverse=True)
        return scored_options[0][1]

class MetaCognitiveMonitor:
    """メタ認知監視システム"""
    
    def __init__(self):
        self.monitoring_active = False
        self.performance_metrics = {
            'decision_accuracy': deque(maxlen=100),
            'execution_efficiency': deque(maxlen=100),
            'learning_rate': deque(maxlen=100),
            'error_rate': deque(maxlen=100)
        }
        
        self.metacognitive_beliefs = {
            'confidence_calibration': 0.5,  # 信頼度の校正
            'strategy_effectiveness': defaultdict(float),
            'task_difficulty_estimation': defaultdict(float)
        }
        
        self.monitoring_history = deque(maxlen=1000)
    
    async def start_monitoring(self, decision: ExecutiveDecision):
        """メタ認知監視の開始"""
        try:
            self.monitoring_active = True
            
            monitoring_context = {
                'decision_id': decision.decision_id,
                'strategy': decision.chosen_strategy.value,
                'confidence': decision.confidence,
                'start_time': datetime.now(),
                'expected_difficulty': self._estimate_task_difficulty(decision)
            }
            
            self.monitoring_history.append(monitoring_context)
            
            # バックグラウンドで監視を開始
            monitoring_task = asyncio.create_task(
                self._continuous_monitoring(monitoring_context)
            )
            
            logging.debug(f"🔍 メタ認知監視開始: {decision.decision_id}")
            return monitoring_task
            
        except Exception as e:
            logging.error(f"❌ メタ認知監視開始エラー: {e}")
            return None
    
    async def _continuous_monitoring(self, context: Dict[str, Any]):
        """継続的な監視プロセス"""
        try:
            start_time = context['start_time']
            
            while self.monitoring_active:
                current_time = datetime.now()
                elapsed_time = (current_time - start_time).total_seconds()
                
                # パフォーマンス評価
                performance_assessment = await self._assess_current_performance(context)
                
                # 必要に応じて介入
                if performance_assessment['needs_intervention']:
                    await self._metacognitive_intervention(context, performance_assessment)
                
                # 信念の更新
                self._update_metacognitive_beliefs(context, performance_assessment)
                
                # 1秒間隔で監視
                await asyncio.sleep(1.0)
                
                # 最大監視時間（5分）
                if elapsed_time > 300:
                    break
                    
        except asyncio.CancelledError:
            logging.debug("🔍 メタ認知監視が停止されました")
        except Exception as e:
            logging.error(f"❌ メタ認知監視エラー: {e}")
    
    async def _assess_current_performance(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """現在のパフォーマンス評価"""
        try:
            current_time = datetime.now()
            elapsed_time = (current_time - context['start_time']).total_seconds()
            
            # 進捗評価
            expected_progress = elapsed_time / context.get('estimated_duration', 60)
            # 実際の進捗は外部システムから取得する必要があるが、ここでは簡略化
            actual_progress = min(elapsed_time / 60, 1.0)  # 簡略化された進捗
            
            progress_deviation = abs(expected_progress - actual_progress)
            
            # 介入が必要かの判定
            needs_intervention = (
                progress_deviation > 0.3 or  # 30%以上の遅れ
                elapsed_time > context.get('estimated_duration', 60) * 1.5  # 1.5倍の時間超過
            )
            
            return {
                'progress_deviation': progress_deviation,
                'needs_intervention': needs_intervention,
                'confidence_drift': context['confidence'] - 0.5,  # 簡略化
                'elapsed_time': elapsed_time
            }
            
        except Exception as e:
            logging.error(f"❌ パフォーマンス評価エラー: {e}")
            return {'needs_intervention': False}
    
    async def _metacognitive_intervention(self, context: Dict[str, Any], 
                                        assessment: Dict[str, Any]):
        """メタ認知的介入"""
        try:
            intervention_type = "unknown"
            
            if assessment['progress_deviation'] > 0.3:
                intervention_type = "progress_adjustment"
                # 進捗調整の提案
                logging.warning(f"🚨 進捗遅延検出: {context['decision_id']}")
                
            elif assessment.get('confidence_drift', 0) < -0.2:
                intervention_type = "confidence_restoration"
                # 信頼度回復の提案
                logging.warning(f"🚨 信頼度低下検出: {context['decision_id']}")
            
            # 介入履歴に記録
            intervention_record = {
                'context': context,
                'intervention_type': intervention_type,
                'assessment': assessment,
                'timestamp': datetime.now()
            }
            
            # 実際の介入は他のシステムコンポーネントに委譲
            logging.info(f"🔧 メタ認知介入: {intervention_type}")
            
        except Exception as e:
            logging.error(f"❌ メタ認知介入エラー: {e}")
    
    def _estimate_task_difficulty(self, decision: ExecutiveDecision) -> float:
        """タスク難易度の推定"""
        # 戦略の複雑性、タスク数、リソース要求などから推定
        base_difficulty = len(decision.task_sequence) / 10.0
        strategy_complexity = {
            DecisionStrategy.RATIONAL: 0.3,
            DecisionStrategy.INTUITIVE: 0.1,
            DecisionStrategy.HYBRID: 0.5,
            DecisionStrategy.EMOTIONAL: 0.2,
            DecisionStrategy.CONSERVATIVE: 0.4
        }
        
        strategy_factor = strategy_complexity.get(decision.chosen_strategy, 0.3)
        confidence_factor = 1.0 - decision.confidence
        
        estimated_difficulty = min(base_difficulty + strategy_factor + confidence_factor, 1.0)
        return estimated_difficulty
    
    def _update_metacognitive_beliefs(self, context: Dict[str, Any], 
                                    assessment: Dict[str, Any]):
        """メタ認知的信念の更新"""
        strategy = context['strategy']
        
        # 戦略効果性の更新
        if not assessment['needs_intervention']:
            self.metacognitive_beliefs['strategy_effectiveness'][strategy] += 0.1
        else:
            self.metacognitive_beliefs['strategy_effectiveness'][strategy] -= 0.05
        
        # 信頼度校正の更新
        confidence_error = abs(context['confidence'] - assessment.get('actual_performance', 0.5))
        learning_rate = 0.05
        self.metacognitive_beliefs['confidence_calibration'] += learning_rate * confidence_error
    
    def stop_monitoring(self):
        """監視の停止"""
        self.monitoring_active = False
    
    def get_metacognitive_statistics(self) -> Dict[str, Any]:
        """メタ認知統計"""
        return {
            'monitoring_active': self.monitoring_active,
            'confidence_calibration': self.metacognitive_beliefs['confidence_calibration'],
            'strategy_effectiveness': dict(self.metacognitive_beliefs['strategy_effectiveness']),
            'monitoring_history_size': len(self.monitoring_history),
            'performance_metrics': {
                metric: len(values) for metric, values in self.performance_metrics.items()
            }
        }

class ExecutiveController:
    """高次認知制御システム統合"""
    
    def __init__(self):
        self.working_memory = WorkingMemory()
        self.attention_manager = AttentionManager()
        self.conflict_resolver = ConflictResolver()
        self.meta_cognition = MetaCognitiveMonitor()
        
        # 意思決定履歴
        self.decision_history = deque(maxlen=1000)
        
        # 学習パラメータ
        self.strategy_performance = defaultdict(list)
        
    async def executive_decision(self, task_options: List[CognitiveTask], 
                               context: Dict[str, Any]) -> ExecutiveDecision:
        """高次の実行決定プロセス"""
        try:
            decision_start_time = datetime.now()
            
            # 1. 作業記憶への情報ロード
            for task in task_options:
                self.working_memory.add_item(task, "episodic")
            
            # 2. 注意リソースの評価
            attention_allocations = await self.attention_manager.allocate_attention(task_options)
            
            # 3. 複数評価軸での分析
            evaluations = await asyncio.gather(
                self._rational_analysis(task_options, context),
                self._intuitive_analysis(task_options, context),
                self._emotional_analysis(task_options, context)
            )
            
            # 4. 競合検出と解決
            if self._detect_evaluation_conflicts(evaluations):
                resolved_evaluation = await self.conflict_resolver.resolve_conflict(
                    evaluations, context
                )
            else:
                resolved_evaluation = self._integrate_evaluations(evaluations)
            
            # 5. 最終決定の形成
            executive_decision = self._form_executive_decision(
                resolved_evaluation, attention_allocations, context
            )
            
            # 6. メタ認知監視の開始
            monitoring_task = await self.meta_cognition.start_monitoring(executive_decision)
            
            # 7. 決定履歴への記録
            self.decision_history.append(executive_decision)
            
            execution_time = (datetime.now() - decision_start_time).total_seconds()
            logging.info(f"🧠 実行決定完了: {executive_decision.decision_id} "
                        f"({execution_time:.2f}秒, 戦略: {executive_decision.chosen_strategy.value})")
            
            return executive_decision
            
        except Exception as e:
            logging.error(f"❌ 実行決定エラー: {e}")
            # フォールバック決定
            return self._create_fallback_decision(task_options)
    
    async def _rational_analysis(self, tasks: List[CognitiveTask], 
                               context: Dict[str, Any]) -> Dict[str, Any]:
        """合理的分析"""
        try:
            # 期待値理論に基づく分析
            task_scores = []
            
            for task in tasks:
                # 利益 × 成功確率 - コスト × 失敗確率
                estimated_success_prob = 1.0 - task.complexity * 0.3
                expected_benefit = task.importance * estimated_success_prob
                estimated_cost = task.required_attention / 100.0
                
                utility_score = expected_benefit - estimated_cost
                task_scores.append((utility_score, task))
            
            # 最高スコアのタスクを選択
            task_scores.sort(reverse=True)
            best_task = task_scores[0][1] if task_scores else tasks[0]
            
            return {
                'strategy': DecisionStrategy.RATIONAL,
                'recommended_task': best_task,
                'confidence': 0.8,
                'rationale': 'Expected utility maximization',
                'evaluation_details': task_scores[:3]
            }
            
        except Exception as e:
            logging.error(f"❌ 合理的分析エラー: {e}")
            return {'strategy': DecisionStrategy.RATIONAL, 'confidence': 0.1}
    
    async def _intuitive_analysis(self, tasks: List[CognitiveTask], 
                                context: Dict[str, Any]) -> Dict[str, Any]:
        """直感的分析"""
        try:
            # ヒューリスティックベースの判断
            intuitive_scores = []
            
            for task in tasks:
                # 認識しやすさ（availability heuristic）
                familiarity = 1.0 - task.complexity
                
                # 代表性（representativeness heuristic）
                typical_pattern = 0.7 if task.task_type in ['simple', 'qa'] else 0.5
                
                # アンカリング効果
                anchor_adjustment = task.urgency * 0.8
                
                intuitive_score = (familiarity + typical_pattern + anchor_adjustment) / 3.0
                intuitive_scores.append((intuitive_score, task))
            
            intuitive_scores.sort(reverse=True)
            best_task = intuitive_scores[0][1] if intuitive_scores else tasks[0]
            
            return {
                'strategy': DecisionStrategy.INTUITIVE,
                'recommended_task': best_task,
                'confidence': 0.6,
                'rationale': 'Heuristic-based fast judgment',
                'evaluation_details': intuitive_scores[:3]
            }
            
        except Exception as e:
            logging.error(f"❌ 直感的分析エラー: {e}")
            return {'strategy': DecisionStrategy.INTUITIVE, 'confidence': 0.1}
    
    async def _emotional_analysis(self, tasks: List[CognitiveTask], 
                                context: Dict[str, Any]) -> Dict[str, Any]:
        """感情的分析"""
        try:
            emotional_scores = []
            
            for task in tasks:
                # 感情的重みに基づく評価
                emotional_appeal = task.emotional_weight
                
                # ストレス軽減効果
                stress_relief = 1.0 - task.complexity if task.task_type == 'creative' else 0.3
                
                # 達成感の予測
                achievement_feeling = task.importance * 0.8
                
                emotional_score = (emotional_appeal + stress_relief + achievement_feeling) / 3.0
                emotional_scores.append((emotional_score, task))
            
            emotional_scores.sort(reverse=True)
            best_task = emotional_scores[0][1] if emotional_scores else tasks[0]
            
            return {
                'strategy': DecisionStrategy.EMOTIONAL,
                'recommended_task': best_task,
                'confidence': 0.7,
                'rationale': 'Emotion-driven selection',
                'evaluation_details': emotional_scores[:3]
            }
            
        except Exception as e:
            logging.error(f"❌ 感情的分析エラー: {e}")
            return {'strategy': DecisionStrategy.EMOTIONAL, 'confidence': 0.1}
    
    def _detect_evaluation_conflicts(self, evaluations: List[Dict[str, Any]]) -> bool:
        """評価間の競合検出"""
        recommended_tasks = [
            eval_result.get('recommended_task') 
            for eval_result in evaluations 
            if eval_result.get('recommended_task')
        ]
        
        # 異なるタスクが推奨されている場合は競合
        unique_recommendations = set(
            task.task_id for task in recommended_tasks if task
        )
        
        return len(unique_recommendations) > 1
    
    def _integrate_evaluations(self, evaluations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """評価の統合"""
        # 信頼度による重み付け平均
        total_confidence = sum(eval_result.get('confidence', 0) for eval_result in evaluations)
        
        if total_confidence == 0:
            return evaluations[0]  # フォールバック
        
        # 最も信頼度の高い評価を採用
        best_evaluation = max(evaluations, key=lambda x: x.get('confidence', 0))
        best_evaluation['strategy'] = DecisionStrategy.HYBRID
        best_evaluation['rationale'] = 'Integrated multi-perspective analysis'
        
        return best_evaluation
    
    def _form_executive_decision(self, evaluation: Dict[str, Any], 
                               attention_allocations: Dict[str, float], 
                               context: Dict[str, Any]) -> ExecutiveDecision:
        """実行決定の形成"""
        decision_id = f"exec_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        
        recommended_task = evaluation.get('recommended_task')
        task_sequence = [recommended_task.task_id] if recommended_task else []
        
        decision = ExecutiveDecision(
            decision_id=decision_id,
            chosen_strategy=evaluation.get('strategy', DecisionStrategy.RATIONAL),
            task_sequence=task_sequence,
            resource_allocation=attention_allocations,
            confidence=evaluation.get('confidence', 0.5),
            rationale=evaluation.get('rationale', 'Default decision'),
            alternatives_considered=evaluation.get('evaluation_details', []),
            timestamp=datetime.now()
        )
        
        return decision
    
    def _create_fallback_decision(self, tasks: List[CognitiveTask]) -> ExecutiveDecision:
        """フォールバック決定の作成"""
        decision_id = f"fallback_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        
        # 最初のタスクを選択
        first_task = tasks[0] if tasks else None
        task_sequence = [first_task.task_id] if first_task else []
        
        return ExecutiveDecision(
            decision_id=decision_id,
            chosen_strategy=DecisionStrategy.CONSERVATIVE,
            task_sequence=task_sequence,
            resource_allocation={},
            confidence=0.3,
            rationale='Fallback decision due to error',
            alternatives_considered=[],
            timestamp=datetime.now()
        )
    
    async def update_strategy_performance(self, decision_id: str, success: bool, 
                                        performance_metrics: Dict[str, float]):
        """戦略パフォーマンスの更新"""
        try:
            # 決定履歴から該当決定を検索
            target_decision = None
            for decision in reversed(self.decision_history):
                if decision.decision_id == decision_id:
                    target_decision = decision
                    break
            
            if target_decision:
                strategy = target_decision.chosen_strategy
                performance_score = 1.0 if success else 0.0
                
                # パフォーマンスメトリクスの重み付き合計
                if performance_metrics:
                    weighted_score = (
                        performance_metrics.get('efficiency', 0.5) * 0.3 +
                        performance_metrics.get('quality', 0.5) * 0.4 +
                        performance_metrics.get('user_satisfaction', 0.5) * 0.3
                    )
                    performance_score = (performance_score + weighted_score) / 2.0
                
                self.strategy_performance[strategy].append(performance_score)
                
                logging.debug(f"📊 戦略パフォーマンス更新: {strategy.value} -> {performance_score:.2f}")
            
        except Exception as e:
            logging.error(f"❌ 戦略パフォーマンス更新エラー: {e}")
    
    def get_executive_statistics(self) -> Dict[str, Any]:
        """実行制御統計"""
        strategy_stats = {}
        for strategy, performances in self.strategy_performance.items():
            if performances:
                strategy_stats[strategy.value] = {
                    'average_performance': sum(performances) / len(performances),
                    'sample_count': len(performances),
                    'recent_performance': performances[-5:] if len(performances) >= 5 else performances
                }
        
        return {
            'working_memory': self.working_memory.get_current_context(),
            'attention_manager': self.attention_manager.get_attention_statistics(),
            'metacognition': self.meta_cognition.get_metacognitive_statistics(),
            'decision_history_size': len(self.decision_history),
            'strategy_performance': strategy_stats
        }