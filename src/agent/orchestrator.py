"""
軽量オーケストレーション
タスクの統合管理と効率的なワークフロー実行
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta

from .task_planner import EfficientTaskPlanner, Task, TaskType, TaskPriority
from .executor import LocalExecutor, ExecutionResult, ExecutionStatus
from .reflector import SimpleReflector
from ..llm.provider_manager import LLMProviderManager

@dataclass
class WorkflowResult:
    """ワークフロー実行結果"""
    goal: str
    total_tasks: int
    completed_tasks: int
    failed_tasks: int
    total_time: float
    results: List[ExecutionResult]
    summary: str = ""
    success: bool = False

class LightweightOrchestrator:
    """軽量オーケストレーター"""
    
    def __init__(self, llm_manager: LLMProviderManager, config: Dict[str, Any] = None):
        self.llm_manager = llm_manager
        self.config = config or {}
        
        # コンポーネントの初期化
        self.task_planner = EfficientTaskPlanner(llm_manager)
        self.executor = LocalExecutor(llm_manager, safe_mode=self.config.get('safe_mode', True))
        self.reflector = SimpleReflector(llm_manager)
        
        # 実行設定
        self.max_concurrent_tasks = self.config.get('max_concurrent_tasks', 2)
        self.max_retries = self.config.get('max_retries', 2)
        self.timeout_seconds = self.config.get('timeout_seconds', 300)  # 5分
        
        # 統計情報
        self.workflow_history: List[WorkflowResult] = []
    
    async def execute_goal(self, goal: str, context: Dict[str, Any] = None) -> WorkflowResult:
        """目標の実行"""
        if context is None:
            context = {}
        
        start_time = datetime.now()
        
        try:
            logging.info(f"🎯 目標実行開始: {goal}")
            
            # Step 1: タスク分割
            tasks = await self.task_planner.decompose_goal(goal)
            
            if not tasks:
                return WorkflowResult(
                    goal=goal,
                    total_tasks=0,
                    completed_tasks=0,
                    failed_tasks=0,
                    total_time=0.0,
                    results=[],
                    summary="タスクの分割に失敗しました",
                    success=False
                )
            
            # Step 2: タスク優先度付け
            prioritized_tasks = self.task_planner.prioritize_tasks(tasks)
            
            # Step 3: タスク実行
            results = await self._execute_tasks_batch(prioritized_tasks, context)
            
            # Step 4: 結果評価
            total_time = (datetime.now() - start_time).total_seconds()
            workflow_result = self._analyze_workflow_results(
                goal, prioritized_tasks, results, total_time
            )
            
            # Step 5: 簡易振り返り
            workflow_result.summary = await self._generate_summary(workflow_result)
            
            # 履歴に記録
            self.workflow_history.append(workflow_result)
            
            logging.info(f"✅ 目標実行完了: {goal} ({workflow_result.completed_tasks}/{workflow_result.total_tasks})")
            return workflow_result
            
        except Exception as e:
            logging.error(f"❌ 目標実行エラー: {goal} - {e}")
            
            error_result = WorkflowResult(
                goal=goal,
                total_tasks=0,
                completed_tasks=0,
                failed_tasks=1,
                total_time=(datetime.now() - start_time).total_seconds(),
                results=[],
                summary=f"実行エラー: {str(e)}",
                success=False
            )
            
            self.workflow_history.append(error_result)
            return error_result
    
    async def _execute_tasks_batch(self, tasks: List[Task], context: Dict[str, Any]) -> List[ExecutionResult]:
        """バッチタスク実行"""
        results = []
        
        # 依存関係のないタスクを先に実行
        independent_tasks = [t for t in tasks if not t.dependencies]
        dependent_tasks = [t for t in tasks if t.dependencies]
        
        # 独立タスクの並列実行
        if independent_tasks:
            batch_size = min(self.max_concurrent_tasks, len(independent_tasks))
            
            for i in range(0, len(independent_tasks), batch_size):
                batch = independent_tasks[i:i + batch_size]
                
                # 並列実行
                batch_results = await asyncio.gather(
                    *[self.executor.execute_task(task, context) for task in batch],
                    return_exceptions=True
                )
                
                # 結果の処理
                for result in batch_results:
                    if isinstance(result, Exception):
                        logging.error(f"❌ バッチ実行エラー: {result}")
                    else:
                        results.append(result)
        
        # 依存タスクの順次実行
        for task in dependent_tasks:
            # 依存チェック（簡易版）
            if self._check_dependencies(task, results):
                result = await self.executor.execute_task(task, context)
                results.append(result)
            else:
                # 依存が満たされない場合はスキップ
                skip_result = ExecutionResult(
                    task_id=task.id,
                    status=ExecutionStatus.SKIPPED,
                    error="依存関係が満たされていません"
                )
                results.append(skip_result)
        
        return results
    
    def _check_dependencies(self, task: Task, completed_results: List[ExecutionResult]) -> bool:
        """依存関係チェック（簡易版）"""
        if not task.dependencies:
            return True
        
        completed_task_ids = [r.task_id for r in completed_results if r.status == ExecutionStatus.COMPLETED]
        
        return all(dep in completed_task_ids for dep in task.dependencies)
    
    def _analyze_workflow_results(
        self, 
        goal: str, 
        tasks: List[Task], 
        results: List[ExecutionResult], 
        total_time: float
    ) -> WorkflowResult:
        """ワークフロー結果の分析"""
        
        completed = sum(1 for r in results if r.status == ExecutionStatus.COMPLETED)
        failed = sum(1 for r in results if r.status == ExecutionStatus.FAILED)
        
        success = completed > 0 and failed == 0
        
        return WorkflowResult(
            goal=goal,
            total_tasks=len(tasks),
            completed_tasks=completed,
            failed_tasks=failed,
            total_time=total_time,
            results=results,
            success=success
        )
    
    async def _generate_summary(self, workflow_result: WorkflowResult) -> str:
        """ワークフロー結果のサマリー生成"""
        
        if workflow_result.success:
            summary = f"✅ 目標「{workflow_result.goal}」を正常に完了しました。"
        else:
            summary = f"⚠️ 目標「{workflow_result.goal}」の実行で問題が発生しました。"
        
        summary += f"\n- 完了タスク: {workflow_result.completed_tasks}/{workflow_result.total_tasks}"
        summary += f"\n- 実行時間: {workflow_result.total_time:.1f}秒"
        
        if workflow_result.failed_tasks > 0:
            summary += f"\n- 失敗タスク: {workflow_result.failed_tasks}個"
        
        return summary
    
    async def execute_simple_task(self, description: str, task_type: str = "general") -> str:
        """シンプルなタスクの直接実行"""
        
        try:
            response = await self.llm_manager.get_completion(
                description,
                task_type=task_type
            )
            
            logging.info(f"✅ シンプルタスク完了: {description[:50]}...")
            return response
            
        except Exception as e:
            logging.error(f"❌ シンプルタスクエラー: {e}")
            return f"エラーが発生しました: {str(e)}"
    
    async def batch_execute_simple_tasks(self, tasks: List[str], task_type: str = "general") -> List[str]:
        """シンプルタスクのバッチ実行"""
        
        results = []
        batch_size = min(self.max_concurrent_tasks, len(tasks))
        
        for i in range(0, len(tasks), batch_size):
            batch = tasks[i:i + batch_size]
            
            batch_results = await asyncio.gather(
                *[self.execute_simple_task(task, task_type) for task in batch],
                return_exceptions=True
            )
            
            for result in batch_results:
                if isinstance(result, Exception):
                    results.append(f"エラー: {str(result)}")
                else:
                    results.append(result)
        
        return results
    
    def get_orchestrator_stats(self) -> Dict[str, Any]:
        """オーケストレーター統計情報"""
        
        if not self.workflow_history:
            return {
                'total_workflows': 0,
                'success_rate': 0,
                'average_execution_time': 0,
                'average_tasks_per_workflow': 0
            }
        
        total_workflows = len(self.workflow_history)
        successful_workflows = sum(1 for w in self.workflow_history if w.success)
        
        avg_time = sum(w.total_time for w in self.workflow_history) / total_workflows
        avg_tasks = sum(w.total_tasks for w in self.workflow_history) / total_workflows
        
        return {
            'total_workflows': total_workflows,
            'successful_workflows': successful_workflows,
            'success_rate': (successful_workflows / total_workflows * 100) if total_workflows > 0 else 0,
            'average_execution_time': round(avg_time, 2),
            'average_tasks_per_workflow': round(avg_tasks, 1),
            'task_planner_stats': self.task_planner.get_planner_stats(),
            'executor_stats': self.executor.get_execution_stats()
        }
    
    def get_recent_workflows(self, limit: int = 5) -> List[WorkflowResult]:
        """最近のワークフロー履歴取得"""
        return self.workflow_history[-limit:]
    
    def clear_history(self):
        """履歴のクリア"""
        self.workflow_history.clear()
        self.executor.clear_history()
        logging.info("🗑️ オーケストレーター履歴をクリア")
    
    def optimize_orchestrator(self):
        """オーケストレーターの最適化"""
        self.task_planner.optimize_planner()
        logging.info("🔧 オーケストレーターを最適化")