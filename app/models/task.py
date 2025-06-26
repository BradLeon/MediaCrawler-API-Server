"""
任务模型
定义爬虫任务的数据结构
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import Column, String, Integer, Text, JSON, DateTime, Enum
from sqlalchemy.sql import func

from .base import Base


class TaskModel(Base):
    """爬虫任务模型"""
    
    __tablename__ = "tasks"
    
    # 任务基本信息
    task_id = Column(String(50), unique=True, nullable=False, index=True, comment="任务ID")
    platform = Column(String(20), nullable=False, index=True, comment="平台标识")
    task_type = Column(
        Enum("search", "detail", "creator", name="task_type_enum"),
        nullable=False, 
        index=True, 
        comment="任务类型"
    )
    
    # 任务状态
    status = Column(
        Enum("pending", "running", "completed", "failed", "cancelled", name="task_status_enum"),
        default="pending",
        nullable=False,
        index=True,
        comment="任务状态"
    )
    
    # 进度信息
    progress = Column(Integer, default=0, comment="任务进度(0-100)")
    total_items = Column(Integer, default=0, comment="总项目数")
    completed_items = Column(Integer, default=0, comment="已完成项目数")
    failed_items = Column(Integer, default=0, comment="失败项目数")
    
    # 任务参数
    parameters = Column(JSON, comment="任务参数(JSON格式)")
    
    # 结果统计
    results_summary = Column(JSON, comment="结果摘要(JSON格式)")
    
    # 时间信息
    started_at = Column(DateTime, comment="开始时间")
    completed_at = Column(DateTime, comment="完成时间")
    estimated_completion = Column(DateTime, comment="预计完成时间")
    
    # 错误信息
    error_message = Column(Text, comment="错误信息")
    error_code = Column(String(50), comment="错误代码")
    
    # 回调配置
    callback_url = Column(String(500), comment="回调URL")
    callback_sent = Column(Integer, default=0, comment="回调发送次数")
    
    # 创建者信息
    created_by = Column(String(100), comment="创建者")
    
    def __repr__(self):
        return f"<TaskModel(task_id={self.task_id}, platform={self.platform}, status={self.status})>"
    
    @property
    def is_running(self) -> bool:
        """是否正在运行"""
        return self.status == "running"
    
    @property
    def is_completed(self) -> bool:
        """是否已完成"""
        return self.status in ["completed", "failed", "cancelled"]
    
    @property
    def success_rate(self) -> float:
        """成功率"""
        if self.total_items == 0:
            return 0.0
        return (self.completed_items / self.total_items) * 100
    
    def update_progress(self, completed: int, failed: int = 0, total: Optional[int] = None):
        """更新任务进度"""
        self.completed_items = completed
        self.failed_items = failed
        if total is not None:
            self.total_items = total
        
        if self.total_items > 0:
            self.progress = int((completed / self.total_items) * 100)
        
        self.updated_at = func.now() 