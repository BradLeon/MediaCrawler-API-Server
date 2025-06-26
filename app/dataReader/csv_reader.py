"""
CSV数据读取器
从CSV文件中读取MediaCrawler爬取的数据
注意：此类只负责数据读取，不负责数据写入
"""
import csv
import os
import pathlib
import logging
import asyncio
from datetime import datetime
from typing import Dict, List, Any, Optional
import aiofiles

from app.dataReader.base import BaseDataReader, DataAccessResult, DataReaderConfig, PlatformType, ReaderMetrics, QueryFilter

logger = logging.getLogger(__name__)


def calculate_number_of_files(file_path: str) -> int:
    """计算目录中的文件数量"""
    try:
        if os.path.exists(file_path):
            return len([f for f in os.listdir(file_path) if os.path.isfile(os.path.join(file_path, f))])
        return 0
    except Exception:
        return 0


class CsvDataReader(BaseDataReader):
    """CSV数据读取器"""
    
    def __init__(self, config: DataReaderConfig):
        super().__init__(config)
        
        # 根据平台设置存储路径
        base_path = self._get_platform_base_path()
        self.csv_store_path = f"{base_path}/csv"
        self.file_count = calculate_number_of_files(self.csv_store_path)
    
    def _get_platform_base_path(self) -> str:
        """获取平台对应的基础存储路径"""
        base_path = self.config.file_path or "data"
        platform_name = self.config.platform.value
        return f"{base_path}/{platform_name}"
    
    async def initialize(self) -> bool:
        """初始化CSV读取器"""
        try:
            # 检查路径是否存在
            if not os.path.exists(self.csv_store_path):
                logger.warning(f"CSV storage path does not exist: {self.csv_store_path}")
                # 创建目录以便后续使用
                pathlib.Path(self.csv_store_path).mkdir(parents=True, exist_ok=True)
            
            self._initialized = True
            logger.info(f"CSV reader initialized at: {self.csv_store_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize CSV reader: {e}")
            return False
    
    async def health_check(self) -> bool:
        """健康检查"""
        try:
            return os.path.exists(self.csv_store_path) and os.access(self.csv_store_path, os.R_OK)
        except Exception as e:
            logger.error(f"CSV reader health check failed: {e}")
            return False
    
    # 由于CSV文件特性，以下方法都返回"不支持"的错误
    async def get_content_list(self, 
                             platform: PlatformType,
                             filters: Optional[QueryFilter] = None) -> DataAccessResult:
        """获取内容列表 - CSV存储不支持复杂查询"""
        return DataAccessResult(False, message="CSV storage does not support querying operations")
    
    async def get_content_by_id(self,
                              platform: PlatformType, 
                              content_id: str) -> DataAccessResult:
        """根据ID获取单个内容 - CSV存储不支持复杂查询"""
        return DataAccessResult(False, message="CSV storage does not support querying operations")
    
    async def get_content_count(self,
                              platform: PlatformType,
                              filters: Optional[QueryFilter] = None) -> int:
        """获取内容数量 - CSV存储不支持复杂查询"""
        return 0
    
    async def get_user_content(self,
                             platform: PlatformType,
                             user_id: str,
                             filters: Optional[QueryFilter] = None) -> DataAccessResult:
        """获取用户内容 - CSV存储不支持复杂查询"""
        return DataAccessResult(False, message="CSV storage does not support querying operations")
    
    async def search_content(self,
                           platform: PlatformType,
                           keyword: str,
                           filters: Optional[QueryFilter] = None) -> DataAccessResult:
        """搜索内容 - CSV存储不支持复杂查询"""
        return DataAccessResult(False, message="CSV storage does not support querying operations")
    
    async def get_task_results(self, task_id: str) -> DataAccessResult:
        """获取任务结果 - CSV存储不支持复杂查询"""
        return DataAccessResult(False, message="CSV storage does not support querying operations")
    
    async def get_platform_stats(self, platform: PlatformType) -> Dict[str, Any]:
        """获取平台统计信息"""
        try:
            # 统计CSV文件信息
            stats = {
                "platform": platform.value,
                "storage_type": "csv",
                "csv_files_count": self.file_count,
                "storage_path": self.csv_store_path
            }
            
            # 计算文件总大小
            total_size = 0
            if os.path.exists(self.csv_store_path):
                for filename in os.listdir(self.csv_store_path):
                    file_path = os.path.join(self.csv_store_path, filename)
                    if os.path.isfile(file_path):
                        total_size += os.path.getsize(file_path)
            
            stats["total_size_mb"] = round(total_size / (1024 * 1024), 2)
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get platform stats: {e}")
            return {} 