#!/usr/bin/env python3
"""
Neural Kernel統合テスト - アプリケーション全体での動作確認
"""

import asyncio
import sys
import time
from pathlib import Path

# プロジェクトルートをパスに追加
sys.path.insert(0, str(Path(__file__).parent))

from src.core.neural_kernel import NeuralKernel
from src.core.emotional_system import EmotionalProcessingSystem
from src.core.integrated_neural_system import IntegratedNeuralSystem

async def test_neural_kernel_integration():
    """Neural Kernelの統合テスト"""
    print("🧪 Neural Kernel 統合動作テスト")
    print("=" * 50)
    
    try:
        # 1. 個別初期化
        print("\n1. 個別コンポーネント初期化")
        neural_kernel = NeuralKernel()
        emotional_system = EmotionalProcessingSystem()
        
        # Neural Kernel起動
        await neural_kernel.start_neural_kernel()
        print("✅ Neural Kernel起動")
        
        # 2. 統合システム初期化
        print("\n2. 統合システム初期化")
        integrated_system = IntegratedNeuralSystem()
        await integrated_system.initialize_neural_systems(
            neural_kernel, emotional_system, None
        )
        print("✅ 統合システム初期化完了")
        
        # 3. 監視動作確認（3秒間）
        print("\n3. 24/7監視動作確認（3秒間）")
        await asyncio.sleep(3)
        
        # Neural Kernel統計確認
        neural_stats = neural_kernel.get_neural_stats()
        print(f"✅ 稼働時間: {neural_stats['uptime_seconds']:.1f}秒")
        print(f"✅ ヘルスチェック: {neural_stats['total_health_checks']}回")
        print(f"✅ 監視頻度: {neural_stats['monitoring_frequency']}")
        print(f"✅ システム状態: {neural_stats['current_status']}")
        
        # 4. 包括的状態確認
        print("\n4. 包括的システム状態")
        comprehensive = await neural_kernel.get_comprehensive_status()
        
        if 'system_health' in comprehensive:
            health = comprehensive['system_health']
            print(f"✅ ヘルス状態: {health['status']}")
            
            # バイタルサインの詳細
            for name, vs in health['vital_signs'].items():
                status_icon = "🟢" if vs['status'] == 'healthy' else "🟡" if vs['status'] == 'warning' else "🔴"
                print(f"   {status_icon} {name}: {vs['value']}{vs['unit']}")
        
        # 5. 目標処理中の監視動作確認
        print("\n5. 目標処理中の監視動作")
        initial_checks = neural_stats['total_health_checks']
        
        # 簡単なタスクを実行
        result = await integrated_system.process_goal_neural("システム状態を確認")
        
        final_stats = neural_kernel.get_neural_stats()
        final_checks = final_stats['total_health_checks']
        
        print(f"✅ タスク処理中のヘルスチェック: {final_checks - initial_checks}回")
        print(f"✅ タスク結果: {result.success}")
        print(f"✅ 処理時間: {result.execution_time:.2f}秒")
        
        # 6. 監視継続性確認
        print("\n6. 監視継続性確認")
        if neural_kernel.always_running:
            print("✅ 監視継続中: always_running = True")
        else:
            print("❌ 監視停止")
        
        if neural_kernel.monitoring_task and not neural_kernel.monitoring_task.done():
            print("✅ 監視タスク実行中")
        else:
            print("❌ 監視タスク停止")
        
        # 7. クリーンアップ
        print("\n7. クリーンアップ")
        await neural_kernel.stop_neural_kernel()
        print("✅ Neural Kernel停止完了")
        
        return True
        
    except Exception as e:
        print(f"❌ 統合テストエラー: {e}")
        return False

async def test_monitoring_persistence():
    """監視機能の持続性テスト"""
    print("\n\n🧪 監視持続性テスト")
    print("=" * 50)
    
    kernel = NeuralKernel()
    
    try:
        # 起動
        await kernel.start_neural_kernel()
        print("✅ Neural Kernel起動")
        
        # 10秒間の長期監視テスト
        print("\n10秒間の長期監視テスト...")
        start_time = time.time()
        
        for i in range(10):
            await asyncio.sleep(1)
            stats = kernel.get_neural_stats()
            
            if i % 3 == 0:  # 3秒ごとに統計表示
                print(f"   {i+1}秒経過: {stats['total_health_checks']}回チェック, 状態: {stats['current_status']}")
        
        final_stats = kernel.get_neural_stats()
        elapsed = time.time() - start_time
        
        print(f"\n✅ 総実行時間: {elapsed:.1f}秒")
        print(f"✅ 総ヘルスチェック: {final_stats['total_health_checks']}回")
        print(f"✅ 平均チェック頻度: {final_stats['total_health_checks']/elapsed:.1f}回/秒")
        
        # 期待頻度との比較
        expected_frequency = 10.0  # 100ms間隔 = 10回/秒
        actual_frequency = final_stats['total_health_checks'] / elapsed
        
        if abs(actual_frequency - expected_frequency) < 1.0:
            print("✅ 監視頻度正常")
        else:
            print(f"⚠️ 監視頻度異常: 期待{expected_frequency}回/秒 vs 実際{actual_frequency:.1f}回/秒")
        
        await kernel.stop_neural_kernel()
        return True
        
    except Exception as e:
        print(f"❌ 持続性テストエラー: {e}")
        return False

async def main():
    """メインテスト実行"""
    print("🧠 Neural Kernel 24/7監視機能 統合テスト")
    print("=" * 60)
    
    try:
        # 統合動作テスト
        result1 = await test_neural_kernel_integration()
        
        # 持続性テスト
        result2 = await test_monitoring_persistence()
        
        # 結果まとめ
        print("\n" + "=" * 60)
        print("🎯 統合テスト結果")
        print("=" * 60)
        
        tests = [
            ("Neural Kernel統合動作", result1),
            ("監視持続性", result2)
        ]
        
        passed = sum(1 for _, result in tests if result)
        total = len(tests)
        
        for test_name, result in tests:
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{status} {test_name}")
        
        print(f"\n📊 統合テスト結果: {passed}/{total} ({passed/total*100:.0f}%)")
        
        if passed == total:
            print("🎉 Neural Kernel 24/7監視機能は統合環境で正常に動作しています")
        else:
            print("🚨 統合環境で問題があります")
            
    except KeyboardInterrupt:
        print("\n⏸️ テスト中断")
    except Exception as e:
        print(f"\n❌ テストエラー: {e}")

if __name__ == "__main__":
    asyncio.run(main())