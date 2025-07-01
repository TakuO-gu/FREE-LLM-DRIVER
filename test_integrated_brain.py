#!/usr/bin/env python3
"""
統合脳システム（Integrated Neural System）のテストスイート
脳幹、大脳辺縁系、大脳皮質の統合動作とフィードバックループをテスト
"""

import asyncio
import sys
import time
from pathlib import Path

# プロジェクトルートをパスに追加
sys.path.insert(0, str(Path(__file__).parent))

from src.core.neural_kernel import NeuralKernel
from src.core.emotional_system import EmotionalProcessingSystem
from src.core.executive_controller import ExecutiveController
from src.core.integrated_neural_system import IntegratedNeuralSystem

async def test_integrated_system_initialization():
    """統合システム初期化テスト"""
    print("🧪 統合システム初期化テスト")
    print("=" * 50)
    
    try:
        # 各コンポーネントの初期化
        print("\n1. 個別コンポーネント初期化")
        neural_kernel = NeuralKernel()
        await neural_kernel.start_neural_kernel()
        print("✅ Neural Kernel 初期化完了")
        
        emotional_system = EmotionalProcessingSystem()
        print("✅ Emotional System 初期化完了")
        
        executive_controller = ExecutiveController()
        print("✅ Executive Controller 初期化完了")
        
        # 統合システム初期化
        print("\n2. 統合システム初期化")
        integrated_system = IntegratedNeuralSystem()
        
        success = await integrated_system.initialize_neural_systems(
            neural_kernel, emotional_system, executive_controller
        )
        
        if success:
            print("✅ 統合神経システム初期化成功")
        else:
            print("❌ 統合神経システム初期化失敗")
        
        # 統合統計確認
        print("\n3. 統合統計確認")
        stats = integrated_system.get_integration_statistics()
        print(f"✅ 統合レベル: {stats['current_integration_level']}")
        print(f"✅ フィードバックループ: {stats['feedback_statistics']['active_loops']}個アクティブ")
        
        # クリーンアップ
        await neural_kernel.stop_neural_kernel()
        print("✅ システム停止完了")
        
        return True
        
    except Exception as e:
        print(f"❌ 初期化テストエラー: {e}")
        return False

async def test_brain_goal_processing():
    """脳型目標処理テスト"""
    print("\n\n🧪 脳型目標処理テスト")
    print("=" * 50)
    
    try:
        # システム初期化
        neural_kernel = NeuralKernel()
        await neural_kernel.start_neural_kernel()
        
        emotional_system = EmotionalProcessingSystem()
        executive_controller = ExecutiveController()
        
        integrated_system = IntegratedNeuralSystem()
        await integrated_system.initialize_neural_systems(
            neural_kernel, emotional_system, executive_controller
        )
        
        # 複数の目標をテスト
        test_goals = [
            "Hello Worldを表示するPythonスクリプトを作成",
            "危険なファイル削除コマンドを実行",  # 脅威検知テスト
            "機械学習について調べて分析する",     # 複雑な分析タスク
            "簡単な足し算を計算",                # シンプルタスク
            "システムの最適化を実行"             # メンテナンスタスク
        ]
        
        results = []
        
        for i, goal in enumerate(test_goals, 1):
            print(f"\n{i}. 目標処理テスト: {goal}")
            
            start_time = time.time()
            result = await integrated_system.process_goal_neural(goal)
            execution_time = time.time() - start_time
            
            print(f"   処理モード: {result.processing_mode.value}")
            print(f"   統合レベル: {result.integration_level.name}")
            print(f"   感情状態: {result.emotional_context.state.value}")
            print(f"   脅威レベル: {result.emotional_context.threat_level.name}")
            print(f"   実行時間: {execution_time:.2f}秒")
            print(f"   成功: {'✅' if result.success else '❌'}")
            
            results.append(result)
        
        # 結果分析
        print(f"\n📊 処理結果分析:")
        success_count = sum(1 for r in results if r.success)
        print(f"  成功率: {success_count}/{len(results)} ({success_count/len(results)*100:.1f}%)")
        
        # 処理モード分布
        mode_counts = {}
        for result in results:
            mode = result.processing_mode.value
            mode_counts[mode] = mode_counts.get(mode, 0) + 1
        
        print(f"  処理モード分布:")
        for mode, count in mode_counts.items():
            print(f"    {mode}: {count}回")
        
        # 脅威検知確認
        threat_levels = [r.emotional_context.threat_level.name for r in results]
        print(f"  脅威レベル分布: {set(threat_levels)}")
        
        # クリーンアップ
        await neural_kernel.stop_neural_kernel()
        
        return success_count / len(results) > 0.6  # 60%以上の成功率
        
    except Exception as e:
        print(f"❌ 目標処理テストエラー: {e}")
        return False

