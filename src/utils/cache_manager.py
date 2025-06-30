"""
キャッシュ管理システム
LLMレスポンスを効率的にキャッシュし、API使用量を削減
"""

import hashlib
import json
import logging
import pickle
import time
from typing import Optional, Dict, Any, List, Tuple
from datetime import datetime, timedelta
from collections import OrderedDict
import os

class ResponseCache:
    """LLMレスポンスキャッシュ管理"""
    
    def __init__(self, max_size: int = 1000, ttl_hours: int = 24, persist_to_disk: bool = True):
        self.max_size = max_size
        self.ttl_seconds = ttl_hours * 3600
        self.persist_to_disk = persist_to_disk
        
        # メモリキャッシュ（LRU）
        self.memory_cache: OrderedDict[str, Tuple[str, float]] = OrderedDict()
        
        # ディスクキャッシュのパス
        self.cache_dir = os.path.join(os.getcwd(), '.cache')
        self.cache_file = os.path.join(self.cache_dir, 'llm_responses.cache')
        
        # 統計情報
        self.stats = {
            'hits': 0,
            'misses': 0,
            'saves': 0,
            'evictions': 0
        }
        
        # 初期化
        self._ensure_cache_dir()
        if self.persist_to_disk:
            self._load_from_disk()
    
    def _ensure_cache_dir(self):
        """キャッシュディレクトリの作成"""
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)
            logging.info(f"📁 キャッシュディレクトリを作成: {self.cache_dir}")
    
    def _generate_cache_key(self, prompt: str, **kwargs) -> str:
        """キャッシュキーの生成"""
        # プロンプトとパラメータから一意なハッシュを生成
        cache_data = {
            'prompt': prompt.strip(),
            'params': kwargs
        }
        
        # JSON文字列化してハッシュ化
        cache_str = json.dumps(cache_data, sort_keys=True, ensure_ascii=False)
        return hashlib.sha256(cache_str.encode('utf-8')).hexdigest()
    
    def _is_expired(self, timestamp: float) -> bool:
        """キャッシュの有効期限チェック"""
        return time.time() - timestamp > self.ttl_seconds
    
    def _cleanup_expired(self):
        """期限切れキャッシュのクリーンアップ"""
        current_time = time.time()
        expired_keys = []
        
        for key, (_, timestamp) in self.memory_cache.items():
            if self._is_expired(timestamp):
                expired_keys.append(key)
        
        for key in expired_keys:
            del self.memory_cache[key]
            self.stats['evictions'] += 1
        
        if expired_keys:
            logging.debug(f"🗑️ 期限切れキャッシュを削除: {len(expired_keys)}件")
    
    def _evict_lru(self):
        """LRU（最も古いもの）を削除"""
        if len(self.memory_cache) >= self.max_size:
            # 最も古いキャッシュを削除
            oldest_key = next(iter(self.memory_cache))
            del self.memory_cache[oldest_key]
            self.stats['evictions'] += 1
            logging.debug("🗑️ LRUキャッシュを削除")
    
    def get_cached_response(self, prompt: str, **kwargs) -> Optional[str]:
        """キャッシュからレスポンスを取得"""
        cache_key = self._generate_cache_key(prompt, **kwargs)
        
        # 期限切れクリーンアップ
        self._cleanup_expired()
        
        if cache_key in self.memory_cache:
            response, timestamp = self.memory_cache[cache_key]
            
            # 有効期限チェック
            if not self._is_expired(timestamp):
                # LRU更新（最後に使用したものを末尾に移動）
                self.memory_cache.move_to_end(cache_key)
                self.stats['hits'] += 1
                
                logging.debug(f"💰 キャッシュヒット: {cache_key[:8]}...")
                return response
            else:
                # 期限切れなので削除
                del self.memory_cache[cache_key]
                self.stats['evictions'] += 1
        
        self.stats['misses'] += 1
        return None
    
    def cache_response(self, prompt: str, response: str, **kwargs):
        """レスポンスをキャッシュに保存"""
        if not response or not response.strip():
            return  # 空のレスポンスはキャッシュしない
        
        cache_key = self._generate_cache_key(prompt, **kwargs)
        current_time = time.time()
        
        # LRU削除
        self._evict_lru()
        
        # キャッシュに保存
        self.memory_cache[cache_key] = (response, current_time)
        self.stats['saves'] += 1
        
        logging.debug(f"💾 キャッシュ保存: {cache_key[:8]}...")
        
        # ディスクに永続化
        if self.persist_to_disk:
            self._save_to_disk()
    
    def _save_to_disk(self):
        """キャッシュのディスク保存"""
        try:
            with open(self.cache_file, 'wb') as f:
                pickle.dump(dict(self.memory_cache), f)
            logging.debug("💾 キャッシュをディスクに保存")
        except Exception as e:
            logging.error(f"❌ キャッシュ保存エラー: {e}")
    
    def _load_from_disk(self):
        """ディスクからキャッシュを読み込み"""
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'rb') as f:
                    disk_cache = pickle.load(f)
                
                # 有効期限チェックして読み込み
                current_time = time.time()
                valid_count = 0
                
                for key, (response, timestamp) in disk_cache.items():
                    if not self._is_expired(timestamp):
                        self.memory_cache[key] = (response, timestamp)
                        valid_count += 1
                
                logging.info(f"📚 ディスクから{valid_count}件のキャッシュを読み込み")
                
        except Exception as e:
            logging.error(f"❌ キャッシュ読み込みエラー: {e}")
    
    def clear_cache(self):
        """キャッシュのクリア"""
        self.memory_cache.clear()
        self.stats = {
            'hits': 0,
            'misses': 0,
            'saves': 0,
            'evictions': 0
        }
        
        # ディスクキャッシュも削除
        if self.persist_to_disk and os.path.exists(self.cache_file):
            os.remove(self.cache_file)
        
        logging.info("🗑️ キャッシュを全クリア")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """キャッシュ統計情報取得"""
        total_requests = self.stats['hits'] + self.stats['misses']
        hit_rate = (self.stats['hits'] / total_requests * 100) if total_requests > 0 else 0
        
        return {
            'cache_size': len(self.memory_cache),
            'max_size': self.max_size,
            'hit_rate_percent': round(hit_rate, 2),
            'stats': self.stats.copy(),
            'ttl_hours': self.ttl_seconds // 3600,
            'persist_to_disk': self.persist_to_disk
        }
    
    def get_cache_info(self) -> Dict[str, Any]:
        """キャッシュ詳細情報取得"""
        current_time = time.time()
        
        # 年齢別分析
        age_buckets = {'0-1h': 0, '1-6h': 0, '6-24h': 0, '24h+': 0}
        
        for _, (_, timestamp) in self.memory_cache.items():
            age_hours = (current_time - timestamp) / 3600
            
            if age_hours <= 1:
                age_buckets['0-1h'] += 1
            elif age_hours <= 6:
                age_buckets['1-6h'] += 1
            elif age_hours <= 24:
                age_buckets['6-24h'] += 1
            else:
                age_buckets['24h+'] += 1
        
        return {
            **self.get_cache_stats(),
            'age_distribution': age_buckets,
            'disk_cache_exists': os.path.exists(self.cache_file) if self.persist_to_disk else False
        }
    
    def optimize_cache(self):
        """キャッシュの最適化"""
        original_size = len(self.memory_cache)
        
        # 期限切れクリーンアップ
        self._cleanup_expired()
        
        # サイズ制限の適用
        while len(self.memory_cache) > self.max_size * 0.8:  # 80%まで削減
            self._evict_lru()
        
        optimized_size = len(self.memory_cache)
        removed_count = original_size - optimized_size
        
        if removed_count > 0:
            logging.info(f"🔧 キャッシュ最適化: {removed_count}件削除 ({original_size} → {optimized_size})")
        
        # ディスクに保存
        if self.persist_to_disk:
            self._save_to_disk()

