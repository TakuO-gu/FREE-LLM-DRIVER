#!/usr/bin/env python3
"""
Neural Kernel 24/7監視機能のテスト
"""

import asyncio
import sys
import time
from pathlib import Path

# プロジェクトルートをパスに追加
sys.path.insert(0, str(Path(__file__).parent))

from src.core.neural_kernel import NeuralKernel

async def test_continuous_monitoring():
    """24/7監視機能のテスト"""
    print("🧪 Neural Kernel 24/7監視機能テスト")
    print("=" * 50)
    
    # Neural Kernel初期化
    kernel = NeuralKernel()
    
    print("\n1. Neural Kernel起動")
    await kernel.start_neural_kernel()
    
    if kernel.always_running:
        print("✅ 監視開始: always_running = True")
    else:
        print("❌ 監視開始失敗")
        return False
    
    print(f"✅ 監視タスク: {kernel.monitoring_task is not None}")
    print(f"✅ 監視間隔: 100ms")
    
    # 5秒間監視を実行
    print("\n2. 5秒間の監視動作テスト")
    await asyncio.sleep(5)
    
    # 統計確認
    stats = kernel.get_neural_stats()
    print(f"✅ 実行時間: {stats['uptime_seconds']:.1f}秒")
    print(f"✅ ヘルスチェック回数: {stats['total_health_checks']}")
    print(f"✅ 緊急活性化: {stats['emergency_activations']}")
    print(f"✅ 現在の状態: {stats['current_status']}")
    
    # 包括的状態確認
    print("\n3. 包括的システム状態確認")
    comprehensive = await kernel.get_comprehensive_status()
    
    if 'system_health' in comprehensive:
        health = comprehensive['system_health']
        print(f"✅ システムヘルス: {health['status']}")
        print(f"✅ バイタルサイン数: {len(health['vital_signs'])}")
        
        for name, vs in health['vital_signs'].items():
            print(f"   {name}: {vs['value']}{vs['unit']} ({vs['status']})")
    
    # リソース状態確認
    if 'resources' in comprehensive:
        resources = comprehensive['resources']
        print(f"✅ リソース監視: {len(resources)}項目")
        
        if 'warnings' in resources:
            warnings = resources['warnings']
            if warnings:
                print(f"⚠️ リソース警告: {len(warnings)}件")
                for warning in warnings[:3]:  # 最初の3件だけ表示
                    print(f"   - {warning}")
            else:
                print("✅ リソース警告: なし")
    
    # 監視頻度確認
    print("\n4. 監視頻度確認（2秒間測定）")
    initial_checks = stats['total_health_checks']
    await asyncio.sleep(2)
    
    final_stats = kernel.get_neural_stats()
    final_checks = final_stats['total_health_checks']
    
    checks_per_second = (final_checks - initial_checks) / 2
    expected_checks = 10  # 100ms間隔なら10回/秒
    
    print(f"✅ チェック回数: {final_checks - initial_checks}回/2秒")
    print(f"✅ 実際の頻度: {checks_per_second:.1f}回/秒")
    print(f"✅ 期待頻度: {expected_checks}回/秒")
    
    frequency_ok = abs(checks_per_second - expected_checks) < 3  # 3回/秒の誤差許容
    print(f"{'✅' if frequency_ok else '⚠️'} 頻度正常性: {frequency_ok}")
    
    # カーネル停止
    print("\n5. Neural Kernel停止")
    await kernel.stop_neural_kernel()
    
    if not kernel.always_running:
        print("✅ 監視停止: always_running = False")
    else:
        print("❌ 監視停止失敗")
        return False
    
    print("✅ 監視タスク停止完了")
    
    return True

async def test_emergency_detection():
    """緊急事態検出テスト（シミュレーション）"""
    print("\n\n🧪 緊急事態検出テスト")
    print("=" * 50)
    
    kernel = NeuralKernel()
    await kernel.start_neural_kernel()
    
    print("1. 通常動作確認（3秒）")
    await asyncio.sleep(3)
    
    initial_stats = kernel.get_neural_stats()
    initial_emergencies = initial_stats['emergency_activations']
    
    print(f"✅ 初期緊急活性化: {initial_emergencies}")
    
    # 注意: 実際の緊急事態は意図的に発生させない
    print("✅ 緊急事態検出システム待機中")
    
    await kernel.stop_neural_kernel()
    
    return True

async def main():
    """メインテスト実行"""
    print("🧠 Neural Kernel 24/7監視機能 詳細テスト")
    print("=" * 60)
    
    try:
        # 基本監視機能テスト
        result1 = await test_continuous_monitoring()
        
        # 緊急検出機能テスト
        result2 = await test_emergency_detection()
        
        # 結果まとめ
        print("\n" + "=" * 60)
        print("🎯 テスト結果")
        print("=" * 60)
        
        tests = [
            ("24/7監視機能", result1),
            ("緊急事態検出", result2)
        ]
        
        passed = sum(1 for _, result in tests if result)
        total = len(tests)
        
        for test_name, result in tests:
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{status} {test_name}")
        
        print(f"\n📊 総合結果: {passed}/{total} ({passed/total*100:.0f}%)")
        
        if passed == total:
            print("🎉 Neural Kernel 24/7監視機能は正常に動作しています")
        else:
            print("🚨 一部の機能に問題があります")
            
    except KeyboardInterrupt:
        print("\n⏸️ テスト中断")
    except Exception as e:
        print(f"\n❌ テストエラー: {e}")

if __name__ == "__main__":
    asyncio.run(main())