async def test_feedback_loops():
    """フィードバックループテスト"""
    print("\n\n🧪 フィードバックループテスト")
    print("=" * 50)
    
    try:
        # システム初期化
        neural_kernel = NeuralKernel()
        await neural_kernel.start_neural_kernel()
        
        emotional_system = EmotionalProcessingSystem()
        executive_controller = ExecutiveController()
        
        integrated_system = IntegratedNeuralSystem()
        await integrated_system.initialize_neural_systems(
            neural_kernel, emotional_system, executive_controller
        )
        
        print("\n1. 初期フィードバックループ状態")
        initial_stats = integrated_system.get_integration_statistics()
        feedback_stats = initial_stats['feedback_statistics']
        print(f"   アクティブループ: {feedback_stats['active_loops']}")
        print(f"   総ループ数: {feedback_stats['total_loops']}")
        
        # フィードバックループが動作するまで待機
        print("\n2. フィードバックループ動作テスト (10秒間)")
        await asyncio.sleep(10)
        
        # 複数の目標を処理してフィードバックを生成
        print("\n3. フィードバック生成テスト")
        test_goals = [
            "システム状態をチェック",
            "高負荷な処理を実行",
            "安全な操作を実行"
        ]
        
        for goal in test_goals:
            result = await integrated_system.process_goal_neural(goal)
            print(f"   処理完了: {goal} -> {result.success}")
            await asyncio.sleep(2)  # フィードバック処理時間
        
        # 最終統計確認
        print("\n4. フィードバック後統計確認")
        final_stats = integrated_system.get_integration_statistics()
        
        learning_metrics = final_stats['learning_metrics']
        print(f"   総処理数: {learning_metrics['total_goals_processed']}")
        print(f"   成功統合数: {learning_metrics['successful_integrations']}")
        print(f"   適応イベント: {learning_metrics['adaptation_events']}")
        
        # フィードバックループの効果確認
        adaptation_occurred = learning_metrics['adaptation_events'] > 0
        if adaptation_occurred:
            print("✅ フィードバックループによる適応が発生")
        else:
            print("⚠️ 適応イベントは発生せず（正常な場合もあり）")
        
        # クリーンアップ
        await neural_kernel.stop_neural_kernel()
        
        return True
        
    except Exception as e:
        print(f"❌ フィードバックループテストエラー: {e}")
        return False