class BatchCache:
    """バッチ処理用のキャッシュ管理"""
    
    def __init__(self, base_cache: ResponseCache):
        self.base_cache = base_cache
        self.batch_cache: Dict[str, List[str]] = {}
    
    def get_batch_responses(self, prompts: List[str], **kwargs) -> List[Optional[str]]:
        """バッチプロンプトのキャッシュ取得"""
        responses = []
        
        for prompt in prompts:
            cached_response = self.base_cache.get_cached_response(prompt, **kwargs)
            responses.append(cached_response)
        
        return responses
    
    def cache_batch_responses(self, prompts: List[str], responses: List[str], **kwargs):
        """バッチレスポンスのキャッシュ保存"""
        if len(prompts) != len(responses):
            logging.error("❌ プロンプトとレスポンスの数が一致しません")
            return
        
        for prompt, response in zip(prompts, responses):
            if response:  # 空でないレスポンスのみキャッシュ
                self.base_cache.cache_response(prompt, response, **kwargs)
    
    def get_partial_batch_info(self, prompts: List[str], **kwargs) -> Dict[str, Any]:
        """部分的なバッチキャッシュ情報"""
        cached_count = 0
        total_count = len(prompts)
        
        for prompt in prompts:
            if self.base_cache.get_cached_response(prompt, **kwargs):
                cached_count += 1
        
        return {
            'total_prompts': total_count,
            'cached_responses': cached_count,
            'cache_hit_rate': (cached_count / total_count * 100) if total_count > 0 else 0,
            'remaining_requests': total_count - cached_count
        }