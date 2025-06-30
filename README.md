# 無料オンラインLLM + Open Interpreter 実装仕様書

## 1. プロジェクト概要

### 目的
無料のオンラインLLMサービスを活用した自己完結型タスク遂行AIエージェントシステムの構築

### アーキテクチャ概要
- **LLMバックエンド**: 無料オンラインAPI（Google Gemini、Groq、Together AI等）
- **エージェントフレームワーク**: Open Interpreter + カスタムオーケストレーター
- **実行モード**: ハイブリッド（推論はクラウド、実行はローカル）

## 2. 無料LLMサービス選択肢

### 2.1 推奨無料サービス
| サービス | モデル | 月間制限 | レスポンス速度 | 推奨用途 |
|---------|-------|---------|--------------|---------|
| **Google AI Studio** | Gemini 1.5 Flash | 1,500 req/day | 高速 | メイン推論 |
| **Groq** | Llama 3.1 70B | 14,400 req/day | 超高速 | コード生成 |
| **Together AI** | Llama 3.1 8B | 200 req/month | 中速 | バックアップ |
| **Hugging Face** | Code Llama | 1,000 req/day | 中速 | 特殊タスク |

### 2.2 フォールバック戦略
```python
# プロバイダー優先順位設定
PROVIDER_PRIORITY = [
    "google_gemini",     # メイン
    "groq_llama",        # 高速処理用
    "together_ai",       # バックアップ
    "huggingface"        # 最終手段
]
```

## 3. システム要件

### 3.1 ハードウェア要件（大幅軽量化）
- **最小構成**:
  - RAM: 4GB以上
  - ストレージ: 5GB以上
  - ネットワーク: 安定したインターネット接続
- **推奨構成**:
  - RAM: 8GB以上
  - ストレージ: 10GB以上
  - ネットワーク: 高速ブロードバンド

### 3.2 ソフトウェア要件
- **OS**: Windows 10+, macOS 10.14+, Ubuntu 18.04+
- **Python**: 3.8以上
- **必須パッケージ**: requests, asyncio, openai-compatible clients

## 4. 無料APIキー取得・設定

### 4.1 各サービスのセットアップ
```bash
# Google AI Studio
# https://makersuite.google.com/app/apikey でAPIキー取得

# Groq
# https://console.groq.com/keys でAPIキー取得

# Together AI
# https://api.together.xyz/settings/api-keys でAPIキー取得

# 環境変数設定
export GOOGLE_API_KEY="your_google_api_key"
export GROQ_API_KEY="your_groq_api_key"
export TOGETHER_API_KEY="your_together_api_key"
```

### 4.2 レート制限管理
```python
# config/rate_limits.yaml
rate_limits:
  google_gemini:
    requests_per_minute: 60
    requests_per_day: 1500
    
  groq_llama:
    requests_per_minute: 30
    requests_per_day: 14400
    
  together_ai:
    requests_per_minute: 10
    requests_per_month: 200
```

## 5. コンポーネント設計

### 5.1 軽量化されたコアコンポーネント
```
project_root/
├── src/
│   ├── agent/
│   │   ├── __init__.py
│   │   ├── task_planner.py      # タスク分割（軽量化）
│   │   ├── executor.py          # ローカル実行
│   │   ├── reflector.py         # 簡易評価
│   │   └── orchestrator.py      # 軽量オーケストレーション
│   ├── llm/
│   │   ├── __init__.py
│   │   ├── provider_manager.py  # マルチプロバイダー管理
│   │   ├── rate_limiter.py      # レート制限管理
│   │   └── fallback_handler.py  # フォールバック処理
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── local_executor.py    # ローカル実行のみ
│   │   └── web_tools.py         # 軽量Web操作
│   └── utils/
│       ├── __init__.py
│       ├── cache_manager.py     # レスポンスキャッシュ
│       └── quota_tracker.py     # 使用量追跡
├── config/
│   ├── providers.yaml           # プロバイダー設定
│   └── limits.yaml              # 制限設定
├── requirements.txt
└── main.py
```

## 6. LLMプロバイダー管理実装