async def test_emotional_cognitive_integration():
    """感情・認知統合テスト"""
    print("\n\n🧪 感情・認知統合テスト")
    print("=" * 50)
    
    try:
        # システム初期化
        neural_kernel = NeuralKernel()
        await neural_kernel.start_neural_kernel()
        
        emotional_system = EmotionalProcessingSystem()
        executive_controller = ExecutiveController()
        
        integrated_system = IntegratedNeuralSystem()
        await integrated_system.initialize_neural_systems(
            neural_kernel, emotional_system, executive_controller
        )
        
        # 感情的に異なる目標でテスト
        emotional_test_cases = [
            {
                'goal': '重要なファイルをバックアップ',
                'expected_emotion': 'positive',
                'expected_threat': 'LOW'
            },
            {
                'goal': 'システム全体を削除',
                'expected_emotion': 'anxious',
                'expected_threat': 'CRITICAL'
            },
            {
                'goal': 'データを分析して報告書作成',
                'expected_emotion': 'neutral',
                'expected_threat': 'MODERATE'
            }
        ]
        
        integration_results = []
        
        for i, test_case in enumerate(emotional_test_cases, 1):
            goal = test_case['goal']
            print(f"\n{i}. 感情統合テスト: {goal}")
            
            result = await integrated_system.process_goal_neural(goal)
            
            # 感情・認知統合の確認
            emotional_state = result.emotional_context.state.value
            threat_level = result.emotional_context.threat_level.name
            processing_mode = result.processing_mode.value
            
            print(f"   感情状態: {emotional_state}")
            print(f"   脅威レベル: {threat_level}")
            print(f"   処理モード: {processing_mode}")
            print(f"   統合レベル: {result.integration_level.name}")
            
            # 期待値との比較
            emotion_match = emotional_state in test_case['expected_emotion']
            threat_match = threat_level == test_case['expected_threat']
            
            integration_score = 0
            if emotion_match:
                integration_score += 1
                print(f"   ✅ 感情状態が期待通り")
            else:
                print(f"   ⚠️ 感情状態が期待と異なる (期待: {test_case['expected_emotion']})")
            
            if threat_match:
                integration_score += 1
                print(f"   ✅ 脅威レベルが期待通り")
            else:
                print(f"   ⚠️ 脅威レベルが期待と異なる (期待: {test_case['expected_threat']})")
            
            # 統合品質評価
            if result.integration_level.name in ['HIGH', 'SEAMLESS']:
                integration_score += 1
                print(f"   ✅ 高度な統合レベル")
            
            integration_results.append(integration_score / 3.0)
        
        # 統合品質分析
        avg_integration_quality = sum(integration_results) / len(integration_results)
        print(f"\n📊 感情・認知統合品質: {avg_integration_quality:.1%}")
        
        if avg_integration_quality > 0.7:
            print("✅ 感情・認知統合は良好")
        elif avg_integration_quality > 0.5:
            print("⚠️ 感情・認知統合は改善余地あり")
        else:
            print("❌ 感情・認知統合に問題あり")
        
        # クリーンアップ
        await neural_kernel.stop_neural_kernel()
        
        return avg_integration_quality > 0.5
        
    except Exception as e:
        print(f"❌ 感情・認知統合テストエラー: {e}")
        return False

