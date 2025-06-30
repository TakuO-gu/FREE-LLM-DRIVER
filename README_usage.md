# Free LLM Driver - 使用方法

無料オンラインLLM + Open Interpreter実装の使用方法

## クイックスタート

### 1. セットアップ確認
```bash
python check_setup.py
```

### 2. 基本的な使用方法

#### インタラクティブモード
```bash
python main.py -i
```

#### 直接目標実行
```bash
python main.py --goal "Pythonでファイル管理ツールを作成"
```

#### システム状況確認
```bash
python main.py --status
```

#### 最適化状況確認
```bash
python main.py --optimize
```

## 設定

### APIキー設定
`.env`ファイルで各サービスのAPIキーを設定：

```env
GOOGLE_API_KEY=your_google_api_key
GROQ_API_KEY=your_groq_api_key  
TOGETHER_API_KEY=your_together_api_key
```

### プロバイダー設定
`config/providers.yaml`でプロバイダーの詳細設定を調整できます。

### 制限設定
`config/limits.yaml`でレート制限やキャッシュ設定を調整できます。

## 使用例

### 基本的なタスク
```bash
python main.py --goal "現在のディレクトリのファイル一覧を表示"
```

### コード生成
```bash
python main.py --goal "CSVファイルを読み込んでグラフを作成するPythonスクリプト"
```

### 分析タスク
```bash
python main.py --goal "ログファイルを分析して異常を検出"
```

## インタラクティブモードコマンド

- `/help` - ヘルプ表示
- `/status` - システム状況表示
- `/optimize` - 最適化状況表示
- `/quit` - 終了

## トラブルシューティング

### APIエラーが発生する場合
1. APIキーが正しく設定されているか確認
2. プロバイダーの無料枠を超過していないか確認
3. ネットワーク接続を確認

### パフォーマンスが遅い場合
1. キャッシュが有効になっているか確認
2. 最適化推奨事項を確認（`--optimize`）
3. 使用量の多いプロバイダーを制限

### 実行エラーが発生する場合
1. セットアップスクリプトを実行（`python check_setup.py`）
2. ログファイル（`logs/free_llm_driver.log`）を確認
3. 安全モードを有効にして実行

## ログとデータ

- ログファイル: `logs/free_llm_driver.log`
- 使用量データ: `logs/usage_data.json` 
- キャッシュデータ: `.cache/llm_responses.cache`

## 制限事項

- 各プロバイダーの無料枠内での使用
- 安全モードでは危険なコード実行を制限
- ネットワーク接続が必要

## サポート

問題が発生した場合は、ログファイルを確認し、`check_setup.py`を実行してシステム状況を確認してください。