"""
ローカル実行エンジン
タスクの実際の実行とローカル操作を管理
"""

import asyncio
import logging
import os
import subprocess
import sys
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass
from enum import Enum

from .task_planner import Task, TaskType, TaskPriority
from ..llm.provider_manager import LLMProviderManager
from ..tools.web_tools import WebSearcher

class ExecutionStatus(Enum):
    """実行状態"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"

@dataclass
class ExecutionResult:
    """実行結果"""
    task_id: str
    status: ExecutionStatus
    output: str = ""
    error: str = ""
    execution_time: float = 0.0
    tokens_used: int = 0
    provider_used: str = ""

class LocalExecutor:
    """ローカル実行エンジン"""
    
    def __init__(self, llm_manager: LLMProviderManager, safe_mode: bool = True):
        self.llm_manager = llm_manager
        self.safe_mode = safe_mode
        self.execution_history: List[ExecutionResult] = []
        self.web_searcher = WebSearcher(safe_mode=safe_mode)
        
        # 安全なコマンド許可リスト
        self.safe_commands = {
            'ls', 'cat', 'head', 'tail', 'pwd', 'echo', 'date',
            'python', 'python3', 'node', 'npm', 'pip', 'pip3',
            'git', 'curl', 'wget', 'grep', 'find', 'wc', 'sort'
        }
        
        # 危険なコマンド拒否リスト
        self.dangerous_commands = {
            'rm', 'rmdir', 'del', 'format', 'fdisk', 'dd',
            'sudo', 'su', 'chmod', 'chown', 'kill', 'killall'
        }
    
    async def execute_task(self, task: Task, context: Dict[str, Any] = None) -> ExecutionResult:
        """タスクの実行"""
        if context is None:
            context = {}
        
        start_time = asyncio.get_event_loop().time()
        
        try:
            logging.info(f"🚀 タスク実行開始: {task.id} - {task.description}")
            
            # タスクタイプに基づく実行方法選択
            if task.task_type == TaskType.CODE:
                result = await self._execute_code_task(task, context)
            elif task.task_type == TaskType.ANALYSIS:
                result = await self._execute_analysis_task(task, context)
            elif task.task_type == TaskType.QUESTION_ANSWER:
                result = await self._execute_qa_task(task, context)
            elif task.task_type == TaskType.WEB_SEARCH:
                result = await self._execute_web_search_task(task, context)
            else:
                result = await self._execute_general_task(task, context)
            
            # 実行時間の記録
            result.execution_time = asyncio.get_event_loop().time() - start_time
            
            # 実行履歴に追加
            self.execution_history.append(result)
            
            logging.info(f"✅ タスク実行完了: {task.id} ({result.execution_time:.2f}s)")
            return result
            
        except Exception as e:
            error_result = ExecutionResult(
                task_id=task.id,
                status=ExecutionStatus.FAILED,
                error=str(e),
                execution_time=asyncio.get_event_loop().time() - start_time
            )
            
            self.execution_history.append(error_result)
            logging.error(f"❌ タスク実行失敗: {task.id} - {e}")
            return error_result
    
    async def _execute_code_task(self, task: Task, context: Dict[str, Any]) -> ExecutionResult:
        """コードタスクの実行"""
        
        # コード生成プロンプトの作成
        prompt = f"""
        Task: {task.description}
        
        Generate executable code for this task.
        Include comments and error handling.
        Format: ```language
        [code here]
        ```
        """
        
        try:
            # LLMでコード生成
            response = await self.llm_manager.get_completion(
                prompt, 
                task_type="code_generation"
            )
            
            # コード抽出
            code = self._extract_code_from_response(response)
            
            if not code:
                return ExecutionResult(
                    task_id=task.id,
                    status=ExecutionStatus.FAILED,
                    error="コードの抽出に失敗しました",
                    output=response
                )
            
            # コード実行（安全モードでは制限あり）
            if self.safe_mode:
                # 安全性チェック
                if not self._is_code_safe(code):
                    return ExecutionResult(
                        task_id=task.id,
                        status=ExecutionStatus.FAILED,
                        error="安全でないコードが検出されました",
                        output=code
                    )
            
            # 実行結果
            execution_output = await self._execute_code_safely(code)
            
            return ExecutionResult(
                task_id=task.id,
                status=ExecutionStatus.COMPLETED,
                output=execution_output,
                provider_used=self.llm_manager.provider_priority[0]  # 使用したプロバイダー
            )
            
        except Exception as e:
            return ExecutionResult(
                task_id=task.id,
                status=ExecutionStatus.FAILED,
                error=str(e)
            )
    
    async def _execute_analysis_task(self, task: Task, context: Dict[str, Any]) -> ExecutionResult:
        """分析タスクの実行"""
        
        prompt = f"""
        Analyze: {task.description}
        
        Provide a structured analysis with:
        1. Key findings
        2. Important insights
        3. Recommendations
        
        Keep it concise and actionable.
        """
        
        try:
            response = await self.llm_manager.get_completion(
                prompt,
                task_type="complex_reasoning"
            )
            
            return ExecutionResult(
                task_id=task.id,
                status=ExecutionStatus.COMPLETED,
                output=response,
                provider_used="analysis"
            )
            
        except Exception as e:
            return ExecutionResult(
                task_id=task.id,
                status=ExecutionStatus.FAILED,
                error=str(e)
            )
    
    async def _execute_web_search_task(self, task: Task, context: Dict[str, Any]) -> ExecutionResult:
        """Web検索タスクの実行"""
        
        try:
            # 検索キーワードの抽出
            search_query = task.description
            
            # Web検索とLLM要約を実行
            search_result = self.web_searcher.search_and_summarize(search_query, self.llm_manager)
            
            return ExecutionResult(
                task_id=task.id,
                status=ExecutionStatus.COMPLETED,
                output=search_result,
                provider_used="web_search"
            )
            
        except Exception as e:
            return ExecutionResult(
                task_id=task.id,
                status=ExecutionStatus.FAILED,
                error=str(e)
            )
    
    async def _execute_qa_task(self, task: Task, context: Dict[str, Any]) -> ExecutionResult:
        """質問応答タスクの実行"""
        
        # シンプルなQAプロンプト
        prompt = f"Question: {task.description}\n\nProvide a clear, concise answer:"
        
        try:
            response = await self.llm_manager.get_completion(
                prompt,
                task_type="simple_task"
            )
            
            return ExecutionResult(
                task_id=task.id,
                status=ExecutionStatus.COMPLETED,
                output=response,
                provider_used="qa"
            )
            
        except Exception as e:
            return ExecutionResult(
                task_id=task.id,
                status=ExecutionStatus.FAILED,
                error=str(e)
            )
    
    async def _execute_general_task(self, task: Task, context: Dict[str, Any]) -> ExecutionResult:
        """一般タスクの実行"""
        
        prompt = f"Task: {task.description}\n\nExecute this task step by step:"
        
        try:
            response = await self.llm_manager.get_completion(
                prompt,
                task_type="general"
            )
            
            return ExecutionResult(
                task_id=task.id,
                status=ExecutionStatus.COMPLETED,
                output=response,
                provider_used="general"
            )
            
        except Exception as e:
            return ExecutionResult(
                task_id=task.id,
                status=ExecutionStatus.FAILED,
                error=str(e)
            )
    
    def _extract_code_from_response(self, response: str) -> Optional[str]:
        """レスポンスからコードを抽出"""
        import re
        
        # コードブロックの抽出
        code_pattern = r'```(?:python|javascript|bash|sh|sql)?\n(.*?)```'
        matches = re.findall(code_pattern, response, re.DOTALL)
        
        if matches:
            return matches[0].strip()
        
        # コードブロックがない場合、全体を返す
        lines = response.split('\n')
        code_lines = [line for line in lines if line.strip() and not line.startswith('#')]
        
        if code_lines:
            return '\n'.join(code_lines)
        
        return None
    
    def _is_code_safe(self, code: str) -> bool:
        """コードの安全性チェック"""
        if not self.safe_mode:
            return True
        
        code_lower = code.lower()
        
        # 危険なコマンドのチェック
        for dangerous_cmd in self.dangerous_commands:
            if dangerous_cmd in code_lower:
                logging.warning(f"⚠️ 危険なコマンド検出: {dangerous_cmd}")
                return False
        
        # ファイル操作の制限チェック
        dangerous_patterns = [
            r'os\.system\s*\(',
            r'subprocess\..*\(',
            r'exec\s*\(',
            r'eval\s*\(',
            r'__import__\s*\(',
            r'open\s*\(.*["\']w["\']',  # 書き込みモードでのファイルオープン
        ]
        
        for pattern in dangerous_patterns:
            if re.search(pattern, code_lower):
                logging.warning(f"⚠️ 危険なパターン検出: {pattern}")
                return False
        
        return True
    
    async def _execute_code_safely(self, code: str) -> str:
        """安全なコード実行"""
        
        # Python コードの場合
        if 'print(' in code or 'import ' in code or 'def ' in code:
            return await self._execute_python_code(code)
        
        # シェルコマンドの場合
        if any(cmd in code for cmd in self.safe_commands):
            return await self._execute_shell_command(code)
        
        # その他の場合は文字列として返す
        return f"Code generated:\n{code}"
    
    async def _execute_python_code(self, code: str) -> str:
        """Pythonコードの実行"""
        try:
            # 安全なPython実行環境
            safe_globals = {
                '__builtins__': {
                    'print': print,
                    'len': len,
                    'str': str,
                    'int': int,
                    'float': float,
                    'list': list,
                    'dict': dict,
                    'range': range,
                    'enumerate': enumerate,
                    'zip': zip,
                }
            }
            
            # 出力をキャプチャ
            import io
            import sys
            old_stdout = sys.stdout
            sys.stdout = captured_output = io.StringIO()
            
            try:
                exec(code, safe_globals)
                output = captured_output.getvalue()
            finally:
                sys.stdout = old_stdout
            
            return output if output else "Code executed successfully (no output)"
            
        except Exception as e:
            return f"Python execution error: {e}"
    
    async def _execute_shell_command(self, command: str) -> str:
        """シェルコマンドの実行"""
        try:
            # 安全なコマンドのみ実行
            cmd_parts = command.split()
            if not cmd_parts or cmd_parts[0] not in self.safe_commands:
                return f"Command not allowed: {command}"
            
            # 実行
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30  # 30秒タイムアウト
            )
            
            if result.returncode == 0:
                return result.stdout
            else:
                return f"Command failed: {result.stderr}"
                
        except subprocess.TimeoutExpired:
            return "Command timeout"
        except Exception as e:
            return f"Shell execution error: {e}"
    
    def get_execution_stats(self) -> Dict[str, Any]:
        """実行統計の取得"""
        if not self.execution_history:
            return {'total_executions': 0}
        
        total = len(self.execution_history)
        completed = sum(1 for r in self.execution_history if r.status == ExecutionStatus.COMPLETED)
        failed = sum(1 for r in self.execution_history if r.status == ExecutionStatus.FAILED)
        
        avg_time = sum(r.execution_time for r in self.execution_history) / total
        
        return {
            'total_executions': total,
            'completed': completed,
            'failed': failed,
            'success_rate': (completed / total * 100) if total > 0 else 0,
            'average_execution_time': round(avg_time, 2),
            'safe_mode': self.safe_mode
        }
    
    def clear_history(self):
        """実行履歴のクリア"""
        self.execution_history.clear()
        logging.info("🗑️ 実行履歴をクリア")