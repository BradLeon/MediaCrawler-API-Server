"""
数据读取层基础抽象类和配置
定义数据读取接口和平台特定的映射配置
注意：此模块仅负责数据读取，不负责数据写入
"""
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Any, Optional, Union
from datetime import datetime

from app.models.base import BaseModel
from app.models.content import ContentModel


class PlatformType(Enum):
    """支持的平台类型"""
    XHS = "xhs"          # 小红书
    DOUYIN = "douyin"    # 抖音
    BILIBILI = "bilibili" # B站
    KUAISHOU = "kuaishou" # 快手
    WEIBO = "weibo"      # 微博
    TIEBA = "tieba"      # 百度贴吧
    ZHIHU = "zhihu"      # 知乎


class DataSourceType(Enum):
    """数据源类型枚举"""
    DATABASE = "database"  # 数据库（Supabase/MySQL）
    CSV = "csv"           # CSV文件
    JSON = "json"         # JSON文件


@dataclass
class DataReaderConfig:
    """数据读取器配置类"""
    source_type: DataSourceType
    platform: PlatformType
    
    # 数据库配置
    database_url: Optional[str] = None
    supabase_url: Optional[str] = None
    supabase_key: Optional[str] = None
    
    # 文件存储配置
    file_path: Optional[str] = None
    
    # 其他配置
    max_retries: int = 3
    timeout_seconds: int = 30


@dataclass
class DataAccessResult:
    """数据访问结果类"""
    success: bool
    data: Optional[Union[List[Dict], Dict]] = None
    total: int = 0
    message: str = ""
    error: Optional[Exception] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "success": self.success,
            "data": self.data,
            "total": self.total,
            "message": self.message
        }


@dataclass
class ReaderMetrics:
    """数据读取指标类"""
    operations_count: int = 0
    success_count: int = 0
    error_count: int = 0
    total_processing_time: float = 0.0
    created_at: datetime = field(default_factory=datetime.now)
    
    def record_operation(self, success: bool, count: int = 1, processing_time: float = 0.0):
        """记录操作指标"""
        self.operations_count += count
        if success:
            self.success_count += count
        else:
            self.error_count += count
        self.total_processing_time += processing_time
    
    def get_success_rate(self) -> float:
        """获取成功率"""
        if self.operations_count == 0:
            return 0.0
        return self.success_count / self.operations_count
    
    def get_average_processing_time(self) -> float:
        """获取平均处理时间"""
        if self.operations_count == 0:
            return 0.0
        return self.total_processing_time / self.operations_count
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "operations_count": self.operations_count,
            "success_count": self.success_count,
            "error_count": self.error_count,
            "success_rate": self.get_success_rate(),
            "total_processing_time": self.total_processing_time,
            "average_processing_time": self.get_average_processing_time(),
            "created_at": self.created_at.isoformat()
        }


class PlatformTableMapping:
    """平台表映射配置"""
    
    # 平台到表名的映射
    PLATFORM_TABLE_MAPPING = {
        PlatformType.XHS: {
            "content": "xhs_note",
            "comment": "xhs_note_comment", 
            "creator": "xhs_creator"
        },
        PlatformType.DOUYIN: {
            "content": "douyin_aweme",
            "comment": "douyin_aweme_comment",
            "creator": "dy_creator"
        },
        PlatformType.BILIBILI: {
            "content": "bilibili_video", 
            "comment": "bilibili_video_comment",
            "creator": "bilibili_up_info"
        },
        PlatformType.KUAISHOU: {
            "content": "kuaishou_video",
            "comment": "kuaishou_video_comment", 
            "creator": "kuaishou_creator"
        },
        PlatformType.WEIBO: {
            "content": "weibo_note",
            "comment": "weibo_note_comment",
            "creator": "weibo_creator"
        },
        PlatformType.TIEBA: {
            "content": "tieba_note",
            "comment": "tieba_note_comment",
            "creator": "tieba_creator"
        },
        PlatformType.ZHIHU: {
            "content": "zhihu_note", 
            "comment": "zhihu_note_comment",
            "creator": "zhihu_creator"
        }
    }
    
    # 平台主键字段映射
    PLATFORM_PRIMARY_KEY_MAPPING = {
        PlatformType.XHS: {
            "content": "note_id",
            "comment": "comment_id",
            "creator": "user_id"
        },
        PlatformType.DOUYIN: {
            "content": "aweme_id", 
            "comment": "comment_id",
            "creator": "user_id"
        },
        PlatformType.BILIBILI: {
            "content": "video_id",
            "comment": "comment_id", 
            "creator": "user_id"
        },
        PlatformType.KUAISHOU: {
            "content": "video_id",
            "comment": "comment_id",
            "creator": "user_id"
        },
        PlatformType.WEIBO: {
            "content": "weibo_id",
            "comment": "comment_id",
            "creator": "user_id"
        },
        PlatformType.TIEBA: {
            "content": "note_id",
            "comment": "comment_id", 
            "creator": "user_id"
        },
        PlatformType.ZHIHU: {
            "content": "note_id",
            "comment": "comment_id",
            "creator": "user_id"
        }
    }
    
    # 平台评论关联字段映射（评论表中关联内容的字段）
    PLATFORM_COMMENT_RELATION_MAPPING = {
        PlatformType.XHS: "note_id",
        PlatformType.DOUYIN: "aweme_id",
        PlatformType.BILIBILI: "video_id",
        PlatformType.KUAISHOU: "video_id", 
        PlatformType.WEIBO: "weibo_id",
        PlatformType.TIEBA: "note_id",
        PlatformType.ZHIHU: "note_id"
    }
    
    @classmethod
    def get_table_name(cls, platform: PlatformType, data_type: str) -> str:
        """获取平台对应的表名"""
        return cls.PLATFORM_TABLE_MAPPING.get(platform, {}).get(data_type, "")
    
    @classmethod
    def get_primary_key(cls, platform: PlatformType, data_type: str) -> str:
        """获取平台对应的主键字段名"""
        return cls.PLATFORM_PRIMARY_KEY_MAPPING.get(platform, {}).get(data_type, "id")
    
    @classmethod
    def get_comment_relation_field(cls, platform: PlatformType) -> str:
        """获取平台评论关联字段名"""
        return cls.PLATFORM_COMMENT_RELATION_MAPPING.get(platform, "content_id")


