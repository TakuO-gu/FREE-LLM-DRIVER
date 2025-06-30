"""
Emotional Processing System - 大脳辺縁系を模倣した感情・記憶システム
扁桃体（脅威検知）、海馬（記憶管理）、報酬系を統合した感情的判断機能
"""

import asyncio
import logging
import hashlib
import json
import math
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
from datetime import datetime, timedelta
from collections import defaultdict, deque

class ThreatLevel(Enum):
    """脅威レベル"""
    SAFE = 1
    LOW = 2
    MODERATE = 3
    HIGH = 4
    CRITICAL = 5

class EmotionalState(Enum):
    """感情状態"""
    NEUTRAL = "neutral"
    POSITIVE = "positive"
    NEGATIVE = "negative"
    ANXIOUS = "anxious"
    CONFIDENT = "confident"
    FRUSTRATED = "frustrated"

@dataclass
class EmotionalContext:
    """感情的文脈"""
    threat_level: ThreatLevel
    emotional_weight: float
    confidence: float
    valence: float  # 感情の価値（-1.0 to 1.0）
    arousal: float  # 覚醒度（0.0 to 1.0）
    state: EmotionalState
    timestamp: datetime

@dataclass
class Experience:
    """経験データ"""
    task_id: str
    task_pattern: str
    task_type: str
    result_quality: float
    success: bool
    execution_time: float
    emotional_impact: float
    threat_assessment: ThreatLevel
    timestamp: datetime
    reinforcement_count: int = 1
    decay_factor: float = 1.0

class ThreatDetector:
    """扁桃体機能 - 脅威検知システム"""
    
    def __init__(self):
        self.threat_patterns = {
            # セキュリティ関連のパターン
            'security_threats': [
                'delete', 'remove', 'rm ', 'format', 'sudo', 'admin',
                'password', 'private', 'secret', 'token', 'key',
                'system', 'root', 'kernel', 'registry'
            ],
            # リソース消費パターン
            'resource_intensive': [
                'infinite', 'loop', 'recursive', 'heavy', 'large',
                'massive', 'bulk', 'batch', 'parallel'
            ],
            # 複雑性パターン
            'complexity_markers': [
                'complex', 'difficult', 'advanced', 'expert',
                'sophisticated', 'intricate', 'comprehensive'
            ],
            # 破壊的操作
            'destructive_operations': [
                'overwrite', 'replace', 'destroy', 'clear',
                'reset', 'wipe', 'purge', 'cleanup'
            ]
        }
        
        self.threat_weights = {
            'security_threats': 5.0,
            'resource_intensive': 3.0,
            'complexity_markers': 2.0,
            'destructive_operations': 4.0
        }
        
        # 学習された脅威パターン
        self.learned_threats = defaultdict(float)
        
    async def assess_threat(self, task_description: str, task_type: str = "general") -> Tuple[ThreatLevel, float, Dict[str, Any]]:
        """脅威レベルの評価"""
        try:
            description_lower = task_description.lower()
            threat_score = 0.0
            detected_patterns = {}
            
            # 既知のパターンマッチング
            for category, patterns in self.threat_patterns.items():
                matches = [pattern for pattern in patterns if pattern in description_lower]
                if matches:
                    category_score = len(matches) * self.threat_weights[category]
                    threat_score += category_score
                    detected_patterns[category] = {
                        'matches': matches,
                        'score': category_score
                    }
            
            # 学習された脅威パターンチェック
            for pattern, weight in self.learned_threats.items():
                if pattern in description_lower:
                    threat_score += weight
                    detected_patterns['learned'] = detected_patterns.get('learned', [])
                    detected_patterns['learned'].append({'pattern': pattern, 'weight': weight})
            
            # タスクタイプによる調整
            type_multiplier = self._get_type_risk_multiplier(task_type)
            threat_score *= type_multiplier
            
            # 長さによる複雑性評価
            length_factor = min(len(task_description) / 100, 2.0)
            threat_score += length_factor
            
            # 脅威レベルの判定
            threat_level = self._calculate_threat_level(threat_score)
            
            assessment_details = {
                'raw_score': threat_score,
                'type_multiplier': type_multiplier,
                'length_factor': length_factor,
                'detected_patterns': detected_patterns,
                'assessment_timestamp': datetime.now()
            }
            
            logging.debug(f"🔍 脅威評価: {task_description[:50]}... -> {threat_level.name} (スコア: {threat_score:.2f})")
            
            return threat_level, threat_score, assessment_details
            
        except Exception as e:
            logging.error(f"❌ 脅威評価エラー: {e}")
            return ThreatLevel.MODERATE, 3.0, {'error': str(e)}
    
    def _get_type_risk_multiplier(self, task_type: str) -> float:
        """タスクタイプによるリスク倍率"""
        multipliers = {
            'code': 2.0,
            'system': 3.0,
            'admin': 4.0,
            'analysis': 1.0,
            'creative': 0.5,
            'qa': 0.3,
            'web_search': 0.8
        }
        return multipliers.get(task_type.lower(), 1.0)
    
    def _calculate_threat_level(self, score: float) -> ThreatLevel:
        """スコアから脅威レベルを判定"""
        if score <= 1.0:
            return ThreatLevel.SAFE
        elif score <= 3.0:
            return ThreatLevel.LOW
        elif score <= 6.0:
            return ThreatLevel.MODERATE
        elif score <= 10.0:
            return ThreatLevel.HIGH
        else:
            return ThreatLevel.CRITICAL
    
    async def learn_from_outcome(self, task_description: str, was_successful: bool, impact_severity: float):
        """結果から学習して脅威パターンを更新"""
        try:
            description_lower = task_description.lower()
            
            # 失敗した場合、関連パターンの脅威重みを増加
            if not was_successful and impact_severity > 0.5:
                words = description_lower.split()
                for word in words:
                    if len(word) > 3:  # 短すぎる単語は除外
                        self.learned_threats[word] += impact_severity * 0.5
            
            # 成功した場合、脅威重みを軽微に減少
            elif was_successful:
                words = description_lower.split()
                for word in words:
                    if word in self.learned_threats:
                        self.learned_threats[word] *= 0.95  # 5%減少
            
            # 重みの上限設定
            for pattern in self.learned_threats:
                self.learned_threats[pattern] = min(self.learned_threats[pattern], 5.0)
            
        except Exception as e:
            logging.error(f"❌ 脅威学習エラー: {e}")

