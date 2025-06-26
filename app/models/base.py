"""
数据库模型基类
定义通用字段和方法
"""

import uuid
from datetime import datetime
from typing import Any, Dict

from sqlalchemy import Column, DateTime, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func


class BaseModel:
    """模型基类，包含通用字段"""
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), comment="主键ID")
    created_at = Column(DateTime, default=func.now(), nullable=False, comment="创建时间")
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False, comment="更新时间")
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        result = {}
        for column in self.__table__.columns:
            value = getattr(self, column.name)
            if isinstance(value, datetime):
                value = value.isoformat()
            result[column.name] = value
        return result
    
    def update_from_dict(self, data: Dict[str, Any]):
        """从字典更新模型"""
        for key, value in data.items():
            if hasattr(self, key):
                setattr(self, key, value)


# 创建声明基类
Base = declarative_base(cls=BaseModel) 