class QueryFilter:
    """查询过滤器类"""
    
    def __init__(self):
        self.limit: int = 100
        self.offset: int = 0
        self.task_id: Optional[str] = None
        self.user_id: Optional[str] = None
        self.keyword: Optional[str] = None
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        result = {
            "limit": self.limit,
            "offset": self.offset
        }
        
        if self.task_id:
            result["task_id"] = self.task_id
        if self.user_id:
            result["user_id"] = self.user_id
        if self.keyword:
            result["keyword"] = self.keyword
        if self.start_time:
            result["start_time"] = self.start_time.isoformat()
        if self.end_time:
            result["end_time"] = self.end_time.isoformat()
            
        return result


class BaseDataReader(ABC):
    """数据读取器基础抽象类（只负责读取，不负责写入）"""
    
    def __init__(self, config: DataReaderConfig):
        self.config = config
        self.logger = logging.getLogger(f"{self.__class__.__name__}")
        self.table_mapping = PlatformTableMapping()
        self._initialized = False
        self.metrics = ReaderMetrics()

    @abstractmethod
    async def initialize(self) -> bool:
        """初始化数据读取器"""
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        """健康检查 - 检查数据源是否可用"""
        pass

    @abstractmethod
    async def get_content_list(self, 
                             platform: PlatformType,
                             filters: Optional[QueryFilter] = None) -> DataAccessResult:
        """获取内容列表"""
        pass

    @abstractmethod
    async def get_content_by_id(self,
                              platform: PlatformType, 
                              content_id: str) -> DataAccessResult:
        """根据ID获取单个内容"""
        pass

    @abstractmethod
    async def get_content_count(self,
                              platform: PlatformType,
                              filters: Optional[QueryFilter] = None) -> int:
        """获取内容数量"""
        pass

    @abstractmethod
    async def get_user_content(self,
                             platform: PlatformType,
                             user_id: str,
                             filters: Optional[QueryFilter] = None) -> DataAccessResult:
        """获取用户内容"""
        pass

    @abstractmethod 
    async def search_content(self,
                           platform: PlatformType,
                           keyword: str,
                           filters: Optional[QueryFilter] = None) -> DataAccessResult:
        """搜索内容"""
        pass

    @abstractmethod
    async def get_task_results(self, task_id: str) -> DataAccessResult:
        """获取任务结果"""
        pass

    @abstractmethod
    async def get_platform_stats(self, platform: PlatformType) -> Dict[str, Any]:
        """获取平台统计信息"""
        pass

    async def close(self):
        """关闭数据读取器"""
        self._initialized = False
        self.logger.info(f"{self.__class__.__name__} closed")

    @property
    def initialized(self) -> bool:
        """检查是否已初始化"""
        return self._initialized

    def _validate_platform(self, platform: PlatformType) -> bool:
        """验证平台类型"""
        return isinstance(platform, PlatformType)

    def _build_error_result(self, message: str) -> DataAccessResult:
        """构建错误结果"""
        return DataAccessResult(success=False, message=message) 