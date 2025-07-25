"""
数据读取器工厂
负责创建和管理不同类型的数据读取器实例
"""
import logging
from typing import Dict, Optional

from .base import DataSourceType, BaseDataReader, DataReaderConfig, PlatformType
from .json_reader import JsonDataReader
from .csv_reader import CsvDataReader  
from .supabase_reader import SupabaseDataReader
from app.core.config_manager import get_config_manager, StorageConfig

logger = logging.getLogger(__name__)


class DataReaderFactory:
    """数据读取器工厂类"""
    
    _instances: Dict[str, BaseDataReader] = {}
    
    @classmethod
    async def create_data_reader(cls, source_type: DataSourceType, platform: PlatformType, file_path: str = None) -> BaseDataReader:
        """创建数据读取器"""
        try:
            # 🎯 使用新的基于模型的配置管理
            config_manager = get_config_manager()
            storage_config: StorageConfig = config_manager.build_storage_config(
                source_type=source_type.value,
                platform=platform.value
            )
            
            # 创建DataReaderConfig (兼容现有的读取器接口)
            reader_config = DataReaderConfig(
                source_type=source_type,
                platform=platform,
                file_path=file_path or storage_config.base_path or "data"
            )
            
            # 创建对应的读取器
            if source_type == DataSourceType.JSON:
                from app.dataReader.json_reader import JsonDataReader
                reader = JsonDataReader(reader_config)
            elif source_type == DataSourceType.CSV:
                from app.dataReader.csv_reader import CsvDataReader
                reader = CsvDataReader(reader_config)
            elif source_type == DataSourceType.DATABASE:
                from app.dataReader.supabase_reader import SupabaseDataReader
                reader = SupabaseDataReader(reader_config)
            else:
                raise ValueError(f"Unsupported source type: {source_type}")
            
            # 初始化读取器
            await reader.initialize()
            
            logger.info(f"Created data reader for {source_type.value}_{platform.value} with StorageConfig")
            return reader
            
        except Exception as e:
            logger.error(f"Failed to create data reader: {e}")
            raise
    
    @classmethod
    def _get_reader_class(cls, source_type: DataSourceType):
        """获取读取器类"""
        reader_mapping = {
            DataSourceType.JSON: JsonDataReader,
            DataSourceType.CSV: CsvDataReader,
            DataSourceType.DATABASE: SupabaseDataReader,
        }
        return reader_mapping.get(source_type)
    
    @classmethod
    async def get_reader(cls, 
                        source_type: DataSourceType,
                        platform: PlatformType = PlatformType.XHS) -> Optional[BaseDataReader]:
        """
        获取读取器实例（便捷方法）
        
        Args:
            source_type: 数据源类型
            platform: 平台类型
            
        Returns:
            数据读取器实例
        """
        return await cls.create_data_reader(source_type, platform)
    
    @classmethod
    async def close_all(cls):
        """关闭所有读取器实例"""
        try:
            for instance in cls._instances.values():
                await instance.close()
            cls._instances.clear()
            logger.info("All data readers closed")
        except Exception as e:
            logger.error(f"Failed to close data readers: {e}")
    
    @classmethod
    def get_available_types(cls) -> list:
        """获取可用的数据源类型"""
        return [source_type.value for source_type in DataSourceType]
    
    @classmethod
    async def health_check_all(cls) -> Dict[str, bool]:
        """检查所有实例的健康状态"""
        results = {}
        for key, instance in cls._instances.items():
            try:
                results[key] = await instance.health_check()
            except Exception as e:
                logger.error(f"Health check failed for {key}: {e}")
                results[key] = False
        return results 