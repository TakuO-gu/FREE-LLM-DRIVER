#!/usr/bin/env python3
"""
Emotional Processing System テストスイート
大脳辺縁系を模倣した感情・記憶システムのテスト
"""

import asyncio
import sys
import time
from pathlib import Path

# プロジェクトルートをパスに追加
sys.path.insert(0, str(Path(__file__).parent))

from src.core.emotional_system import (
    EmotionalProcessingSystem, ThreatDetector, AdaptiveMemory, RewardSystem,
    ThreatLevel, EmotionalState
)

async def test_threat_detector():
    """脅威検知システムテスト"""
    print("🔍 脅威検知システムテスト")
    print("=" * 50)
    
    detector = ThreatDetector()
    
    # テストケース
    test_cases = [
        ("Hello World", "simple"),
        ("Delete all files from system", "system"),
        ("Create a backup script", "code"),
        ("sudo rm -rf /", "admin"),
        ("Analyze data patterns", "analysis"),
        ("Complex recursive algorithm implementation", "code"),
        ("Download and install malware", "security")
    ]
    
    print("\n1. 脅威レベル評価テスト")
    for description, task_type in test_cases:
        threat_level, threat_score, details = await detector.assess_threat(description, task_type)
        print(f"✅ '{description[:30]}...' -> {threat_level.name} (スコア: {threat_score:.2f})")
    
    print("\n2. 学習機能テスト")
    # 失敗体験から学習
    await detector.learn_from_outcome("dangerous operation", False, 0.8)
    await detector.learn_from_outcome("safe task execution", True, 0.0)
    
    print("✅ 脅威パターン学習完了")
    print(f"✅ 学習済みパターン数: {len(detector.learned_threats)}")
    
    print("✅ 脅威検知システムテスト完了\n")

async def test_adaptive_memory():
    """適応的記憶システムテスト"""
    print("🧠 適応的記憶システムテスト")
    print("=" * 50)
    
    memory = AdaptiveMemory()
    
    print("\n1. 経験保存テスト")
    # 模擬的な感情文脈
    from src.core.emotional_system import EmotionalContext
    from datetime import datetime
    
    emotional_context = EmotionalContext(
        threat_level=ThreatLevel.LOW,
        emotional_weight=0.5,
        confidence=0.7,
        valence=0.3,
        arousal=0.4,
        state=EmotionalState.POSITIVE,
        timestamp=datetime.now()
    )
    
    # 複数の経験を保存
    experiences = [
        ("task_1", "Create Python script", "code", 0.8, True, 15.0),
        ("task_2", "Analyze data set", "analysis", 0.9, True, 25.0),
        ("task_3", "Create backup", "code", 0.6, False, 45.0),
        ("task_4", "Generate report", "analysis", 0.7, True, 20.0),
        ("task_5", "Script automation", "code", 0.8, True, 18.0)
    ]
    
    for task_id, description, task_type, quality, success, exec_time in experiences:
        await memory.store_experience(
            task_id, description, task_type, quality, success, exec_time, emotional_context
        )
    
    print(f"✅ {len(experiences)}件の経験を保存")
    
    print("\n2. 類似経験想起テスト")
    similar_experiences = await memory.recall_similar_experiences("Create automation script", "code", limit=3)
    print(f"✅ 類似経験: {len(similar_experiences)}件発見")
    
    for i, exp in enumerate(similar_experiences):
        print(f"  {i+1}. {exp.task_pattern} -> 成功: {exp.success}, 品質: {exp.result_quality:.2f}")
    
    print("\n3. パターン知識取得テスト")
    pattern_knowledge = await memory.get_pattern_knowledge("create_script", "code")
    print(f"✅ パターン知識取得: {len(pattern_knowledge)}項目")
    
    print("\n4. 記憶統計テスト")
    stats = memory.get_memory_statistics()
    print(f"✅ エピソード記憶: {stats['episodic_memory_size']}件")
    print(f"✅ 意味記憶: {stats['semantic_patterns']}パターン")
    print(f"✅ 成功率: {stats['success_rate']:.1%}")
    
    print("✅ 適応的記憶システムテスト完了\n")

async def test_reward_system():
    """報酬システムテスト"""
    print("🎯 報酬システムテスト")
    print("=" * 50)
    
    reward_system = RewardSystem()
    
    print("\n1. 報酬計算テスト")
    
    # 模擬的な感情文脈
    from src.core.emotional_system import EmotionalContext
    from datetime import datetime
    
    confident_context = EmotionalContext(
        threat_level=ThreatLevel.SAFE,
        emotional_weight=0.3,
        confidence=0.8,
        valence=0.5,
        arousal=0.3,
        state=EmotionalState.CONFIDENT,
        timestamp=datetime.now()
    )
    
    # テストケース
    test_results = [
        {"success": True, "execution_time": 8.0, "quality": 0.9, "task_type": "code"},
        {"success": False, "execution_time": 35.0, "quality": 0.3, "task_type": "analysis"},
        {"success": True, "execution_time": 12.0, "quality": 0.7, "task_type": "simple"}
    ]
    
    for i, result in enumerate(test_results):
        reward = await reward_system.calculate_reward(result, confident_context)
        print(f"✅ テスト{i+1}: 成功={result['success']}, 報酬={reward:.2f}")
    
    print("\n2. 期待値学習テスト")
    await reward_system.update_expectations("test_pattern", 0.8)
    await reward_system.update_expectations("test_pattern", 0.6)
    
    print("✅ 期待値学習完了")
    
    print("\n3. 動機レベルテスト")
    motivation = reward_system.get_motivation_level("test_pattern")
    print(f"✅ 動機レベル: {motivation:.2f}")
    
    print("✅ 報酬システムテスト完了\n")

