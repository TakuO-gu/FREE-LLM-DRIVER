#!/usr/bin/env python3
"""
Neural Kernelシステムの単体テスト
生物学的脳幹機能を模倣した常時監視システムのテスト
"""

import asyncio
import sys
import time
from pathlib import Path

# プロジェクトルートをパスに追加
sys.path.insert(0, str(Path(__file__).parent))

from src.core.neural_kernel import NeuralKernel, SystemStatus

async def test_neural_kernel_basic():
    """Neural Kernel基本機能テスト"""
    print("🧪 Neural Kernel 基本機能テスト")
    print("=" * 50)
    
    # Neural Kernel初期化
    kernel = NeuralKernel()
    
    try:
        # 起動テスト
        print("\n1. 起動テスト")
        await kernel.start_neural_kernel()
        print("✅ Neural Kernel 起動成功")
        
        # 短時間待機（監視動作確認）
        print("\n2. 監視動作テスト (5秒間)")
        await asyncio.sleep(5)
        
        # 統計情報取得
        stats = kernel.get_neural_stats()
        print(f"✅ 統計情報取得成功:")
        print(f"   稼働状態: {stats['running']}")
        print(f"   稼働時間: {stats['uptime_seconds']:.1f}秒")
        print(f"   ヘルスチェック回数: {stats['total_health_checks']}")
        print(f"   現在の状態: {stats['current_status']}")
        
        # 包括的状態取得テスト
        print("\n3. 包括的状態取得テスト")
        comprehensive_status = await kernel.get_comprehensive_status()
        
        system_health = comprehensive_status.get('system_health', {})
        print(f"✅ システムヘルス: {system_health.get('status', 'unknown')}")
        
        vital_signs = system_health.get('vital_signs', {})
        print(f"✅ バイタルサイン取得: {len(vital_signs)}項目")
        for name, vs in vital_signs.items():
            print(f"   {name}: {vs['value']:.1f}{vs['unit']} ({vs['status']})")
        
        resources = comprehensive_status.get('resources', {})
        print(f"✅ リソース監視: {resources.get('status', 'unknown')}")
        
        # 停止テスト
        print("\n4. 停止テスト")
        await kernel.stop_neural_kernel()
        print("✅ Neural Kernel 停止成功")
        
        print("\n🎉 基本機能テスト完了")
        
    except Exception as e:
        print(f"❌ テストエラー: {e}")
        # 確実に停止
        try:
            await kernel.stop_neural_kernel()
        except:
            pass

async def test_health_monitoring():
    """ヘルス監視機能テスト"""
    print("\n\n🧪 ヘルス監視機能テスト")
    print("=" * 50)
    
    kernel = NeuralKernel()
    
    try:
        await kernel.start_neural_kernel()
        
        # ヘルスモニターの個別テスト
        health_monitor = kernel.vital_monitors['system_health']
        
        print("\n1. システムバイタルチェック")
        health = await health_monitor.check_system_vitals()
        print(f"✅ システム状態: {health.overall_status.value}")
        print(f"✅ バイタルサイン数: {len(health.vital_signs)}")
        print(f"✅ アラート数: {len(health.alerts)}")
        
        # 複数回チェックしてトレンド確認
        print("\n2. トレンド分析テスト (10回チェック)")
        for i in range(10):
            await health_monitor.check_system_vitals()
            await asyncio.sleep(0.1)
        
        trend = health_monitor.get_health_trend(minutes=1)
        print(f"✅ トレンド分析: {trend.get('trend', 'no_data')}")
        print(f"✅ サンプル数: {trend.get('sample_count', 0)}")
        
        await kernel.stop_neural_kernel()
        print("✅ ヘルス監視テスト完了")
        
    except Exception as e:
        print(f"❌ ヘルス監視テストエラー: {e}")
        try:
            await kernel.stop_neural_kernel()
        except:
            pass

