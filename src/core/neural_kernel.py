"""
Neural Kernel System - 生物学的脳幹機能を模倣した基盤監視システム
24/7でシステムの生命維持機能を監視・制御
"""

import asyncio
import logging
import psutil
import time
import threading
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum
from datetime import datetime, timedelta

class SystemStatus(Enum):
    """システム状態"""
    HEALTHY = "healthy"
    WARNING = "warning" 
    CRITICAL = "critical"
    EMERGENCY = "emergency"

class AlertLevel(Enum):
    """アラートレベル"""
    INFO = 1
    WARNING = 2
    CRITICAL = 3
    EMERGENCY = 4

@dataclass
class VitalSign:
    """バイタルサイン"""
    name: str
    value: float
    threshold_warning: float
    threshold_critical: float
    unit: str = ""
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
    
    def get_status(self) -> SystemStatus:
        """状態判定"""
        if self.value >= self.threshold_critical:
            return SystemStatus.CRITICAL
        elif self.value >= self.threshold_warning:
            return SystemStatus.WARNING
        else:
            return SystemStatus.HEALTHY

@dataclass
class SystemHealth:
    """システムヘルス状態"""
    overall_status: SystemStatus
    vital_signs: Dict[str, VitalSign]
    alerts: List[str]
    timestamp: datetime
    
    @property
    def critical(self) -> bool:
        return self.overall_status in [SystemStatus.CRITICAL, SystemStatus.EMERGENCY]

class HealthMonitor:
    """システムヘルス監視"""
    
    def __init__(self):
        self.history: List[SystemHealth] = []
        self.max_history = 1000
        
        # バイタルサインの閾値設定
        self.vital_thresholds = {
            'cpu_usage': {'warning': 80.0, 'critical': 95.0},
            'memory_usage': {'warning': 85.0, 'critical': 95.0},
            'disk_usage': {'warning': 85.0, 'critical': 95.0},
            'network_errors': {'warning': 100, 'critical': 1000},
            'response_time': {'warning': 5.0, 'critical': 10.0},
            'error_rate': {'warning': 5.0, 'critical': 15.0}
        }
    
    async def check_system_vitals(self) -> SystemHealth:
        """システムバイタルチェック"""
        try:
            vital_signs = {}
            alerts = []
            
            # CPU使用率
            cpu_percent = psutil.cpu_percent(interval=0.1)
            vital_signs['cpu_usage'] = VitalSign(
                name="CPU使用率",
                value=cpu_percent,
                threshold_warning=self.vital_thresholds['cpu_usage']['warning'],
                threshold_critical=self.vital_thresholds['cpu_usage']['critical'],
                unit="%"
            )
            
            # メモリ使用率
            memory = psutil.virtual_memory()
            vital_signs['memory_usage'] = VitalSign(
                name="メモリ使用率", 
                value=memory.percent,
                threshold_warning=self.vital_thresholds['memory_usage']['warning'],
                threshold_critical=self.vital_thresholds['memory_usage']['critical'],
                unit="%"
            )
            
            # ディスク使用率
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            vital_signs['disk_usage'] = VitalSign(
                name="ディスク使用率",
                value=disk_percent,
                threshold_warning=self.vital_thresholds['disk_usage']['warning'],
                threshold_critical=self.vital_thresholds['disk_usage']['critical'],
                unit="%"
            )
            
            # プロセス数
            process_count = len(psutil.pids())
            vital_signs['process_count'] = VitalSign(
                name="プロセス数",
                value=process_count,
                threshold_warning=500,
                threshold_critical=1000,
                unit="個"
            )
            
            # 全体状態の判定
            critical_count = sum(1 for vs in vital_signs.values() if vs.get_status() == SystemStatus.CRITICAL)
            warning_count = sum(1 for vs in vital_signs.values() if vs.get_status() == SystemStatus.WARNING)
            
            if critical_count > 0:
                overall_status = SystemStatus.CRITICAL
                alerts.append(f"⚠️ CRITICAL: {critical_count}個の重要な問題を検出")
            elif warning_count > 2:
                overall_status = SystemStatus.WARNING
                alerts.append(f"⚠️ WARNING: {warning_count}個の警告を検出")
            else:
                overall_status = SystemStatus.HEALTHY
            
            health = SystemHealth(
                overall_status=overall_status,
                vital_signs=vital_signs,
                alerts=alerts,
                timestamp=datetime.now()
            )
            
            # 履歴に追加
            self.history.append(health)
            if len(self.history) > self.max_history:
                self.history.pop(0)
            
            return health
            
        except Exception as e:
            logging.error(f"❌ ヘルスチェックエラー: {e}")
            return SystemHealth(
                overall_status=SystemStatus.EMERGENCY,
                vital_signs={},
                alerts=[f"ヘルスチェック失敗: {str(e)}"],
                timestamp=datetime.now()
            )
    
    def get_health_trend(self, minutes: int = 10) -> Dict[str, Any]:
        """ヘルストレンド分析"""
        cutoff_time = datetime.now() - timedelta(minutes=minutes)
        recent_health = [h for h in self.history if h.timestamp >= cutoff_time]
        
        if not recent_health:
            return {'trend': 'no_data'}
        
        # 状態変化の傾向
        status_counts = {}
        for health in recent_health:
            status = health.overall_status.value
            status_counts[status] = status_counts.get(status, 0) + 1
        
        return {
            'trend': 'improving' if recent_health[-1].overall_status == SystemStatus.HEALTHY else 'degrading',
            'status_distribution': status_counts,
            'sample_count': len(recent_health),
            'time_range_minutes': minutes
        }

