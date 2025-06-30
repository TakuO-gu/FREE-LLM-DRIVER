"""
簡易リフレクター
実行結果の評価と改善提案を軽量で実現
"""

import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum

from .executor import ExecutionResult, ExecutionStatus
from ..llm.provider_manager import LLMProviderManager

class ReflectionType(Enum):
    """振り返りタイプ"""
    SUCCESS_ANALYSIS = "success"
    FAILURE_ANALYSIS = "failure"
    PERFORMANCE_REVIEW = "performance"
    IMPROVEMENT_SUGGESTION = "improvement"

@dataclass
class Reflection:
    """振り返り結果"""
    reflection_type: ReflectionType
    summary: str
    insights: List[str]
    recommendations: List[str]
    confidence_score: float = 0.0

class SimpleReflector:
    """簡易リフレクター"""
    
    def __init__(self, llm_manager: LLMProviderManager):
        self.llm_manager = llm_manager
        
        # 軽量プロンプトテンプレート
        self.reflection_templates = {
            ReflectionType.SUCCESS_ANALYSIS: """
Task completed successfully: {task_description}
Output: {output}

What made this successful? (2-3 key points)
""",
            ReflectionType.FAILURE_ANALYSIS: """
Task failed: {task_description}
Error: {error}

What went wrong and how to fix it? (brief analysis)
""",
            ReflectionType.PERFORMANCE_REVIEW: """
Performance summary:
- Completed: {completed}/{total} tasks
- Average time: {avg_time}s
- Success rate: {success_rate}%

Key insights and improvement areas?
""",
            ReflectionType.IMPROVEMENT_SUGGESTION: """
Goal: {goal}
Results: {results_summary}

Quick improvement suggestions for next time?
"""
        }
    
    async def reflect_on_execution(
        self, 
        results: List[ExecutionResult], 
        goal: str = ""
    ) -> List[Reflection]:
        """実行結果の振り返り"""
        
        reflections = []
        
        try:
            # 成功した結果の分析（最も成功したもの1つ）
            successful_results = [r for r in results if r.status == ExecutionStatus.COMPLETED]
            if successful_results:
                best_result = max(successful_results, key=lambda r: len(r.output))
                success_reflection = await self._analyze_success(best_result)
                if success_reflection:
                    reflections.append(success_reflection)
            
            # 失敗した結果の分析（最初の失敗のみ）
            failed_results = [r for r in results if r.status == ExecutionStatus.FAILED]
            if failed_results:
                failure_reflection = await self._analyze_failure(failed_results[0])
                if failure_reflection:
                    reflections.append(failure_reflection)
            
            # 全体的なパフォーマンス分析
            if len(results) > 1:
                performance_reflection = await self._analyze_performance(results)
                if performance_reflection:
                    reflections.append(performance_reflection)
            
            # 改善提案（結果が不十分な場合のみ）
            success_rate = len(successful_results) / len(results) if results else 0
            if success_rate < 0.8 and goal:  # 成功率80%未満の場合
                improvement_reflection = await self._suggest_improvements(results, goal)
                if improvement_reflection:
                    reflections.append(improvement_reflection)
            
            logging.info(f"✅ {len(reflections)}件の振り返りを生成")
            return reflections
            
        except Exception as e:
            logging.error(f"❌ 振り返り生成エラー: {e}")
            return []
    
    async def _analyze_success(self, result: ExecutionResult) -> Optional[Reflection]:
        """成功分析"""
        
        if not result.output or len(result.output) < 10:
            return None
        
        # 軽量プロンプトで分析
        prompt = self.reflection_templates[ReflectionType.SUCCESS_ANALYSIS].format(
            task_description=result.task_id,
            output=result.output[:200]  # 最初の200文字のみ
        )
        
        try:
            response = await self.llm_manager.get_completion(
                prompt, 
                task_type="simple_task"
            )
            
            insights = self._extract_insights(response)
            
            return Reflection(
                reflection_type=ReflectionType.SUCCESS_ANALYSIS,
                summary="成功要因の分析",
                insights=insights,
                recommendations=[],
                confidence_score=0.8
            )
            
        except Exception as e:
            logging.error(f"❌ 成功分析エラー: {e}")
            return None
    
    async def _analyze_failure(self, result: ExecutionResult) -> Optional[Reflection]:
        """失敗分析"""
        
        if not result.error:
            return None
        
        prompt = self.reflection_templates[ReflectionType.FAILURE_ANALYSIS].format(
            task_description=result.task_id,
            error=result.error[:200]  # エラーメッセージの最初の200文字
        )
        
        try:
            response = await self.llm_manager.get_completion(
                prompt,
                task_type="simple_task"
            )
            
            recommendations = self._extract_recommendations(response)
            
            return Reflection(
                reflection_type=ReflectionType.FAILURE_ANALYSIS,
                summary="失敗原因の分析",
                insights=[result.error],
                recommendations=recommendations,
                confidence_score=0.7
            )
            
        except Exception as e:
            logging.error(f"❌ 失敗分析エラー: {e}")
            return None
    
    async def _analyze_performance(self, results: List[ExecutionResult]) -> Optional[Reflection]:
        """パフォーマンス分析"""
        
        if not results:
            return None
        
        # 統計計算
        total = len(results)
        completed = sum(1 for r in results if r.status == ExecutionStatus.COMPLETED)
        avg_time = sum(r.execution_time for r in results) / total
        success_rate = (completed / total * 100)
        
        prompt = self.reflection_templates[ReflectionType.PERFORMANCE_REVIEW].format(
            completed=completed,
            total=total,
            avg_time=round(avg_time, 1),
            success_rate=round(success_rate, 1)
        )
        
        try:
            response = await self.llm_manager.get_completion(
                prompt,
                task_type="simple_task"
            )
            
            insights = self._extract_insights(response)
            
            return Reflection(
                reflection_type=ReflectionType.PERFORMANCE_REVIEW,
                summary=f"パフォーマンス分析 (成功率: {success_rate:.1f}%)",
                insights=insights,
                recommendations=[],
                confidence_score=0.9
            )
            
        except Exception as e:
            logging.error(f"❌ パフォーマンス分析エラー: {e}")
            return None
    
    async def _suggest_improvements(self, results: List[ExecutionResult], goal: str) -> Optional[Reflection]:
        """改善提案"""
        
        # 結果サマリーの作成
        completed = sum(1 for r in results if r.status == ExecutionStatus.COMPLETED)
        failed = sum(1 for r in results if r.status == ExecutionStatus.FAILED)
        
        results_summary = f"{completed}件成功, {failed}件失敗"
        
        prompt = self.reflection_templates[ReflectionType.IMPROVEMENT_SUGGESTION].format(
            goal=goal[:100],  # 目標の最初の100文字
            results_summary=results_summary
        )
        
        try:
            response = await self.llm_manager.get_completion(
                prompt,
                task_type="simple_task"
            )
            
            recommendations = self._extract_recommendations(response)
            
            return Reflection(
                reflection_type=ReflectionType.IMPROVEMENT_SUGGESTION,
                summary="改善提案",
                insights=[],
                recommendations=recommendations,
                confidence_score=0.6
            )
            
        except Exception as e:
            logging.error(f"❌ 改善提案エラー: {e}")
            return None
    
    def _extract_insights(self, response: str) -> List[str]:
        """インサイトの抽出"""
        lines = [line.strip() for line in response.split('\n') if line.strip()]
        
        # 箇条書きや番号付きリストを探す
        insights = []
        for line in lines:
            if (line.startswith('-') or 
                line.startswith('•') or 
                line.startswith('*') or
                any(line.startswith(str(i)+'.') for i in range(1, 10))):
                insights.append(line[1:].strip() if line[0] in '-•*' else line[2:].strip())
        
        # 箇条書きが見つからない場合は文を分割
        if not insights and len(lines) > 0:
            insights = lines[:3]  # 最初の3行
        
        return insights[:3]  # 最大3つのインサイト
    
    def _extract_recommendations(self, response: str) -> List[str]:
        """推奨事項の抽出"""
        return self._extract_insights(response)  # 同じロジックを使用
    
    def create_quick_reflection(self, success: bool, summary: str) -> Reflection:
        """クイック振り返りの作成"""
        
        if success:
            return Reflection(
                reflection_type=ReflectionType.SUCCESS_ANALYSIS,
                summary="タスク成功",
                insights=[summary],
                recommendations=[],
                confidence_score=1.0
            )
        else:
            return Reflection(
                reflection_type=ReflectionType.FAILURE_ANALYSIS,
                summary="タスク失敗",
                insights=[summary],
                recommendations=["エラーログを確認", "別のアプローチを試行"],
                confidence_score=0.8
            )
    
    def format_reflections(self, reflections: List[Reflection]) -> str:
        """振り返り結果のフォーマット"""
        
        if not reflections:
            return "振り返り結果はありません。"
        
        formatted = "## 振り返り結果\n\n"
        
        for i, reflection in enumerate(reflections, 1):
            formatted += f"### {i}. {reflection.summary}\n"
            
            if reflection.insights:
                formatted += "**インサイト:**\n"
                for insight in reflection.insights:
                    formatted += f"- {insight}\n"
            
            if reflection.recommendations:
                formatted += "**推奨事項:**\n"
                for rec in reflection.recommendations:
                    formatted += f"- {rec}\n"
            
            formatted += "\n"
        
        return formatted