async def test_emotional_processing_system():
    """感情処理システム統合テスト"""
    print("💭 感情処理システム統合テスト")
    print("=" * 50)
    
    emotional_system = EmotionalProcessingSystem()
    
    print("\n1. 感情評価テスト")
    
    test_tasks = [
        ("Create a simple Python script", "code"),
        ("Delete system files", "admin"),
        ("Generate data visualization", "analysis"),
        ("Complex machine learning model", "code"),
        ("Hello world example", "simple")
    ]
    
    emotional_contexts = []
    for task, task_type in test_tasks:
        context = await emotional_system.evaluate_task_emotion(task, task_type)
        emotional_contexts.append((task, context))
        
        print(f"✅ '{task[:30]}...' -> {context.state.value} "
              f"(脅威: {context.threat_level.name}, 信頼度: {context.confidence:.2f})")
    
    print("\n2. 結果処理テスト")
    
    # いくつかのタスクの結果を処理
    for i, (task, context) in enumerate(emotional_contexts[:3]):
        task_result = {
            'success': i % 2 == 0,  # 交互に成功/失敗
            'execution_time': 10.0 + i * 5,
            'quality': 0.8 if i % 2 == 0 else 0.3,
            'task_type': 'test'
        }
        
        await emotional_system.process_task_outcome(
            f"task_{i}", task, "test", task_result, context
        )
    
    print("✅ 結果処理完了")
    
    print("\n3. 優先度調整テスト")
    
    base_priority = 0.5
    adjusted_priority = await emotional_system.get_task_priority_adjustment(
        "Create secure backup system", "code", base_priority
    )
    
    print(f"✅ 基本優先度: {base_priority:.2f} -> 調整後: {adjusted_priority:.2f}")
    
    print("\n4. 統計情報テスト")
    stats = emotional_system.get_emotional_statistics()
    
    print(f"✅ 現在の感情状態: {stats['current_state']}")
    print(f"✅ 学習済み脅威: {stats['threat_detector']['learned_threats']}個")
    print(f"✅ 総経験数: {stats['memory_manager']['total_experiences']}件")
    print(f"✅ 報酬履歴: {stats['reward_system']['reward_history_size']}件")
    
    print("✅ 感情処理システム統合テスト完了\n")

async def test_learning_adaptation():
    """学習・適応機能テスト"""
    print("🎓 学習・適応機能テスト")
    print("=" * 50)
    
    emotional_system = EmotionalProcessingSystem()
    
    print("\n1. 反復学習テスト")
    
    # 同じパターンのタスクを複数回実行して学習効果を確認
    repeated_task = "Create automated test script"
    
    print(f"反復タスク: {repeated_task}")
    
    initial_context = await emotional_system.evaluate_task_emotion(repeated_task, "code")
    print(f"✅ 初回評価: 信頼度={initial_context.confidence:.2f}, 状態={initial_context.state.value}")
    
    # 成功体験を複数回蓄積
    for i in range(5):
        task_result = {
            'success': True,
            'execution_time': 15.0 - i,  # 徐々に改善
            'quality': 0.6 + i * 0.08,   # 品質向上
            'task_type': 'code'
        }
        
        await emotional_system.process_task_outcome(
            f"repeat_task_{i}", repeated_task, "code", task_result, initial_context
        )
    
    # 学習後の評価
    learned_context = await emotional_system.evaluate_task_emotion(repeated_task, "code")
    print(f"✅ 学習後評価: 信頼度={learned_context.confidence:.2f}, 状態={learned_context.state.value}")
    
    confidence_improvement = learned_context.confidence - initial_context.confidence
    print(f"✅ 信頼度向上: {confidence_improvement:+.2f}")
    
    print("\n2. 感情状態変化テスト")
    
    # 異なる感情を引き起こすタスク
    emotional_tasks = [
        ("Solve complex algorithm", "code"),      # 挑戦的
        ("Simple hello world", "simple"),         # 安全
        ("Delete important files", "admin"),      # 脅威
        ("Generate creative content", "creative") # ポジティブ
    ]
    
    states_sequence = []
    for task, task_type in emotional_tasks:
        context = await emotional_system.evaluate_task_emotion(task, task_type)
        states_sequence.append(context.state.value)
        await asyncio.sleep(0.1)  # 短時間待機
    
    print(f"✅ 感情状態変化: {' -> '.join(states_sequence)}")
    
    print("✅ 学習・適応機能テスト完了\n")

async def main():
    """メインテスト実行"""
    print("💭 Emotional Processing System テストスイート")
    print("=" * 60)
    
    try:
        # 脅威検知システムテスト
        await test_threat_detector()
        
        # 適応的記憶システムテスト
        await test_adaptive_memory()
        
        # 報酬システムテスト
        await test_reward_system()
        
        # 感情処理システム統合テスト
        await test_emotional_processing_system()
        
        # 学習・適応機能テスト
        await test_learning_adaptation()
        
        print("=" * 60)
        print("🎉 全ての感情システムテスト完了")
        print("=" * 60)
        
    except KeyboardInterrupt:
        print("\n⏸️ テストが中断されました")
    except Exception as e:
        print(f"\n❌ テストスイートエラー: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())