class ResourceMonitor:
    """リソース監視"""
    
    def __init__(self):
        self.resource_limits = {
            'max_memory_mb': 1024,  # 1GB制限
            'max_cpu_time': 300,    # 5分制限
            'max_file_handles': 100,
            'max_network_connections': 50
        }
        self.current_usage = {
            'memory_mb': 0,
            'cpu_time': 0,
            'file_handles': 0,
            'network_connections': 0
        }
    
    async def check_resource_usage(self) -> Dict[str, Any]:
        """リソース使用量チェック"""
        try:
            # 現在のプロセス情報
            process = psutil.Process()
            
            # メモリ使用量
            memory_info = process.memory_info()
            memory_mb = memory_info.rss / 1024 / 1024  # MB変換
            
            # CPU時間
            cpu_times = process.cpu_times()
            cpu_time = cpu_times.user + cpu_times.system
            
            # ファイルハンドル数
            try:
                file_handles = process.num_fds() if hasattr(process, 'num_fds') else len(process.open_files())
            except:
                file_handles = 0
            
            # ネットワーク接続数
            try:
                network_connections = len(process.connections())
            except:
                network_connections = 0
            
            self.current_usage.update({
                'memory_mb': memory_mb,
                'cpu_time': cpu_time,
                'file_handles': file_handles,
                'network_connections': network_connections
            })
            
            # 制限チェック
            warnings = []
            for resource, current in self.current_usage.items():
                limit_key = f'max_{resource}'
                if limit_key in self.resource_limits:
                    limit = self.resource_limits[limit_key]
                    usage_percent = (current / limit) * 100
                    
                    if usage_percent > 90:
                        warnings.append(f"{resource}: {current:.1f}/{limit} ({usage_percent:.1f}%)")
            
            return {
                'usage': self.current_usage.copy(),
                'limits': self.resource_limits.copy(),
                'warnings': warnings,
                'status': 'warning' if warnings else 'ok'
            }
            
        except Exception as e:
            logging.error(f"❌ リソース監視エラー: {e}")
            return {
                'usage': {},
                'limits': {},
                'warnings': [f"監視エラー: {str(e)}"],
                'status': 'error'
            }

class EmergencyHandler:
    """緊急事態ハンドラー"""
    
    def __init__(self):
        self.emergency_actions = []
        self.emergency_log = []
        self.recovery_procedures = {
            'high_memory': self._handle_high_memory,
            'high_cpu': self._handle_high_cpu,
            'system_overload': self._handle_system_overload,
            'disk_full': self._handle_disk_full
        }
    
    async def activate(self, health: SystemHealth):
        """緊急対応の起動"""
        emergency_time = datetime.now()
        
        logging.critical(f"🚨 緊急事態発生: {health.overall_status.value}")
        
        # 緊急対応ログ
        self.emergency_log.append({
            'timestamp': emergency_time,
            'status': health.overall_status.value,
            'alerts': health.alerts,
            'vital_signs': {name: vs.value for name, vs in health.vital_signs.items()}
        })
        
        # 状況に応じた対応
        for name, vital_sign in health.vital_signs.items():
            if vital_sign.get_status() == SystemStatus.CRITICAL:
                await self._execute_recovery_procedure(name, vital_sign)
    
    async def _execute_recovery_procedure(self, vital_name: str, vital_sign: VitalSign):
        """回復手順の実行"""
        try:
            if vital_name == 'memory_usage' and vital_sign.value > 90:
                await self.recovery_procedures['high_memory']()
            elif vital_name == 'cpu_usage' and vital_sign.value > 90:
                await self.recovery_procedures['high_cpu']()
            elif vital_name == 'disk_usage' and vital_sign.value > 90:
                await self.recovery_procedures['disk_full']()
            
            logging.info(f"🔧 回復手順実行: {vital_name}")
            
        except Exception as e:
            logging.error(f"❌ 回復手順失敗: {vital_name} - {e}")
    
    async def _handle_high_memory(self):
        """高メモリ使用時の対応"""
        import gc
        gc.collect()  # ガベージコレクション強制実行
        
    async def _handle_high_cpu(self):
        """高CPU使用時の対応"""
        await asyncio.sleep(1)  # 短時間の休止
        
    async def _handle_system_overload(self):
        """システム過負荷時の対応"""
        await asyncio.sleep(2)  # システム負荷軽減
        
    async def _handle_disk_full(self):
        """ディスク容量不足時の対応"""
        logging.warning("⚠️ ディスク容量不足 - ログローテーション推奨")

