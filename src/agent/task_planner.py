"""
軽量化タスクプランナー
効率的なタスク分割とAPI使用量削減を実現
"""

import hashlib
import logging
import re
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum

from ..llm.provider_manager import LLMProviderManager
from ..utils.cache_manager import ResponseCache

class TaskType(Enum):
    """タスクタイプの定義"""
    SIMPLE = "simple"
    COMPLEX = "complex"
    CODE = "code"
    ANALYSIS = "analysis"
    CREATIVE = "creative"
    QUESTION_ANSWER = "qa"
    WEB_SEARCH = "web_search"

class TaskPriority(Enum):
    """タスク優先度"""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4

@dataclass
class Task:
    """タスク情報"""
    id: str
    description: str
    task_type: TaskType
    priority: TaskPriority
    dependencies: List[str] = None
    estimated_tokens: int = 0
    context: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []
        if self.context is None:
            self.context = {}

class EfficientTaskPlanner:
    """効率的なタスクプランナー"""
    
    def __init__(self, llm_manager: LLMProviderManager):
        self.llm_manager = llm_manager
        self.cache = ResponseCache(max_size=500, ttl_hours=12)
        
        # シンプルなプロンプトテンプレート（トークン節約）
        self.decomposition_template = """Goal: {goal}

Break into 3-5 executable tasks:
Task1: [description] | Task2: [description] | Task3: [description]

Focus on concrete, actionable steps."""
        
        # パターンマッチング用の正規表現
        self.task_pattern = re.compile(r'Task\d+:\s*([^|]+)')
        
    def _classify_goal_type(self, goal: str) -> TaskType:
        """目標の種類を分類"""
        goal_lower = goal.lower()
        
        # Web検索キーワードの検出
        search_keywords = [
            '検索', 'search', '調べる', '情報', '最新', 'ニュース', '天気', 
            'について教えて', 'とは', '価格', '料金', '株価', '為替',
            'インターネット', 'ウェブ', 'web', '公式', 'サイト'
        ]
        if any(keyword in goal_lower for keyword in search_keywords):
            return TaskType.WEB_SEARCH
        elif any(keyword in goal_lower for keyword in ['code', 'program', 'script', 'function', 'class']):
            return TaskType.CODE
        elif any(keyword in goal_lower for keyword in ['analyze', 'analysis', 'study', 'research']):
            return TaskType.ANALYSIS
        elif any(keyword in goal_lower for keyword in ['create', 'write', 'design', 'generate']):
            return TaskType.CREATIVE
        elif any(keyword in goal_lower for keyword in ['what', 'how', 'why', 'when', 'where', '?']):
            return TaskType.QUESTION_ANSWER
        elif len(goal.split()) > 20:
            return TaskType.COMPLEX
        else:
            return TaskType.SIMPLE
    
    def _estimate_complexity(self, goal: str) -> int:
        """目標の複雑さを推定（1-5のスケール）"""
        factors = 0
        goal_lower = goal.lower()
        
        # 長さベースの複雑さ
        if len(goal.split()) > 30:
            factors += 2
        elif len(goal.split()) > 15:
            factors += 1
        
        # キーワードベースの複雑さ
        complex_keywords = ['multiple', 'various', 'complex', 'advanced', 'comprehensive', 'detailed']
        factors += sum(1 for keyword in complex_keywords if keyword in goal_lower)
        
        # 技術的複雑さ
        tech_keywords = ['algorithm', 'optimization', 'machine learning', 'database', 'api', 'integration']
        factors += sum(1 for keyword in tech_keywords if keyword in goal_lower)
        
        return min(5, max(1, factors))
    
    def _generate_task_id(self, description: str) -> str:
        """タスクIDの生成"""
        return hashlib.md5(description.encode('utf-8')).hexdigest()[:8]
    
    async def decompose_goal(self, goal: str, max_tasks: int = 5) -> List[Task]:
        """目標の効率的分割"""
        
        # キャッシュチェック
        cache_key = f"decompose_{hashlib.md5(goal.encode()).hexdigest()}"
        cached_result = self.cache.get_cached_response(cache_key)
        
        if cached_result:
            logging.info("💰 タスク分割結果をキャッシュから取得")
            return self._parse_cached_tasks(cached_result, goal)
        
        # 目標の分析
        goal_type = self._classify_goal_type(goal)
        complexity = self._estimate_complexity(goal)
        
        # 複雑さに基づくタスク数調整
        if complexity <= 2:
            target_tasks = min(3, max_tasks)
        elif complexity <= 3:
            target_tasks = min(4, max_tasks)
        else:
            target_tasks = max_tasks
        
        # 軽量プロンプトの作成
        prompt = self.decomposition_template.format(goal=goal)
        
        try:
            # LLM実行（シンプルタスクとして実行してAPI使用量を削減）
            response = await self.llm_manager.get_completion(
                prompt, 
                task_type="simple_task"
            )
            
            # キャッシュ保存
            self.cache.cache_response(cache_key, response)
            
            # タスク解析
            tasks = self._parse_llm_response(response, goal, goal_type)
            
            logging.info(f"✅ 目標を{len(tasks)}個のタスクに分割")
            return tasks[:target_tasks]  # 最大タスク数制限
            
        except Exception as e:
            logging.error(f"❌ タスク分割エラー: {e}")
            # フォールバック: シンプルなルールベース分割
            return self._fallback_decomposition(goal, goal_type)
    
    def _parse_llm_response(self, response: str, original_goal: str, goal_type: TaskType) -> List[Task]:
        """LLMレスポンスの解析"""
        tasks = []
        
        # 正規表現でタスクを抽出
        matches = self.task_pattern.findall(response)
        
        if not matches:
            # パターンマッチしない場合は行分割で試行
            lines = [line.strip() for line in response.split('\n') if line.strip()]
            matches = [line for line in lines if any(char.isdigit() for char in line[:5])]
            
            # それでもマッチしない場合は、より柔軟な解析
            if not matches:
                logging.warning("⚠️ 標準パターンでタスク抽出失敗、フォールバック実行")
                # 文を分割してタスクとして扱う
                sentences = [s.strip() for s in response.split('.') if len(s.strip()) > 10]
                matches = sentences[:3]  # 最大3つ
        
        for i, match in enumerate(matches):
            description = match.strip()
            if not description or len(description) < 10:
                continue
            
            # タスクオブジェクト作成
            task = Task(
                id=self._generate_task_id(description),
                description=description,
                task_type=goal_type,
                priority=TaskPriority.MEDIUM,
                estimated_tokens=len(description.split()) * 2,  # 簡易推定
                context={'original_goal': original_goal, 'task_index': i}
            )
            
            tasks.append(task)
        
        # タスクが空の場合はフォールバック
        if not tasks:
            logging.warning("⚠️ LLMレスポンス解析でタスクが0件、フォールバック実行")
            return self._fallback_decomposition(original_goal, goal_type)
        
        return tasks
    
    def _parse_cached_tasks(self, cached_response: str, original_goal: str) -> List[Task]:
        """キャッシュされたタスクの解析"""
        # キャッシュからの復元時は簡略化
        return self._parse_llm_response(cached_response, original_goal, TaskType.SIMPLE)
    
    def _fallback_decomposition(self, goal: str, goal_type: TaskType) -> List[Task]:
        """フォールバック：ルールベースタスク分割"""
        logging.info("🔄 ルールベースタスク分割を実行")
        
        # シンプルなルールベース分割
        if goal_type == TaskType.CODE:
            tasks_desc = [
                "要件を分析し設計を決定",
                "コードの骨格を作成", 
                "機能を実装",
                "テストとデバッグを実行"
            ]
        elif goal_type == TaskType.ANALYSIS:
            tasks_desc = [
                "データや情報を収集",
                "主要なポイントを分析",
                "結論をまとめて報告"
            ]
        else:
            # 汎用的な分割
            sentences = goal.split('.')
            if len(sentences) > 1:
                tasks_desc = [s.strip() for s in sentences if s.strip()][:4]
            else:
                tasks_desc = [
                    f"{goal}の準備段階",
                    f"{goal}の実行",
                    f"{goal}の確認と完了"
                ]
        
        tasks = []
        for i, desc in enumerate(tasks_desc):
            task = Task(
                id=self._generate_task_id(desc),
                description=desc,
                task_type=goal_type,
                priority=TaskPriority.MEDIUM,
                context={'original_goal': goal, 'fallback': True, 'task_index': i}
            )
            tasks.append(task)
        
        return tasks
    
    def prioritize_tasks(self, tasks: List[Task], constraints: Dict[str, Any] = None) -> List[Task]:
        """タスクの優先度付け"""
        if constraints is None:
            constraints = {}
        
        # 簡易優先度算出
        for task in tasks:
            priority_score = 0
            
            # タスクタイプによる優先度
            if task.task_type == TaskType.CODE:
                priority_score += 3
            elif task.task_type == TaskType.ANALYSIS:
                priority_score += 2
            else:
                priority_score += 1
            
            # 依存関係による優先度
            if not task.dependencies:
                priority_score += 1  # 依存のないタスクは優先
            
            # 推定コストによる調整
            if task.estimated_tokens < 100:
                priority_score += 1  # 軽いタスクは優先
            
            # 優先度設定
            if priority_score >= 5:
                task.priority = TaskPriority.CRITICAL
            elif priority_score >= 4:
                task.priority = TaskPriority.HIGH
            elif priority_score >= 3:
                task.priority = TaskPriority.MEDIUM
            else:
                task.priority = TaskPriority.LOW
        
        # 優先度でソート
        return sorted(tasks, key=lambda t: (t.priority.value, -t.estimated_tokens), reverse=True)
    
    def get_planner_stats(self) -> Dict[str, Any]:
        """プランナーの統計情報"""
        return {
            'cache_stats': self.cache.get_cache_stats(),
            'total_decompositions': self.cache.stats['saves'],
            'cache_hit_rate': self.cache.get_cache_stats()['hit_rate_percent']
        }
    
    def optimize_planner(self):
        """プランナーの最適化"""
        self.cache.optimize_cache()
        logging.info("🔧 タスクプランナーを最適化")