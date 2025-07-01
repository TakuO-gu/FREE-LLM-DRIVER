# Free LLM Driver - 脳型統合AI処理システム

## 🧠 プロジェクト概要

**Free LLM Driver**は、生物学的脳構造を模倣した革新的なAI処理システムです。無料オンラインLLMサービスと脳幹・大脳辺縁系・大脳皮質の機能を統合し、感情・学習・適応能力を持つ次世代AIエージェントを実現します。

### ✨ 主な特徴

- 🧠 **脳型統合アーキテクチャ**: 生物学的脳構造の3層システム
- 💭 **感情的知能**: 脅威検知・記憶・報酬による感情的判断
- 🎯 **高次認知制御**: 注意管理・競合解決・メタ認知監視
- 🔄 **24/7監視システム**: Neural Kernelによる継続的システム監視
- 📚 **適応学習**: 経験からの自動学習と改善
- 🌐 **無料LLM活用**: 複数の無料APIを効率的に統合使用

## 🏗️ システムアーキテクチャ

### 脳型3層構造

```
┌─────────────────────────────────────────────────────────┐
│                大脳皮質 (Executive Controller)              │
│  🎯 高次認知制御・意思決定・メタ認知監視・競合解決             │
└─────────────────────┬───────────────────────────────────┘
                      │ フィードバック
┌─────────────────────┴───────────────────────────────────┐
│              大脳辺縁系 (Emotional System)                │
│  💭 感情処理・脅威検知・適応記憶・報酬学習                   │
└─────────────────────┬───────────────────────────────────┘
                      │ 生理的フィードバック  
┌─────────────────────┴───────────────────────────────────┐
│                脳幹 (Neural Kernel)                     │
│  🔋 24/7システム監視・リソース管理・緊急事態対応            │
└─────────────────────────────────────────────────────────┘
```

### 統合神経システム

```python
# 脳型統合処理の例
async def process_goal_neural(user_goal: str):
    # 1. 脳幹レベル: システム状態確認
    system_state = await neural_kernel.get_system_state()
    
    # 2. 大脳辺縁系: 感情的・記憶的評価
    emotional_context = await emotional_system.evaluate_task_emotion(user_goal)
    
    # 3. 処理モード決定 (EMERGENCY/ANALYTICAL/INTUITIVE/MAINTENANCE)
    processing_mode = determine_processing_mode(system_state, emotional_context)
    
    # 4. 大脳皮質: 高次認知処理
    executive_decision = await executive_controller.executive_decision(
        task_options, integrated_context
    )
    
    # 5. 実行とフィードバック学習
    result = await execute_with_monitoring(executive_decision)
    await neural_learning_integration(goal, decision, result)
    
    return result
```

## 🚀 クイックスタート

### 1. インストール

```bash
git clone https://github.com/your-repo/Free-LLM-Driver.git
cd Free-LLM-Driver
pip install -r requirements.txt
```

### 2. 環境設定

```bash
# .envファイルを作成してAPIキーを設定
cp .env.example .env

# APIキーを取得・設定
# Google AI Studio: https://makersuite.google.com/app/apikey
# Groq: https://console.groq.com/keys
# Together AI: https://api.together.xyz/settings/api-keys
```

```env
GOOGLE_API_KEY=your_google_api_key
GROQ_API_KEY=your_groq_api_key  
TOGETHER_API_KEY=your_together_api_key
```

### 3. システム確認

```bash
# セットアップ確認
python check_setup.py

# 統合システムテスト
python test_integrated_brain.py
```

### 4. 基本的な使用方法

```bash
# インタラクティブモード
python main.py -i

# 直接目標実行
python main.py --goal "Pythonでファイル管理ツールを作成"

# システム状況確認
python main.py --status

# 最適化状況確認
python main.py --optimize
```

## 🧪 テスト結果

最新のシステムテスト結果：

```
🎯 総合テスト結果
============================================================
✅ PASS 初期化テスト
✅ PASS 目標処理テスト (5/5成功)
✅ PASS フィードバックループテスト  
✅ PASS 感情・認知統合テスト
✅ PASS 学習・適応テスト

📊 テスト結果サマリー: 100% (5/5)
🎉 統合脳システムは良好に動作しています
```

## 🔧 設定