class NeuralKernel:
    """神経系カーネル - 生物学的脳幹機能を模倣"""
    
    def __init__(self):
        self.vital_monitors = {
            'system_health': HealthMonitor(),
            'resource_monitor': ResourceMonitor(),
            'emergency_handler': EmergencyHandler()
        }
        self.always_running = False
        self.monitoring_task = None
        self.stats = {
            'uptime': 0,
            'total_checks': 0,
            'emergency_activations': 0,
            'last_status': SystemStatus.HEALTHY
        }
        self.start_time = None
    
    async def start_neural_kernel(self):
        """神経系カーネル開始"""
        if self.always_running:
            return
        
        self.always_running = True
        self.start_time = datetime.now()
        
        logging.info("🧠 Neural Kernel 起動 - 常時監視開始")
        
        # バックグラウンドで監視タスク開始
        self.monitoring_task = asyncio.create_task(self.continuous_monitoring())
    
    async def stop_neural_kernel(self):
        """神経系カーネル停止"""
        self.always_running = False
        
        if self.monitoring_task:
            self.monitoring_task.cancel()
            try:
                await self.monitoring_task
            except asyncio.CancelledError:
                pass
        
        logging.info("🧠 Neural Kernel 停止")
    
    async def continuous_monitoring(self):
        """脳幹のような24/7監視機能"""
        while self.always_running:
            try:
                # システムバイタルチェック
                health_status = await self.vital_monitors['system_health'].check_system_vitals()
                self.stats['total_checks'] += 1
                self.stats['last_status'] = health_status.overall_status
                
                # 緊急事態検出
                if health_status.critical:
                    await self.vital_monitors['emergency_handler'].activate(health_status)
                    self.stats['emergency_activations'] += 1
                
                # リソース監視
                resource_status = await self.vital_monitors['resource_monitor'].check_resource_usage()
                
                # 基本的な優先度調整
                await self.adjust_base_priorities(health_status, resource_status)
                
                # アップタイム更新
                if self.start_time:
                    self.stats['uptime'] = (datetime.now() - self.start_time).total_seconds()
                
                # 100ms間隔での監視（脳幹の頻度を模倣）
                await asyncio.sleep(0.1)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logging.error(f"❌ Neural Kernel監視エラー: {e}")
                await asyncio.sleep(1)  # エラー時は1秒待機
    
    async def adjust_base_priorities(self, health: SystemHealth, resources: Dict[str, Any]):
        """基本的な優先度調整"""
        try:
            # システム状態に基づく優先度調整
            if health.overall_status == SystemStatus.CRITICAL:
                # 緊急時: 基本機能のみに制限
                logging.warning("🔴 緊急モード: システム負荷軽減")
            elif health.overall_status == SystemStatus.WARNING:
                # 警告時: 処理速度を調整
                logging.info("🟡 警告モード: 処理負荷調整")
            
        except Exception as e:
            logging.error(f"❌ 優先度調整エラー: {e}")
    
    def get_neural_stats(self) -> Dict[str, Any]:
        """神経系カーネル統計"""
        return {
            'running': self.always_running,
            'uptime_seconds': self.stats['uptime'],
            'total_health_checks': self.stats['total_checks'],
            'emergency_activations': self.stats['emergency_activations'],
            'current_status': self.stats['last_status'].value,
            'monitoring_frequency': '100ms',
            'start_time': self.start_time.isoformat() if self.start_time else None
        }
    
    async def get_comprehensive_status(self) -> Dict[str, Any]:
        """包括的なシステム状態"""
        try:
            health = await self.vital_monitors['system_health'].check_system_vitals()
            resources = await self.vital_monitors['resource_monitor'].check_resource_usage()
            health_trend = self.vital_monitors['system_health'].get_health_trend()
            
            return {
                'neural_kernel': self.get_neural_stats(),
                'system_health': {
                    'status': health.overall_status.value,
                    'vital_signs': {name: {
                        'value': vs.value,
                        'status': vs.get_status().value,
                        'unit': vs.unit
                    } for name, vs in health.vital_signs.items()},
                    'alerts': health.alerts,
                    'trend': health_trend
                },
                'resources': resources,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logging.error(f"❌ 包括的状態取得エラー: {e}")
            return {
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }