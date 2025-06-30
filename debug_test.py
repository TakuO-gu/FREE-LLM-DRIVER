#!/usr/bin/env python3
"""
Free LLM Driver デバッグテストスイート
ランダムに難易度の異なるタスクを実行してシステムの安定性をテスト
"""

import asyncio
import random
import subprocess
import sys
import time
from typing import List, Dict, Any
from pathlib import Path

class DebugTester:
    """デバッグテストクラス"""
    
    def __init__(self):
        self.test_results = []
        
        # 難易度別テストケース
        self.test_cases = {
            "easy": [
                "Hello Worldと表示",
                "今日の日付を教えて",
                "簡単な足し算をして",
                "天気について教えて",
                "Pythonとは何か説明して"
            ],
            "medium": [
                "Pythonでファイル一覧を表示するスクリプト作成",
                "CSVファイルの読み込み方法を調べる",
                "Dockerの基本的な使い方を検索",
                "機械学習について調べてまとめる",
                "Webスクレイピングの方法を調査"
            ],
            "hard": [
                "Pythonでデータベース接続とCRUD操作のサンプルコード作成",
                "ReactとNode.jsでWebアプリケーション開発手順を調査",
                "Kubernetesクラスター構築手順を詳細に調べる",
                "深層学習モデルの実装例とベストプラクティスを検索",
                "マイクロサービスアーキテクチャの設計パターンを調査分析"
            ],
            "expert": [
                "分散システムでのデータ整合性問題と解決策を調査してPythonで実装例作成",
                "高可用性Webシステムのアーキテクチャ設計と監視システム構築手順",
                "量子コンピューティングの基礎理論と実用例をPythonで実装",
                "ブロックチェーン技術の仕組みと暗号化アルゴリズムの実装例",
                "AIによる自然言語処理パイプラインの設計と最適化手法"
            ]
        }
    
    def run_single_test(self, task: str, difficulty: str) -> Dict[str, Any]:
        """単一テストの実行"""
        print(f"\n🧪 テスト実行: [{difficulty.upper()}] {task}")
        
        start_time = time.time()
        
        try:
            # Free LLM Driverでタスク実行
            cmd = ["python", "main.py", "--goal", task]
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120,  # 2分タイムアウト
                cwd=Path(__file__).parent
            )
            
            execution_time = time.time() - start_time
            
            # 結果解析
            success = result.returncode == 0
            output_lines = result.stdout.split('\n')
            
            # 成功判定（より詳細に）
            success_indicators = ['✅', '成功', 'completed', 'SUCCESS']
            error_indicators = ['❌', 'ERROR', 'Failed', 'エラー']
            
            has_success = any(indicator in result.stdout for indicator in success_indicators)
            has_error = any(indicator in result.stdout for indicator in error_indicators)
            
            # 実際の成功/失敗判定
            if has_success and not has_error:
                status = "SUCCESS"
            elif has_error:
                status = "ERROR"
            elif success:
                status = "PARTIAL"
            else:
                status = "FAILED"
            
            # 出力サイズ分析
            output_size = len(result.stdout)
            error_size = len(result.stderr)
            
            test_result = {
                'task': task,
                'difficulty': difficulty,
                'status': status,
                'execution_time': round(execution_time, 2),
                'return_code': result.returncode,
                'output_size': output_size,
                'error_size': error_size,
                'has_provider_init': '✅' in result.stdout and 'プロバイダー' in result.stdout,
                'has_task_completion': '完了タスク:' in result.stdout,
                'stdout_preview': result.stdout[:200] + '...' if len(result.stdout) > 200 else result.stdout,
                'stderr_preview': result.stderr[:200] + '...' if len(result.stderr) > 200 else result.stderr
            }
            
            print(f"   ⏱️  実行時間: {execution_time:.2f}秒")
            print(f"   📊 ステータス: {status}")
            print(f"   📏 出力サイズ: {output_size} 文字")
            
            return test_result
            
        except subprocess.TimeoutExpired:
            execution_time = time.time() - start_time
            print(f"   ⏰ タイムアウト: {execution_time:.2f}秒")
            
            return {
                'task': task,
                'difficulty': difficulty,
                'status': 'TIMEOUT',
                'execution_time': round(execution_time, 2),
                'return_code': -1,
                'output_size': 0,
                'error_size': 0,
                'has_provider_init': False,
                'has_task_completion': False,
                'stdout_preview': '',
                'stderr_preview': 'TIMEOUT'
            }
            
        except Exception as e:
            execution_time = time.time() - start_time
            print(f"   ❌ 例外発生: {str(e)}")
            
            return {
                'task': task,
                'difficulty': difficulty,
                'status': 'EXCEPTION',
                'execution_time': round(execution_time, 2),
                'return_code': -2,
                'output_size': 0,
                'error_size': 0,
                'has_provider_init': False,
                'has_task_completion': False,
                'stdout_preview': '',
                'stderr_preview': str(e)
            }
    
    def run_random_tests(self, num_tests: int = 10) -> List[Dict[str, Any]]:
        """ランダムテストの実行"""
        print(f"🚀 Free LLM Driver デバッグテスト開始 ({num_tests}件)")
        print("=" * 60)
        
        difficulties = list(self.test_cases.keys())
        
        for i in range(num_tests):
            print(f"\n📋 テスト {i+1}/{num_tests}")
            
            # ランダムに難易度とタスクを選択
            difficulty = random.choice(difficulties)
            task = random.choice(self.test_cases[difficulty])
            
            # テスト実行
            result = self.run_single_test(task, difficulty)
            self.test_results.append(result)
            
            # 短い休憩（システム負荷軽減）
            time.sleep(2)
        
        return self.test_results
    
    def analyze_results(self):
        """結果分析とレポート生成"""
        print("\n" + "="*60)
        print("📊 デバッグテスト結果分析")
        print("="*60)
        
        if not self.test_results:
            print("❌ テスト結果がありません")
            return
        
        # 基本統計
        total_tests = len(self.test_results)
        success_count = len([r for r in self.test_results if r['status'] == 'SUCCESS'])
        error_count = len([r for r in self.test_results if r['status'] in ['ERROR', 'FAILED']])
        timeout_count = len([r for r in self.test_results if r['status'] == 'TIMEOUT'])
        
        print(f"\n📈 基本統計:")
        print(f"   総テスト数: {total_tests}")
        print(f"   成功: {success_count} ({success_count/total_tests*100:.1f}%)")
        print(f"   エラー: {error_count} ({error_count/total_tests*100:.1f}%)")
        print(f"   タイムアウト: {timeout_count} ({timeout_count/total_tests*100:.1f}%)")
        
        # 難易度別分析
        print(f"\n📊 難易度別成功率:")
        for difficulty in ['easy', 'medium', 'hard', 'expert']:
            diff_results = [r for r in self.test_results if r['difficulty'] == difficulty]
            if diff_results:
                diff_success = len([r for r in diff_results if r['status'] == 'SUCCESS'])
                success_rate = diff_success / len(diff_results) * 100
                print(f"   {difficulty.upper()}: {diff_success}/{len(diff_results)} ({success_rate:.1f}%)")
        
        # パフォーマンス分析
        execution_times = [r['execution_time'] for r in self.test_results if r['execution_time'] > 0]
        if execution_times:
            avg_time = sum(execution_times) / len(execution_times)
            max_time = max(execution_times)
            min_time = min(execution_times)
            
            print(f"\n⏱️ パフォーマンス分析:")
            print(f"   平均実行時間: {avg_time:.2f}秒")
            print(f"   最大実行時間: {max_time:.2f}秒")
            print(f"   最小実行時間: {min_time:.2f}秒")
        
        # エラー分析
        print(f"\n🔍 エラー分析:")
        error_results = [r for r in self.test_results if r['status'] in ['ERROR', 'FAILED', 'EXCEPTION']]
        
        if error_results:
            print(f"   エラー詳細 ({len(error_results)}件):")
            for i, result in enumerate(error_results[:3], 1):  # 最初の3件のみ表示
                print(f"   {i}. [{result['difficulty']}] {result['task'][:50]}...")
                print(f"      ステータス: {result['status']}")
                print(f"      エラー: {result['stderr_preview'][:100]}...")
        else:
            print("   ✅ エラーなし")
        
        # 推奨事項
        print(f"\n💡 推奨事項:")
        if success_count / total_tests < 0.7:
            print("   - 成功率が70%未満です。システムの安定性向上が必要")
        if timeout_count > 0:
            print("   - タイムアウトが発生しています。パフォーマンス最適化を検討")
        if avg_time > 30:
            print("   - 平均実行時間が30秒を超えています。効率化が必要")
        
        if success_count / total_tests >= 0.8:
            print("   ✅ システムは良好に動作しています")

def main():
    """メイン実行"""
    tester = DebugTester()
    
    # ランダムテスト実行
    print("🧪 Free LLM Driver デバッグテストスイート")
    
    # テスト数を指定（デフォルト: 8件）
    num_tests = 8
    
    try:
        tester.run_random_tests(num_tests)
        tester.analyze_results()
        
    except KeyboardInterrupt:
        print("\n\n⏸️ テストが中断されました")
        if tester.test_results:
            print("部分的な結果を分析中...")
            tester.analyze_results()
    
    except Exception as e:
        print(f"\n❌ テスト実行エラー: {e}")

if __name__ == "__main__":
    main()