### 6.1 マルチプロバイダー対応
```python
class LLMProviderManager:
    def __init__(self):
        self.providers = {
            'google_gemini': GoogleGeminiProvider(),
            'groq_llama': GroqProvider(),
            'together_ai': TogetherAIProvider(),
        }
        self.rate_limiter = RateLimiter()
        
    async def get_completion(self, prompt: str, task_type: str = "general") -> str:
        """最適なプロバイダーでLLM推論実行"""
        
        # タスクタイプ別の最適プロバイダー選択
        optimal_provider = self._select_provider(task_type)
        
        try:
            # レート制限チェック
            if self.rate_limiter.can_make_request(optimal_provider):
                return await self._make_request(optimal_provider, prompt)
            else:
                # フォールバック実行
                return await self._fallback_request(prompt, task_type)
                
        except Exception as e:
            return await self._handle_provider_error(e, prompt, task_type)
    
    def _select_provider(self, task_type: str) -> str:
        """タスクタイプに基づく最適プロバイダー選択"""
        provider_map = {
            "code_generation": "groq_llama",      # 高速コード生成
            "complex_reasoning": "google_gemini",  # 複雑な推論
            "simple_task": "together_ai",         # 簡単なタスク
            "general": "google_gemini"            # デフォルト
        }
        return provider_map.get(task_type, "google_gemini")
```

### 6.2 レート制限・キャッシュ管理
```python
class RateLimiter:
    def __init__(self):
        self.request_counts = defaultdict(lambda: defaultdict(int))
        self.last_reset = defaultdict(datetime.now)
        
    def can_make_request(self, provider: str) -> bool:
        """リクエスト可能性チェック"""
        limits = self._get_provider_limits(provider)
        current_count = self.request_counts[provider]
        
        # 日次制限チェック
        if current_count['daily'] >= limits['daily']:
            return False
            
        # 分次制限チェック
        if current_count['minute'] >= limits['minute']:
            return False
            
        return True

class ResponseCache:
    def __init__(self, max_size: int = 1000):
        self.cache = {}
        self.max_size = max_size
        
    def get_cached_response(self, prompt_hash: str) -> Optional[str]:
        """キャッシュからレスポンス取得"""
        return self.cache.get(prompt_hash)
        
    def cache_response(self, prompt_hash: str, response: str):
        """レスポンスをキャッシュに保存"""
        if len(self.cache) >= self.max_size:
            # LRU削除
            oldest_key = next(iter(self.cache))
            del self.cache[oldest_key]
        self.cache[prompt_hash] = response
```

## 7. 軽量化されたエージェント実装

### 7.1 効率的なタスクプランナー
```python
class EfficientTaskPlanner:
    def __init__(self, llm_manager: LLMProviderManager):
        self.llm_manager = llm_manager
        self.cache = ResponseCache()
        
    async def decompose_goal(self, goal: str) -> List[Task]:
        """目標の効率的分割（キャッシュ活用）"""
        
        # シンプルなプロンプトでAPI使用量削減
        prompt = f"""
        Goal: {goal}
        
        Break this into 3-5 concrete, executable tasks.
        Format: Task1: description | Task2: description | Task3: description
        """
        
        # キャッシュチェック
        prompt_hash = hashlib.md5(prompt.encode()).hexdigest()
        cached_result = self.cache.get_cached_response(prompt_hash)
        
        if cached_result:
            return self._parse_tasks(cached_result)
            
        # LLM実行
        response = await self.llm_manager.get_completion(
            prompt, 
            task_type="simple_task"
        )
        
        # キャッシュ保存
        self.cache.cache_response(prompt_hash, response)
        
        return self._parse_tasks(response)
```

### 7.2 バッチ処理による効率化
```python
class BatchProcessor:
    def __init__(self, llm_manager: LLMProviderManager):
        self.llm_manager = llm_manager
        self.batch_size = 3  # 複数タスクを一度に処理
        
    async def process_tasks_batch(self, tasks: List[Task]) -> List[Result]:
        """複数タスクの一括処理でAPI呼び出し削減"""
        
        results = []
        for i in range(0, len(tasks), self.batch_size):
            batch = tasks[i:i + self.batch_size]
            
            # バッチプロンプト作成
            batch_prompt = self._create_batch_prompt(batch)
            
            # 一括実行
            batch_response = await self.llm_manager.get_completion(
                batch_prompt,
                task_type="general"
            )
            
            # レスポンス分割
            batch_results = self._parse_batch_response(batch_response, batch)
            results.extend(batch_results)
            
        return results
```

## 8. 使用量監視・最適化

### 8.1 クォータ追跡
```python
class QuotaTracker:
    def __init__(self):
        self.usage_log = defaultdict(list)
        
    def log_request(self, provider: str, tokens_used: int, cost: float = 0):
        """API使用量記録"""
        self.usage_log[provider].append({
            'timestamp': datetime.now(),
            'tokens': tokens_used,
            'cost': cost
        })
        
    def get_daily_usage(self, provider: str) -> dict:
        """日次使用量取得"""
        today = datetime.now().date()
        today_usage = [
            log for log in self.usage_log[provider]
            if log['timestamp'].date() == today
        ]
        
        return {
            'requests': len(today_usage),
            'tokens': sum(log['tokens'] for log in today_usage),
            'cost': sum(log['cost'] for log in today_usage)
        }
```