### プロバイダー設定 (`config/providers.yaml`)

```yaml
providers:
  google_gemini:
    model: "gemini-1.5-flash"
    max_tokens: 2048
    temperature: 0.7
    
  groq_llama:
    model: "llama3-70b-8192"
    max_tokens: 4096
    temperature: 0.3
    
  together_ai:
    model: "meta-llama/Llama-3-8b-chat-hf"
    max_tokens: 2048
    temperature: 0.5
```

### 制限設定 (`config/limits.yaml`)

```yaml
daily_limits:
  google_gemini: 1500
  groq_llama: 14400
  together_ai: 6

optimization:
  enable_caching: true
  cache_ttl_hours: 24
  neural_integration_level: "SEAMLESS"
```

## 📊 システム監視

### Neural Kernel 24/7監視

- **監視頻度**: 100ms間隔 (10回/秒)
- **バイタルサイン**: CPU・メモリ・ディスク・プロセス監視
- **緊急対応**: 自動リソース調整・アラート生成
- **状態管理**: HEALTHY/WARNING/CRITICAL/EMERGENCY

### 感情・学習システム

- **脅威検知**: 危険なコマンドを自動検出
- **感情状態**: POSITIVE/NEUTRAL/NEGATIVE/ANXIOUS/CONFIDENT/FRUSTRATED
- **記憶学習**: 過去の経験から成功・失敗パターンを学習
- **適応調整**: パフォーマンスに基づく動的システム調整

## 🎯 主要機能

### 1. 脳幹機能 (Neural Kernel)
- ✅ 24/7システム監視 (100ms間隔)
- ✅ リソース枯渇の予防的検知
- ✅ 緊急時の自動システム保護
- ✅ 基本的な覚醒レベル調整

### 2. 大脳辺縁系機能 (Emotional System)
- ✅ 脅威検出システム (扁桃体機能)
- ✅ 適応記憶システム (海馬機能)
- ✅ 報酬系による学習強化
- ✅ 感情的重み付けによる優先度調整

### 3. 大脳皮質機能 (Executive Controller)
- ✅ 作業記憶システム (7±2項目管理)
- ✅ 動的注意リソース管理
- ✅ 複数評価軸での競合解決
- ✅ メタ認知的自己監視

### 4. 統合神経システム
- ✅ 多層時間スケールでの学習
- ✅ 感情と理性の動的バランス調整
- ✅ 自己適応型システム最適化
- ✅ 創発的な問題解決能力

## 📈 使用量管理

### 無料APIクォータ管理
- **Google Gemini**: 1,500 req/day
- **Groq**: 14,400 req/day  
- **Together AI**: 200 req/month

### 自動最適化
- 使用量に基づくプロバイダー自動選択
- キャッシュ機能によるAPI使用量削減
- 失敗時の自動フォールバック

## 🔍 ログとデータ

- **ログファイル**: `logs/free_llm_driver.log`
- **使用量データ**: `logs/usage_data.json` 
- **キャッシュデータ**: `.cache/llm_responses.cache`
- **学習データ**: 各システムコンポーネントが自動管理

## 🚨 トラブルシューティング

### APIエラーが発生する場合
1. APIキーが正しく設定されているか確認
2. プロバイダーの無料枠を超過していないか確認
3. ネットワーク接続を確認

### パフォーマンスが遅い場合
1. キャッシュが有効になっているか確認
2. 最適化推奨事項を確認（`--optimize`）
3. 使用量の多いプロバイダーを制限

### 統合システムエラー
1. `python test_integrated_brain.py` でシステム状態確認
2. Neural Kernel監視状況確認
3. ログファイル（`logs/free_llm_driver.log`）を確認

## 🤝 コントリビューション

このプロジェクトへの貢献を歓迎します：

1. Issue報告
2. 機能提案
3. プルリクエスト
4. ドキュメント改善

## 📄 ライセンス

このプロジェクトはMITライセンスの下で公開されています。

## 🙏 謝辞

- 無料LLMプロバイダー各社のAPI提供
- 生物学的脳機能研究のインスパイア
- オープンソースコミュニティのサポート

---

**Free LLM Driver** - 脳の仕組みを理解し、それをAIで再現する挑戦的なプロジェクトです。