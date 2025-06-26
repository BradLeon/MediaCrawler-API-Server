"""
数据读取器模块
提供统一的数据读取接口，支持多种数据源（JSON、CSV、数据库）
注意：此模块只负责数据读取，不负责数据写入
"""

from .base import (
    BaseDataReader,
    DataAccessResult,
    DataReaderConfig,
    DataSourceType,
    PlatformType,
    QueryFilter,
    ReaderMetrics
)
from .factory import DataReaderFactory
from .json_reader import JsonDataReader
from .csv_reader import CsvDataReader
from .supabase_reader import SupabaseDataReader

__all__ = [
    # 基础类
    "BaseDataReader",
    "DataAccessResult", 
    "DataReaderConfig",
    "DataSourceType",
    "PlatformType",
    "QueryFilter",
    "ReaderMetrics",
    
    # 工厂类
    "DataReaderFactory",
    
    # 读取器实现
    "JsonDataReader",
    "CsvDataReader", 
    "SupabaseDataReader"
] 