### 8.2 自動最適化
```python
class AutoOptimizer:
    def __init__(self, quota_tracker: QuotaTracker):
        self.quota_tracker = quota_tracker
        
    def optimize_provider_selection(self) -> dict:
        """使用状況に基づく最適化推奨"""
        
        recommendations = {}
        
        for provider in ['google_gemini', 'groq_llama', 'together_ai']:
            usage = self.quota_tracker.get_daily_usage(provider)
            limit = self._get_daily_limit(provider)
            
            usage_ratio = usage['requests'] / limit
            
            if usage_ratio > 0.8:  # 80%超過
                recommendations[provider] = "REDUCE_USAGE"
            elif usage_ratio < 0.3:  # 30%未満
                recommendations[provider] = "CAN_INCREASE"
            else:
                recommendations[provider] = "OPTIMAL"
                
        return recommendations
```

## 9. 設定例

### 9.1 プロバイダー設定
```yaml
# config/providers.yaml
providers:
  google_gemini:
    model: "gemini-1.5-flash"
    api_key_env: "GOOGLE_API_KEY"
    base_url: "https://generativelanguage.googleapis.com/v1beta"
    max_tokens: 2048
    temperature: 0.7
    
  groq_llama:
    model: "llama3-70b-8192"
    api_key_env: "GROQ_API_KEY"
    base_url: "https://api.groq.com/openai/v1"
    max_tokens: 4096
    temperature: 0.3
    
  together_ai:
    model: "meta-llama/Llama-3-8b-chat-hf"
    api_key_env: "TOGETHER_API_KEY"
    base_url: "https://api.together.xyz/v1"
    max_tokens: 2048
    temperature: 0.5
```

### 9.2 使用量制限設定
```yaml
# config/limits.yaml
daily_limits:
  google_gemini: 1500     # Google AI Studio無料枠
  groq_llama: 14400       # Groq無料枠
  together_ai: 6          # 月200÷30日

optimization:
  enable_caching: true
  cache_ttl_hours: 24
  batch_processing: true
  max_batch_size: 3
  
fallback:
  max_retries: 3
  retry_delay_seconds: 5
  emergency_provider: "together_ai"
```

## 10. インストール・セットアップ

### 10.1 簡単インストール
```bash
# 依存関係インストール（軽量）
pip install openai groq google-generativeai requests aiohttp

# プロジェクトクローン
git clone <repository_url>
cd free-llm-agent

# 環境設定
cp .env.example .env
# .envファイルにAPIキーを記入

# 初回セットアップ
python setup.py
```

### 10.2 設定確認スクリプト
```python
# setup_checker.py
async def check_all_providers():
    """全プロバイダーの動作確認"""
    
    manager = LLMProviderManager()
    
    for provider_name in ['google_gemini', 'groq_llama', 'together_ai']:
        try:
            test_response = await manager.get_completion(
                "Hello, respond with 'OK'", 
                provider=provider_name
            )
            print(f"✅ {provider_name}: {test_response}")
        except Exception as e:
            print(f"❌ {provider_name}: {str(e)}")
```

## 11. 運用上の注意点

### 11.1 コスト管理
- **無料枠監視**: 日次・月次使用量の厳密な追跡
- **自動停止**: 制限近接時の自動停止機能
- **優先度制御**: 重要タスクの優先実行

### 11.2 可用性対策
- **マルチプロバイダー**: 単一障害点の排除
- **グレースフル劣化**: サービス停止時の機能制限モード
- **オフライン対応**: ネットワーク断絶時の基本機能維持

## 12. 実装スケジュール

### Phase 1: 基盤構築（1週間）
1. マルチプロバイダー管理システム
2. レート制限・キャッシュ機能
3. 基本的なタスク実行

### Phase 2: 最適化（1週間）
1. バッチ処理機能
2. 使用量監視・自動最適化
3. フォールバック機能

### Phase 3: 統合・テスト（3-5日）
1. エージェント機能統合
2. エラーハンドリング
3. 動作テスト・調整

この設計により、**高価なローカルGPUの代わりに複数の無料クラウドサービスを組み合わせる**ことで、まるで**複数の専門家チームを適材適所で活用する**ような効率的なシステムを構築できます。