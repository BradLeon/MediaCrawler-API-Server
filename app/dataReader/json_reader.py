"""
JSON数据读取器
从JSON文件中读取MediaCrawler爬取的数据
注意：此类只负责数据读取，不负责数据写入
"""
import json
import os
import pathlib
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional

from .base import (
    BaseDataReader, 
    DataAccessResult, 
    DataReaderConfig,
    QueryFilter, 
    PlatformType,
    ReaderMetrics
)

logger = logging.getLogger(__name__)


def calculate_number_of_files(file_path: str) -> int:
    """计算目录中的文件数量"""
    try:
        if os.path.exists(file_path):
            return len([f for f in os.listdir(file_path) if os.path.isfile(os.path.join(file_path, f))])
        return 0
    except Exception:
        return 0


class JsonDataReader(BaseDataReader):
    """JSON数据读取器"""
    
    def __init__(self, config: DataReaderConfig):
        super().__init__(config)
        
        # 根据平台设置存储路径
        base_path = self._get_platform_base_path()
        self.json_store_path = f"{base_path}/json"
        self.words_store_path = f"{base_path}/words"  # 预留词云功能
        
        self.file_count = calculate_number_of_files(self.json_store_path)
    
    def _get_platform_base_path(self) -> str:
        """获取平台对应的基础存储路径"""
        base_path = self.config.file_path or "data"
        platform_name = self.config.platform.value
        return f"{base_path}/{platform_name}"
    
    async def initialize(self) -> bool:
        """初始化JSON读取器"""
        try:
            # 检查路径是否存在
            if not os.path.exists(self.json_store_path):
                logger.warning(f"JSON storage path does not exist: {self.json_store_path}")
                # 创建目录以便后续使用
                pathlib.Path(self.json_store_path).mkdir(parents=True, exist_ok=True)
                pathlib.Path(self.words_store_path).mkdir(parents=True, exist_ok=True)
            
            self._initialized = True
            logger.info(f"JSON reader initialized at: {self.json_store_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize JSON reader: {e}")
            return False
    
    async def health_check(self) -> bool:
        """健康检查"""
        try:
            return os.path.exists(self.json_store_path) and os.access(self.json_store_path, os.R_OK)
        except Exception as e:
            logger.error(f"JSON reader health check failed: {e}")
            return False
    
    async def get_content_list(self, 
                             platform: PlatformType,
                             filters: Optional[QueryFilter] = None) -> DataAccessResult:
        """获取内容列表"""
        try:
            # 读取所有内容文件
            content_files = self._find_content_files("contents")
            all_data = []
            
            for file_path in content_files:
                try:
                    data = self._read_json_file(file_path)
                    if isinstance(data, list):
                        all_data.extend(data)
                    elif isinstance(data, dict):
                        all_data.append(data)
                except Exception as e:
                    logger.warning(f"Failed to read file {file_path}: {e}")
            
            # 应用过滤器
            filtered_data = self._apply_filters(all_data, filters)
            
            # 分页
            if filters:
                start_idx = filters.offset
                end_idx = start_idx + filters.limit
                paginated_data = filtered_data[start_idx:end_idx]
            else:
                paginated_data = filtered_data[:100]  # 默认返回前100条
            
            return DataAccessResult(
                success=True,
                data=paginated_data,
                total=len(filtered_data),
                message="Content list retrieved successfully from JSON files"
            )
            
        except Exception as e:
            logger.error(f"Failed to get content list from JSON: {e}")
            return DataAccessResult(False, message=f"Failed to get content list: {str(e)}", error=e)
    
    async def get_content_by_id(self,
                              platform: PlatformType, 
                              content_id: str) -> DataAccessResult:
        """根据ID获取单个内容"""
        try:
            content_files = self._find_content_files("contents")
            
            for file_path in content_files:
                try:
                    data = self._read_json_file(file_path)
                    items = data if isinstance(data, list) else [data]
                    
                    # 根据平台确定主键字段
                    primary_key = self.table_mapping.get_primary_key(platform, "content")
                    
                    for item in items:
                        if isinstance(item, dict) and item.get(primary_key) == content_id:
                            return DataAccessResult(
                                success=True,
                                data=item,
                                total=1,
                                message="Content found successfully"
                            )
                            
                except Exception as e:
                    logger.warning(f"Failed to read file {file_path}: {e}")
            
            return DataAccessResult(False, message="Content not found")
            
        except Exception as e:
            logger.error(f"Failed to get content by ID from JSON: {e}")
            return DataAccessResult(False, message=f"Failed to get content: {str(e)}", error=e)
    
    async def get_content_count(self,
                              platform: PlatformType,
                              filters: Optional[QueryFilter] = None) -> int:
        """获取内容数量"""
        try:
            content_files = self._find_content_files("contents")
            all_data = []
            
            for file_path in content_files:
                try:
                    data = self._read_json_file(file_path)
                    if isinstance(data, list):
                        all_data.extend(data)
                    elif isinstance(data, dict):
                        all_data.append(data)
                except Exception as e:
                    logger.warning(f"Failed to read file {file_path}: {e}")
            
            # 应用过滤器
            filtered_data = self._apply_filters(all_data, filters)
            return len(filtered_data)
            
        except Exception as e:
            logger.error(f"Failed to get content count from JSON: {e}")
            return 0
    
    async def get_user_content(self,
                             platform: PlatformType,
                             user_id: str,
                             filters: Optional[QueryFilter] = None) -> DataAccessResult:
        """获取用户内容"""
        try:
            # 创建包含user_id过滤条件的新过滤器
            if not filters:
                filters = QueryFilter()
            filters.user_id = user_id
            
            return await self.get_content_list(platform, filters)
            
        except Exception as e:
            logger.error(f"Failed to get user content from JSON: {e}")
            return DataAccessResult(False, message=f"Failed to get user content: {str(e)}", error=e)
    
    async def search_content(self,
                           platform: PlatformType,
                           keyword: str,
                           filters: Optional[QueryFilter] = None) -> DataAccessResult:
        """搜索内容"""
        try:
            # 创建包含keyword过滤条件的新过滤器
            if not filters:
                filters = QueryFilter()
            filters.keyword = keyword
            
            return await self.get_content_list(platform, filters)
            
        except Exception as e:
            logger.error(f"Failed to search content in JSON: {e}")
            return DataAccessResult(False, message=f"Failed to search content: {str(e)}", error=e)
    
    async def get_task_results(self, task_id: str) -> DataAccessResult:
        """获取任务结果"""
        try:
            # 创建包含task_id过滤条件的新过滤器
            filters = QueryFilter()
            filters.task_id = task_id
            
            return await self.get_content_list(self.config.platform, filters)
            
        except Exception as e:
            logger.error(f"Failed to get task results from JSON: {e}")
            return DataAccessResult(False, message=f"Failed to get task results: {str(e)}", error=e)
    
    async def get_platform_stats(self, platform: PlatformType) -> Dict[str, Any]:
        """获取平台统计信息"""
        try:
            # 统计各类型文件数量
            content_count = await self.get_content_count(platform)
            
            # 统计文件数
            content_files = len(self._find_content_files("contents"))
            comment_files = len(self._find_content_files("comments"))
            creator_files = len(self._find_content_files("creator"))
            
            return {
                "total_content": content_count,
                "content_files": content_files,
                "comment_files": comment_files,
                "creator_files": creator_files,
                "platform": platform.value,
                "storage_path": self.json_store_path
            }
            
        except Exception as e:
            logger.error(f"Failed to get platform stats from JSON: {e}")
            return {}
    
    def _find_content_files(self, content_type: str) -> List[str]:
        """查找指定类型的JSON文件"""
        try:
            if not os.path.exists(self.json_store_path):
                return []
            
            files = []
            for filename in os.listdir(self.json_store_path):
                if filename.endswith('.json') and content_type in filename:
                    files.append(os.path.join(self.json_store_path, filename))
            
            return sorted(files)  # 按文件名排序
            
        except Exception as e:
            logger.error(f"Failed to find content files: {e}")
            return []
    
    def _read_json_file(self, file_path: str) -> Any:
        """读取JSON文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to read JSON file {file_path}: {e}")
            return []
    
    def _apply_filters(self, data: List[Dict], filters: Optional[QueryFilter]) -> List[Dict]:
        """应用查询过滤器"""
        if not filters:
            return data
        
        filtered_data = []
        
        for item in data:
            if not isinstance(item, dict):
                continue
            
            # 应用各种过滤条件
            if filters.task_id and item.get("task_id") != filters.task_id:
                continue
            
            if filters.user_id and item.get("user_id") != filters.user_id:
                continue
            
            if filters.keyword:
                # 在标题和描述中搜索关键词
                title = str(item.get("title", "")).lower()
                desc = str(item.get("desc", "")).lower()
                keyword = filters.keyword.lower()
                
                if keyword not in title and keyword not in desc:
                    continue
            
            # 时间过滤（如果有时间字段）
            if filters.start_time or filters.end_time:
                item_time = self._parse_item_time(item)
                if item_time:
                    if filters.start_time and item_time < filters.start_time:
                        continue
                    if filters.end_time and item_time > filters.end_time:
                        continue
            
            filtered_data.append(item)
        
        return filtered_data
    
    def _parse_item_time(self, item: Dict) -> Optional[datetime]:
        """解析条目的时间字段"""
        try:
            # 尝试不同的时间字段
            for time_field in ["created_at", "publish_time", "last_update_time", "add_ts"]:
                if time_field in item:
                    time_value = item[time_field]
                    
                    if isinstance(time_value, (int, float)):
                        # 时间戳（可能是毫秒）
                        if time_value > 1e10:  # 毫秒时间戳
                            return datetime.fromtimestamp(time_value / 1000)
                        else:  # 秒时间戳
                            return datetime.fromtimestamp(time_value)
                    
                    elif isinstance(time_value, str):
                        # ISO格式时间字符串
                        try:
                            return datetime.fromisoformat(time_value.replace('Z', '+00:00'))
                        except:
                            pass
            
            return None
            
        except Exception as e:
            logger.warning(f"Failed to parse item time: {e}")
            return None
    
    async def close(self):
        """关闭读取器"""
        await super().close()
        logger.info("JSON reader closed") 