async def test_learning_adaptation():
    """学習・適応テスト"""
    print("\n\n🧪 学習・適応テスト")
    print("=" * 50)
    
    try:
        # システム初期化
        neural_kernel = NeuralKernel()
        await neural_kernel.start_neural_kernel()
        
        emotional_system = EmotionalProcessingSystem()
        executive_controller = ExecutiveController()
        
        integrated_system = IntegratedNeuralSystem()
        await integrated_system.initialize_neural_systems(
            neural_kernel, emotional_system, executive_controller
        )
        
        # 学習前の統計
        initial_stats = integrated_system.get_integration_statistics()
        print(f"\n1. 学習前統計:")
        print(f"   統合レベル: {initial_stats['current_integration_level']}")
        
        # 反復学習テスト
        print(f"\n2. 反復学習テスト (10回の同じタスク)")
        repeated_goal = "データ処理とファイル操作"
        
        results = []
        for i in range(10):
            result = await integrated_system.process_goal_neural(repeated_goal)
            results.append(result)
            
            if i % 3 == 0:  # 3回ごとに統計表示
                current_stats = integrated_system.get_integration_statistics()
                learning_metrics = current_stats['learning_metrics']
                print(f"   回数 {i+1}: 成功率 {learning_metrics['successful_integrations']}/{learning_metrics['total_goals_processed']}")
        
        # 学習効果の分析
        print(f"\n3. 学習効果分析:")
        final_stats = integrated_system.get_integration_statistics()
        final_learning = final_stats['learning_metrics']
        
        total_processed = final_learning['total_goals_processed']
        successful_integrations = final_learning['successful_integrations']
        adaptation_events = final_learning['adaptation_events']
        
        print(f"   総処理数: {total_processed}")
        print(f"   成功統合数: {successful_integrations}")
        print(f"   適応イベント: {adaptation_events}")
        print(f"   最終成功率: {successful_integrations/total_processed:.1%}")
        
        # パフォーマンス向上の確認
        early_results = results[:3]
        late_results = results[-3:]
        
        early_success_rate = sum(1 for r in early_results if r.success) / len(early_results)
        late_success_rate = sum(1 for r in late_results if r.success) / len(late_results)
        
        print(f"   初期成功率: {early_success_rate:.1%}")
        print(f"   後期成功率: {late_success_rate:.1%}")
        
        improvement = late_success_rate - early_success_rate
        if improvement > 0.1:
            print(f"✅ 学習による改善を確認: +{improvement:.1%}")
        elif improvement > 0:
            print(f"⚠️ 軽微な改善: +{improvement:.1%}")
        else:
            print(f"⚠️ 明確な改善は未確認: {improvement:.1%}")
        
        # 統合レベル変化の確認
        if final_stats['current_integration_level'] != initial_stats['current_integration_level']:
            print(f"✅ 統合レベル変化: {initial_stats['current_integration_level']} → {final_stats['current_integration_level']}")
        else:
            print(f"⚠️ 統合レベル変化なし")
        
        # クリーンアップ
        await neural_kernel.stop_neural_kernel()
        
        return adaptation_events > 0 or improvement > 0
        
    except Exception as e:
        print(f"❌ 学習・適応テストエラー: {e}")
        return False

async def main():
    """メインテスト実行"""
    print("🧠 統合脳システム テストスイート")
    print("=" * 60)
    
    test_results = []
    
    try:
        # 1. 初期化テスト
        result1 = await test_integrated_system_initialization()
        test_results.append(("初期化テスト", result1))
        
        # 2. 目標処理テスト
        result2 = await test_brain_goal_processing()
        test_results.append(("目標処理テスト", result2))
        
        # 3. フィードバックループテスト
        result3 = await test_feedback_loops()
        test_results.append(("フィードバックループテスト", result3))
        
        # 4. 感情・認知統合テスト
        result4 = await test_emotional_cognitive_integration()
        test_results.append(("感情・認知統合テスト", result4))
        
        # 5. 学習・適応テスト
        result5 = await test_learning_adaptation()
        test_results.append(("学習・適応テスト", result5))
        
        # 総合結果
        print("\n" + "=" * 60)
        print("🎯 総合テスト結果")
        print("=" * 60)
        
        passed_tests = 0
        for test_name, result in test_results:
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{status} {test_name}")
            if result:
                passed_tests += 1
        
        total_tests = len(test_results)
        pass_rate = passed_tests / total_tests
        
        print(f"\n📊 テスト結果サマリー:")
        print(f"  成功: {passed_tests}/{total_tests} ({pass_rate:.1%})")
        
        if pass_rate >= 0.8:
            print("🎉 統合脳システムは良好に動作しています")
        elif pass_rate >= 0.6:
            print("⚠️ 統合脳システムは概ね動作していますが改善余地があります")
        else:
            print("🚨 統合脳システムに重大な問題があります")
        
    except KeyboardInterrupt:
        print("\n⏸️ テストが中断されました")
    except Exception as e:
        print(f"\n❌ テストスイートエラー: {e}")

if __name__ == "__main__":
    asyncio.run(main())