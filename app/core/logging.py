"""
日志监控模块

提供结构化日志、任务跟踪、性能监控等功能
"""

import logging
import json
import time
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
from dataclasses import dataclass, asdict
from enum import Enum
import asyncio
from pathlib import Path


class LogLevel(Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class TaskEventType(Enum):
    TASK_CREATED = "task_created"
    TASK_STARTED = "task_started"
    TASK_PROGRESS = "task_progress"
    TASK_COMPLETED = "task_completed"
    TASK_FAILED = "task_failed"
    TASK_STOPPED = "task_stopped"
    CRAWLER_LOGIN = "crawler_login"
    CRAWLER_ERROR = "crawler_error"
    DATA_EXTRACTED = "data_extracted"
    DATA_SAVED = "data_saved"


@dataclass
class TaskEvent:
    """任务事件"""
    task_id: str
    event_type: TaskEventType
    timestamp: str
    message: str
    data: Optional[Dict[str, Any]] = None
    platform: Optional[str] = None
    progress: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


@dataclass
class TaskProgress:
    """任务进度"""
    task_id: str
    platform: str
    current_stage: str  # "initializing", "logging_in", "crawling", "processing", "saving"
    progress_percent: float
    items_total: int
    items_completed: int
    items_failed: int
    current_item: Optional[str] = None
    estimated_remaining_time: Optional[int] = None  # 秒
    last_update: Optional[str] = None


class TaskLogger:
    """任务专用日志记录器"""
    
    def __init__(self, task_id: str, platform: str):
        self.task_id = task_id
        self.platform = platform
        self.events: List[TaskEvent] = []
        self.progress = TaskProgress(
            task_id=task_id,
            platform=platform,
            current_stage="initializing",
            progress_percent=0.0,
            items_total=0,
            items_completed=0,
            items_failed=0,
            last_update=datetime.now(timezone.utc).isoformat()
        )
        self.start_time = time.time()
        
    def log_event(self, event_type: TaskEventType, message: str, 
                  data: Optional[Dict] = None, error: Optional[str] = None):
        """记录任务事件"""
        event = TaskEvent(
            task_id=self.task_id,
            event_type=event_type,
            timestamp=datetime.now(timezone.utc).isoformat(),
            message=message,
            data=data,
            platform=self.platform,
            progress=asdict(self.progress),
            error=error
        )
        
        self.events.append(event)
        
        # 同时记录到系统日志
        logger = logging.getLogger(f"task.{self.task_id}")
        log_data = {
            "task_id": self.task_id,
            "platform": self.platform,
            "event_type": event_type.value,
            "message": message,
            "data": data,
            "error": error
        }
        
        if error:
            logger.error(json.dumps(log_data, ensure_ascii=False))
        elif event_type in [TaskEventType.TASK_FAILED, TaskEventType.CRAWLER_ERROR]:
            logger.error(json.dumps(log_data, ensure_ascii=False))
        elif event_type in [TaskEventType.TASK_COMPLETED]:
            logger.info(json.dumps(log_data, ensure_ascii=False))
        else:
            logger.debug(json.dumps(log_data, ensure_ascii=False))
    
    def update_progress(self, current_stage: str = None, progress_percent: float = None,
                       items_total: int = None, items_completed: int = None,
                       items_failed: int = None, current_item: str = None):
        """更新任务进度"""
        if current_stage:
            self.progress.current_stage = current_stage
        if progress_percent is not None:
            self.progress.progress_percent = progress_percent
        if items_total is not None:
            self.progress.items_total = items_total
        if items_completed is not None:
            self.progress.items_completed = items_completed
        if items_failed is not None:
            self.progress.items_failed = items_failed
        if current_item:
            self.progress.current_item = current_item
            
        self.progress.last_update = datetime.now(timezone.utc).isoformat()
        
        # 估算剩余时间
        if self.progress.items_total > 0 and self.progress.items_completed > 0:
            elapsed_time = time.time() - self.start_time
            avg_time_per_item = elapsed_time / self.progress.items_completed
            remaining_items = self.progress.items_total - self.progress.items_completed
            self.progress.estimated_remaining_time = int(avg_time_per_item * remaining_items)
        
        # 记录进度事件
        self.log_event(
            TaskEventType.TASK_PROGRESS,
            f"进度更新: {self.progress.current_stage} - {self.progress.progress_percent:.1f}%",
            data={
                "stage": self.progress.current_stage,
                "progress": self.progress.progress_percent,
                "completed": self.progress.items_completed,
                "total": self.progress.items_total,
                "failed": self.progress.items_failed
            }
        )
    
    def get_recent_events(self, limit: int = 50) -> List[TaskEvent]:
        """获取最近的事件"""
        return self.events[-limit:] if len(self.events) > limit else self.events
    
    def get_progress(self) -> TaskProgress:
        """获取当前进度"""
        return self.progress


class LoggingManager:
    """日志管理器"""
    
    def __init__(self, log_dir: str = "logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        self.task_loggers: Dict[str, TaskLogger] = {}
        self.setup_logging()
    
    def setup_logging(self):
        """设置日志配置"""
        # 创建格式化器
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # 主应用日志
        app_handler = logging.FileHandler(self.log_dir / "app.log", encoding='utf-8')
        app_handler.setFormatter(formatter)
        app_logger = logging.getLogger("app")
        app_logger.addHandler(app_handler)
        app_logger.setLevel(logging.INFO)
        
        # 任务日志
        task_handler = logging.FileHandler(self.log_dir / "tasks.log", encoding='utf-8')
        task_handler.setFormatter(formatter)
        task_logger = logging.getLogger("task")
        task_logger.addHandler(task_handler)
        task_logger.setLevel(logging.DEBUG)
        
        # 错误日志
        error_handler = logging.FileHandler(self.log_dir / "errors.log", encoding='utf-8')
        error_handler.setFormatter(formatter)
        error_handler.setLevel(logging.ERROR)
        
        # 添加错误处理器到所有日志记录器
        for logger_name in ["app", "task"]:
            logger = logging.getLogger(logger_name)
            logger.addHandler(error_handler)
        
        # 控制台输出
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        console_handler.setLevel(logging.INFO)
        
        # 根日志记录器
        root_logger = logging.getLogger()
        root_logger.addHandler(console_handler)
        root_logger.setLevel(logging.INFO)
    
    def create_task_logger(self, task_id: str, platform: str) -> TaskLogger:
        """创建任务日志记录器"""
        task_logger = TaskLogger(task_id, platform)
        self.task_loggers[task_id] = task_logger
        
        # 记录任务创建事件
        task_logger.log_event(
            TaskEventType.TASK_CREATED,
            f"任务已创建: 平台={platform}",
            data={"platform": platform}
        )
        
        return task_logger
    
    def get_task_logger(self, task_id: str) -> Optional[TaskLogger]:
        """获取任务日志记录器"""
        return self.task_loggers.get(task_id)
    
    def get_task_progress(self, task_id: str) -> Optional[TaskProgress]:
        """获取任务进度"""
        task_logger = self.get_task_logger(task_id)
        return task_logger.get_progress() if task_logger else None
    
    def get_task_events(self, task_id: str, limit: int = 50) -> List[TaskEvent]:
        """获取任务事件"""
        task_logger = self.get_task_logger(task_id)
        return task_logger.get_recent_events(limit) if task_logger else []
    
    def cleanup_task_logger(self, task_id: str):
        """清理任务日志记录器"""
        if task_id in self.task_loggers:
            task_logger = self.task_loggers[task_id]
            task_logger.log_event(
                TaskEventType.TASK_COMPLETED,
                "任务日志记录器已清理"
            )
            # 保留日志一段时间后再删除
            # del self.task_loggers[task_id]
    
    def get_system_stats(self) -> Dict[str, Any]:
        """获取系统统计信息"""
        return {
            "active_tasks": len(self.task_loggers),
            "total_events": sum(len(logger.events) for logger in self.task_loggers.values()),
            "log_files": [
                {
                    "name": f.name,
                    "size": f.stat().st_size,
                    "modified": datetime.fromtimestamp(f.stat().st_mtime).isoformat()
                }
                for f in self.log_dir.glob("*.log")
            ]
        }


# 全局日志管理器实例
logging_manager = LoggingManager()


def get_app_logger(name: str = "app") -> logging.Logger:
    """获取应用日志记录器"""
    return logging.getLogger(name) 