class AdaptiveMemory:
    """海馬機能 - 適応的記憶管理システム"""
    
    def __init__(self, max_episodic_memories: int = 1000, max_working_memory: int = 50):
        # エピソード記憶（具体的な経験）
        self.episodic_memory: Dict[str, Experience] = {}
        
        # 意味記憶（一般的な知識・パターン）
        self.semantic_memory: Dict[str, Dict[str, Any]] = defaultdict(dict)
        
        # 作業記憶（短期記憶）
        self.working_memory = deque(maxlen=max_working_memory)
        
        # 記憶の統計情報
        self.memory_stats = {
            'total_experiences': 0,
            'successful_experiences': 0,
            'pattern_learning_count': 0,
            'memory_consolidations': 0
        }
        
        self.max_episodic_memories = max_episodic_memories
        
    async def store_experience(self, task_id: str, task_description: str, task_type: str, 
                              result_quality: float, success: bool, execution_time: float,
                              emotional_context: EmotionalContext) -> None:
        """経験を感情的重みと共に保存"""
        try:
            # タスクパターンの抽出
            task_pattern = self._extract_task_pattern(task_description, task_type)
            
            # 経験オブジェクトの作成
            experience = Experience(
                task_id=task_id,
                task_pattern=task_pattern,
                task_type=task_type,
                result_quality=result_quality,
                success=success,
                execution_time=execution_time,
                emotional_impact=emotional_context.emotional_weight,
                threat_assessment=emotional_context.threat_level,
                timestamp=datetime.now()
            )
            
            # 類似経験の検索と強化
            similar_experiences = await self._find_similar_experiences(task_pattern, task_type)
            
            if similar_experiences:
                # 既存の経験を強化
                for similar_exp in similar_experiences[:3]:  # 上位3つを強化
                    similar_exp.reinforcement_count += 1
                    # 新しい結果で重み付き平均を計算
                    weight = 1.0 / similar_exp.reinforcement_count
                    similar_exp.result_quality = (
                        similar_exp.result_quality * (1 - weight) + result_quality * weight
                    )
            
            # エピソード記憶に保存
            self.episodic_memory[task_id] = experience
            
            # 作業記憶に追加
            self.working_memory.append(experience)
            
            # 意味記憶の更新
            await self._update_semantic_memory(task_pattern, task_type, experience)
            
            # メモリサイズ制限の管理
            await self._manage_memory_capacity()
            
            # 統計更新
            self.memory_stats['total_experiences'] += 1
            if success:
                self.memory_stats['successful_experiences'] += 1
            
            logging.debug(f"🧠 経験保存: {task_pattern} -> 成功: {success}, 品質: {result_quality:.2f}")
            
        except Exception as e:
            logging.error(f"❌ 経験保存エラー: {e}")
    
    async def recall_similar_experiences(self, task_description: str, task_type: str, 
                                       limit: int = 10) -> List[Experience]:
        """類似経験の想起"""
        try:
            task_pattern = self._extract_task_pattern(task_description, task_type)
            similar_experiences = await self._find_similar_experiences(task_pattern, task_type)
            
            # 関連度と新鮮さによるスコアリング
            scored_experiences = []
            for exp in similar_experiences:
                relevance_score = self._calculate_relevance_score(task_pattern, exp)
                freshness_score = self._calculate_freshness_score(exp)
                emotional_score = abs(exp.emotional_impact)  # 感情的影響の強さ
                
                combined_score = (
                    relevance_score * 0.5 + 
                    freshness_score * 0.3 + 
                    emotional_score * 0.2
                )
                
                scored_experiences.append((combined_score, exp))
            
            # スコア順でソート
            scored_experiences.sort(key=lambda x: x[0], reverse=True)
            
            return [exp for _, exp in scored_experiences[:limit]]
            
        except Exception as e:
            logging.error(f"❌ 経験想起エラー: {e}")
            return []
    
    async def get_pattern_knowledge(self, task_pattern: str, task_type: str) -> Dict[str, Any]:
        """パターンに関する意味記憶の取得"""
        try:
            pattern_key = f"{task_type}:{task_pattern}"
            return self.semantic_memory.get(pattern_key, {
                'success_rate': 0.5,
                'average_execution_time': 30.0,
                'common_issues': [],
                'confidence': 0.0
            })
            
        except Exception as e:
            logging.error(f"❌ パターン知識取得エラー: {e}")
            return {}
    
    def _extract_task_pattern(self, task_description: str, task_type: str) -> str:
        """タスクから特徴的なパターンを抽出"""
        # 単語の正規化と重要語の抽出
        words = task_description.lower().split()
        
        # ストップワードの除去
        stop_words = {'の', 'を', 'に', 'は', 'が', 'で', 'から', 'まで', 'と', 'a', 'an', 'the', 'is', 'are', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
        meaningful_words = [word for word in words if word not in stop_words and len(word) > 2]
        
        # 重要度による重み付け（動詞、名詞を優先）
        important_words = []
        for word in meaningful_words[:5]:  # 上位5語
            if any(keyword in word for keyword in ['作成', 'create', '分析', 'analyze', '実行', 'execute', '検索', 'search']):
                important_words.append(word)
        
        # パターン文字列の生成
        if important_words:
            pattern = '_'.join(sorted(important_words))
        else:
            pattern = '_'.join(meaningful_words[:3])
        
        return pattern or 'generic_task'
    
    async def _find_similar_experiences(self, task_pattern: str, task_type: str) -> List[Experience]:
        """類似経験の検索"""
        similar_experiences = []
        
        for experience in self.episodic_memory.values():
            # タスクタイプが同じ
            if experience.task_type == task_type:
                similarity = self._calculate_pattern_similarity(task_pattern, experience.task_pattern)
                if similarity > 0.3:  # 30%以上の類似度
                    similar_experiences.append(experience)
            
            # パターンが部分的に一致
            elif any(word in experience.task_pattern for word in task_pattern.split('_')):
                similar_experiences.append(experience)
        
        return similar_experiences
    
    def _calculate_pattern_similarity(self, pattern1: str, pattern2: str) -> float:
        """パターン類似度の計算"""
        words1 = set(pattern1.split('_'))
        words2 = set(pattern2.split('_'))
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union)  # Jaccard類似度
    
    def _calculate_relevance_score(self, target_pattern: str, experience: Experience) -> float:
        """関連度スコアの計算"""
        base_similarity = self._calculate_pattern_similarity(target_pattern, experience.task_pattern)
        
        # 強化回数による重み付け
        reinforcement_boost = min(experience.reinforcement_count / 10.0, 0.5)
        
        # 成功体験への重み付け
        success_boost = 0.2 if experience.success else -0.1
        
        return base_similarity + reinforcement_boost + success_boost
    
    def _calculate_freshness_score(self, experience: Experience) -> float:
        """新鮮さスコアの計算（時間減衰）"""
        time_diff = datetime.now() - experience.timestamp
        days_old = time_diff.total_seconds() / (24 * 3600)
        
        # 指数減衰（半減期: 7日）
        return math.exp(-days_old / 7.0)
    
    async def _update_semantic_memory(self, task_pattern: str, task_type: str, experience: Experience):
        """意味記憶の更新"""
        pattern_key = f"{task_type}:{task_pattern}"
        
        if pattern_key not in self.semantic_memory:
            self.semantic_memory[pattern_key] = {
                'success_rate': 0.0,
                'total_attempts': 0,
                'successful_attempts': 0,
                'average_execution_time': 0.0,
                'emotional_variance': 0.0,
                'common_threats': defaultdict(int),
                'confidence': 0.0
            }
        
        pattern_data = self.semantic_memory[pattern_key]
        pattern_data['total_attempts'] += 1
        
        if experience.success:
            pattern_data['successful_attempts'] += 1
        
        # 成功率の更新
        pattern_data['success_rate'] = pattern_data['successful_attempts'] / pattern_data['total_attempts']
        
        # 実行時間の移動平均
        alpha = 0.1  # 学習率
        pattern_data['average_execution_time'] = (
            pattern_data['average_execution_time'] * (1 - alpha) + 
            experience.execution_time * alpha
        )
        
        # 脅威情報の更新
        pattern_data['common_threats'][experience.threat_assessment.name] += 1
        
        # 信頼度の計算
        pattern_data['confidence'] = min(pattern_data['total_attempts'] / 10.0, 1.0)
        
        self.memory_stats['pattern_learning_count'] += 1
    
    async def _manage_memory_capacity(self):
        """記憶容量の管理"""
        if len(self.episodic_memory) > self.max_episodic_memories:
            # 古い記憶の削除（LRU + 重要度考慮）
            memories_to_remove = len(self.episodic_memory) - self.max_episodic_memories
            
            # 重要度スコアの計算
            memory_scores = []
            for memory_id, experience in self.episodic_memory.items():
                importance_score = (
                    experience.reinforcement_count * 0.3 +
                    (1.0 if experience.success else 0.5) * 0.2 +
                    abs(experience.emotional_impact) * 0.3 +
                    self._calculate_freshness_score(experience) * 0.2
                )
                memory_scores.append((importance_score, memory_id))
            
            # 重要度が低い記憶を削除
            memory_scores.sort()
            for _, memory_id in memory_scores[:memories_to_remove]:
                del self.episodic_memory[memory_id]
            
            self.memory_stats['memory_consolidations'] += 1
    
    def get_memory_statistics(self) -> Dict[str, Any]:
        """記憶統計の取得"""
        return {
            'episodic_memory_size': len(self.episodic_memory),
            'semantic_patterns': len(self.semantic_memory),
            'working_memory_size': len(self.working_memory),
            'success_rate': (
                self.memory_stats['successful_experiences'] / max(self.memory_stats['total_experiences'], 1)
            ),
            'total_experiences': self.memory_stats['total_experiences'],
            'pattern_learning_count': self.memory_stats['pattern_learning_count'],
            'memory_consolidations': self.memory_stats['memory_consolidations']
        }

class RewardSystem:
    """報酬系 - 成功体験に基づく動機付けシステム"""
    
    def __init__(self):
        self.reward_weights = {
            'task_success': 1.0,
            'execution_speed': 0.5,
            'resource_efficiency': 0.3,
            'user_satisfaction': 2.0,
            'learning_achievement': 0.8
        }
        
        # 報酬履歴
        self.reward_history = deque(maxlen=1000)
        
        # 期待値学習
        self.expected_rewards = defaultdict(float)
        
    async def calculate_reward(self, task_result: Dict[str, Any], emotional_context: EmotionalContext) -> float:
        """報酬の計算"""
        try:
            total_reward = 0.0
            reward_components = {}
            
            # 基本成功報酬
            if task_result.get('success', False):
                success_reward = self.reward_weights['task_success']
                total_reward += success_reward
                reward_components['success'] = success_reward
            
            # 実行速度報酬
            execution_time = task_result.get('execution_time', 30.0)
            if execution_time < 10.0:  # 10秒未満で完了
                speed_reward = self.reward_weights['execution_speed'] * (10.0 - execution_time) / 10.0
                total_reward += speed_reward
                reward_components['speed'] = speed_reward
            
            # 品質報酬
            quality = task_result.get('quality', 0.5)
            quality_reward = quality * self.reward_weights['user_satisfaction']
            total_reward += quality_reward
            reward_components['quality'] = quality_reward
            
            # 感情的ボーナス
            if emotional_context.state == EmotionalState.CONFIDENT:
                confidence_bonus = 0.2
                total_reward += confidence_bonus
                reward_components['confidence'] = confidence_bonus
            
            # 脅威レベルによるペナルティ/ボーナス
            if emotional_context.threat_level == ThreatLevel.CRITICAL:
                total_reward -= 0.5  # 高リスクタスクのペナルティ
            elif emotional_context.threat_level == ThreatLevel.SAFE:
                total_reward += 0.1   # 安全タスクのボーナス
            
            # 報酬履歴に記録
            reward_record = {
                'timestamp': datetime.now(),
                'total_reward': total_reward,
                'components': reward_components,
                'task_type': task_result.get('task_type', 'unknown')
            }
            self.reward_history.append(reward_record)
            
            return max(total_reward, 0.0)  # 負の報酬は0にクリップ
            
        except Exception as e:
            logging.error(f"❌ 報酬計算エラー: {e}")
            return 0.0
    
    async def update_expectations(self, task_pattern: str, actual_reward: float):
        """期待報酬の更新"""
        learning_rate = 0.1
        current_expectation = self.expected_rewards[task_pattern]
        
        # TD学習による期待値更新
        prediction_error = actual_reward - current_expectation
        self.expected_rewards[task_pattern] += learning_rate * prediction_error
    
    def get_motivation_level(self, task_pattern: str) -> float:
        """動機レベルの計算"""
        expected_reward = self.expected_rewards.get(task_pattern, 0.5)
        
        # 最近の報酬平均
        recent_rewards = [r['total_reward'] for r in list(self.reward_history)[-10:]]
        avg_recent_reward = sum(recent_rewards) / max(len(recent_rewards), 1)
        
        # 動機レベル = 期待報酬 + 最近のパフォーマンス
        motivation = (expected_reward + avg_recent_reward) / 2.0
        
        return min(max(motivation, 0.0), 1.0)  # 0-1にクリップ

class EmotionalProcessingSystem:
    """感情処理システム - 大脳辺縁系の統合機能"""
    
    def __init__(self):
        self.threat_detector = ThreatDetector()
        self.memory_manager = AdaptiveMemory()
        self.reward_system = RewardSystem()
        
        # 現在の感情状態
        self.current_emotional_state = EmotionalState.NEUTRAL
        self.emotional_history = deque(maxlen=100)
        
        # 感情的重み付けパラメータ
        self.emotional_weights = {
            'threat_influence': 0.4,
            'memory_influence': 0.3,
            'reward_influence': 0.3
        }
    
    async def evaluate_task_emotion(self, task_description: str, task_type: str = "general") -> EmotionalContext:
        """タスクの感情的重みを評価"""
        try:
            # 脅威評価
            threat_level, threat_score, threat_details = await self.threat_detector.assess_threat(
                task_description, task_type
            )
            
            # 過去の経験想起
            past_experiences = await self.memory_manager.recall_similar_experiences(
                task_description, task_type, limit=5
            )
            
            # 感情的重みの計算
            emotional_weight = await self._calculate_emotional_significance(
                threat_level, threat_score, past_experiences
            )
            
            # 信頼度の計算
            confidence = self._calculate_confidence(past_experiences)
            
            # 感情価値（valence）と覚醒度（arousal）の計算
            valence, arousal = self._calculate_emotional_dimensions(
                threat_level, past_experiences, emotional_weight
            )
            
            # 感情状態の判定
            emotional_state = self._determine_emotional_state(valence, arousal, threat_level)
            
            # 感情的文脈の作成
            emotional_context = EmotionalContext(
                threat_level=threat_level,
                emotional_weight=emotional_weight,
                confidence=confidence,
                valence=valence,
                arousal=arousal,
                state=emotional_state,
                timestamp=datetime.now()
            )
            
            # 感情履歴に記録
            self.emotional_history.append(emotional_context)
            self.current_emotional_state = emotional_state
            
            logging.info(f"💭 感情評価: {task_description[:50]}... -> {emotional_state.value} "
                        f"(脅威: {threat_level.name}, 重み: {emotional_weight:.2f}, 信頼度: {confidence:.2f})")
            
            return emotional_context
            
        except Exception as e:
            logging.error(f"❌ 感情評価エラー: {e}")
            return EmotionalContext(
                threat_level=ThreatLevel.MODERATE,
                emotional_weight=0.5,
                confidence=0.0,
                valence=0.0,
                arousal=0.5,
                state=EmotionalState.NEUTRAL,
                timestamp=datetime.now()
            )
    
    async def process_task_outcome(self, task_id: str, task_description: str, task_type: str,
                                  task_result: Dict[str, Any], emotional_context: EmotionalContext):
        """タスク結果の感情的処理"""
        try:
            # 結果の品質評価
            success = task_result.get('success', False)
            execution_time = task_result.get('execution_time', 30.0)
            result_quality = task_result.get('quality', 0.5 if success else 0.1)
            
            # 報酬計算
            reward = await self.reward_system.calculate_reward(task_result, emotional_context)
            
            # 記憶への保存
            await self.memory_manager.store_experience(
                task_id, task_description, task_type,
                result_quality, success, execution_time, emotional_context
            )
            
            # 脅威検知器の学習
            impact_severity = 1.0 - result_quality if not success else 0.0
            await self.threat_detector.learn_from_outcome(
                task_description, success, impact_severity
            )
            
            # 期待報酬の更新
            task_pattern = self.memory_manager._extract_task_pattern(task_description, task_type)
            await self.reward_system.update_expectations(task_pattern, reward)
            
            logging.info(f"🎯 結果処理: {task_id} -> 成功: {success}, 報酬: {reward:.2f}")
            
        except Exception as e:
            logging.error(f"❌ 結果処理エラー: {e}")
    
    async def _calculate_emotional_significance(self, threat_level: ThreatLevel, 
                                              threat_score: float, past_experiences: List[Experience]) -> float:
        """感情的重要度の計算"""
        # 脅威による重み
        threat_weight = threat_score / 10.0  # 正規化
        
        # 過去の経験による重み
        if past_experiences:
            experience_weights = []
            for exp in past_experiences:
                # 失敗体験は重みを増加
                exp_weight = abs(exp.emotional_impact)
                if not exp.success:
                    exp_weight *= 1.5
                experience_weights.append(exp_weight)
            
            avg_experience_weight = sum(experience_weights) / len(experience_weights)
        else:
            avg_experience_weight = 0.5  # デフォルト
        
        # 総合的な感情的重み
        emotional_significance = (
            threat_weight * self.emotional_weights['threat_influence'] +
            avg_experience_weight * self.emotional_weights['memory_influence']
        )
        
        return min(max(emotional_significance, 0.0), 1.0)
    
    def _calculate_confidence(self, past_experiences: List[Experience]) -> float:
        """信頼度の計算"""
        if not past_experiences:
            return 0.0
        
        # 経験数による基本信頼度
        base_confidence = min(len(past_experiences) / 10.0, 0.8)
        
        # 成功率による調整
        success_rate = sum(1 for exp in past_experiences if exp.success) / len(past_experiences)
        success_confidence = success_rate * 0.2
        
        return min(base_confidence + success_confidence, 1.0)
    
    def _calculate_emotional_dimensions(self, threat_level: ThreatLevel, 
                                      past_experiences: List[Experience], 
                                      emotional_weight: float) -> Tuple[float, float]:
        """感情の価値と覚醒度を計算"""
        # 価値（valence）: ポジティブ(+1.0) ↔ ネガティブ(-1.0)
        valence = 0.0
        
        if past_experiences:
            success_rate = sum(1 for exp in past_experiences if exp.success) / len(past_experiences)
            valence = (success_rate - 0.5) * 2.0  # -1.0 to 1.0
        
        # 脅威による価値の調整
        threat_penalty = (threat_level.value - 1) * 0.2
        valence -= threat_penalty
        
        # 覚醒度（arousal）: 低(0.0) ↔ 高(1.0)
        arousal = emotional_weight
        
        # 脅威による覚醒度増加
        arousal += (threat_level.value - 1) * 0.15
        
        return max(min(valence, 1.0), -1.0), max(min(arousal, 1.0), 0.0)
    
    def _determine_emotional_state(self, valence: float, arousal: float, 
                                 threat_level: ThreatLevel) -> EmotionalState:
        """感情状態の判定"""
        if threat_level == ThreatLevel.CRITICAL:
            return EmotionalState.ANXIOUS
        
        if valence > 0.3:
            if arousal > 0.6:
                return EmotionalState.CONFIDENT
            else:
                return EmotionalState.POSITIVE
        elif valence < -0.3:
            if arousal > 0.6:
                return EmotionalState.FRUSTRATED
            else:
                return EmotionalState.NEGATIVE
        else:
            if arousal > 0.7:
                return EmotionalState.ANXIOUS
            else:
                return EmotionalState.NEUTRAL
    
    async def get_task_priority_adjustment(self, task_description: str, task_type: str, 
                                         base_priority: float) -> float:
        """感情的評価に基づく優先度調整"""
        try:
            emotional_context = await self.evaluate_task_emotion(task_description, task_type)
            
            # 脅威レベルによる調整
            threat_adjustment = 0.0
            if emotional_context.threat_level == ThreatLevel.CRITICAL:
                threat_adjustment = -0.3  # 優先度を下げる
            elif emotional_context.threat_level == ThreatLevel.HIGH:
                threat_adjustment = -0.1
            elif emotional_context.threat_level == ThreatLevel.SAFE:
                threat_adjustment = 0.1   # 優先度を上げる
            
            # 信頼度による調整
            confidence_adjustment = emotional_context.confidence * 0.2
            
            # 感情状態による調整
            state_adjustment = 0.0
            if emotional_context.state == EmotionalState.CONFIDENT:
                state_adjustment = 0.15
            elif emotional_context.state == EmotionalState.FRUSTRATED:
                state_adjustment = -0.1
            elif emotional_context.state == EmotionalState.ANXIOUS:
                state_adjustment = -0.2
            
            # 総合調整
            total_adjustment = threat_adjustment + confidence_adjustment + state_adjustment
            adjusted_priority = base_priority + total_adjustment
            
            return max(min(adjusted_priority, 1.0), 0.0)
            
        except Exception as e:
            logging.error(f"❌ 優先度調整エラー: {e}")
            return base_priority
    
    def get_emotional_statistics(self) -> Dict[str, Any]:
        """感情システムの統計情報"""
        return {
            'current_state': self.current_emotional_state.value,
            'threat_detector': {
                'learned_threats': len(self.threat_detector.learned_threats)
            },
            'memory_manager': self.memory_manager.get_memory_statistics(),
            'reward_system': {
                'reward_history_size': len(self.reward_system.reward_history),
                'expected_rewards': len(self.reward_system.expected_rewards)
            },
            'emotional_history_size': len(self.emotional_history)
        }