async def test_resource_monitoring():
    """リソース監視機能テスト"""
    print("\n\n🧪 リソース監視機能テスト") 
    print("=" * 50)
    
    kernel = NeuralKernel()
    
    try:
        await kernel.start_neural_kernel()
        
        # リソースモニターの個別テスト
        resource_monitor = kernel.vital_monitors['resource_monitor']
        
        print("\n1. リソース使用量チェック")
        resource_status = await resource_monitor.check_resource_usage()
        
        usage = resource_status.get('usage', {})
        print(f"✅ メモリ使用量: {usage.get('memory_mb', 0):.1f}MB")
        print(f"✅ CPU時間: {usage.get('cpu_time', 0):.1f}秒")
        print(f"✅ ファイルハンドル: {usage.get('file_handles', 0)}個")
        print(f"✅ ネットワーク接続: {usage.get('network_connections', 0)}個")
        
        warnings = resource_status.get('warnings', [])
        if warnings:
            print(f"⚠️ 警告: {len(warnings)}件")
            for warning in warnings:
                print(f"   - {warning}")
        else:
            print("✅ 警告なし")
        
        await kernel.stop_neural_kernel()
        print("✅ リソース監視テスト完了")
        
    except Exception as e:
        print(f"❌ リソース監視テストエラー: {e}")
        try:
            await kernel.stop_neural_kernel()
        except:
            pass

async def test_emergency_handler():
    """緊急対応システムテスト"""
    print("\n\n🧪 緊急対応システムテスト")
    print("=" * 50)
    
    kernel = NeuralKernel()
    
    try:
        await kernel.start_neural_kernel()
        
        # 模擬的な緊急事態を作成
        from src.core.neural_kernel import SystemHealth, VitalSign
        from datetime import datetime
        
        # 危険なバイタルサインを作成
        critical_vital = VitalSign(
            name="テスト用CPU使用率",
            value=98.0,  # 危険レベル
            threshold_warning=80.0,
            threshold_critical=95.0,
            unit="%"
        )
        
        mock_health = SystemHealth(
            overall_status=SystemStatus.CRITICAL,
            vital_signs={'test_cpu': critical_vital},
            alerts=['🚨 テスト用緊急事態'],
            timestamp=datetime.now()
        )
        
        print("\n1. 緊急対応テスト")
        emergency_handler = kernel.vital_monitors['emergency_handler']
        
        # 緊急対応実行
        await emergency_handler.activate(mock_health)
        print("✅ 緊急対応処理実行")
        
        # 緊急ログ確認
        if emergency_handler.emergency_log:
            print(f"✅ 緊急ログ記録: {len(emergency_handler.emergency_log)}件")
            last_log = emergency_handler.emergency_log[-1]
            print(f"   最新ログ: {last_log['status']} ({len(last_log['alerts'])}アラート)")
        
        await kernel.stop_neural_kernel()
        print("✅ 緊急対応テスト完了")
        
    except Exception as e:
        print(f"❌ 緊急対応テストエラー: {e}")
        try:
            await kernel.stop_neural_kernel()
        except:
            pass

async def test_long_running():
    """長時間実行テスト"""
    print("\n\n🧪 長時間実行テスト (30秒)")
    print("=" * 50)
    
    kernel = NeuralKernel()
    
    try:
        await kernel.start_neural_kernel()
        
        print("Neural Kernel 長時間監視開始...")
        start_time = time.time()
        
        # 30秒間実行
        while time.time() - start_time < 30:
            await asyncio.sleep(5)
            
            # 統計情報表示
            stats = kernel.get_neural_stats()
            elapsed = time.time() - start_time
            print(f"経過時間: {elapsed:.1f}s | "
                  f"ヘルスチェック: {stats['total_health_checks']} | "
                  f"状態: {stats['current_status']}")
        
        # 最終統計
        final_stats = kernel.get_neural_stats()
        print(f"\n✅ 長時間実行テスト完了")
        print(f"   総ヘルスチェック: {final_stats['total_health_checks']}")
        print(f"   稼働時間: {final_stats['uptime_seconds']:.1f}秒")
        print(f"   緊急対応回数: {final_stats['emergency_activations']}")
        
        await kernel.stop_neural_kernel()
        
    except Exception as e:
        print(f"❌ 長時間実行テストエラー: {e}")
        try:
            await kernel.stop_neural_kernel()
        except:
            pass

async def main():
    """メインテスト実行"""
    print("🧠 Neural Kernel システムテストスイート")
    print("=" * 60)
    
    try:
        # 基本機能テスト
        await test_neural_kernel_basic()
        
        # ヘルス監視テスト
        await test_health_monitoring()
        
        # リソース監視テスト
        await test_resource_monitoring()
        
        # 緊急対応テスト
        await test_emergency_handler()
        
        # 長時間実行テスト
        await test_long_running()
        
        print("\n" + "=" * 60)
        print("🎉 Neural Kernel全テスト完了")
        print("=" * 60)
        
    except KeyboardInterrupt:
        print("\n⏸️ テストが中断されました")
    except Exception as e:
        print(f"\n❌ テストスイートエラー: {e}")

if __name__ == "__main__":
    asyncio.run(main())