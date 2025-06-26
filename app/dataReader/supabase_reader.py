"""
Supabase数据读取器
只负责从Supabase数据库中读取数据，不负责写入
"""
from typing import Dict, List, Any, Optional
import asyncio
from datetime import datetime
import pytz
import logging

from gotrue.errors import AuthError
from supabase import create_client, Client

from app.core.database import get_supabase_client, check_supabase_connection
from app.core.config import get_settings
from .base import (
    BaseDataReader, 
    DataAccessResult, 
    DataReaderConfig,
    QueryFilter, 
    PlatformType,
    ReaderMetrics
)

logger = logging.getLogger(__name__)


class SupabaseDataReader(BaseDataReader):
    """Supabase数据读取器"""
    
    def __init__(self, config: DataReaderConfig):
        super().__init__(config)
        self.client: Optional[Client] = None
        self.settings = get_settings()
        
    async def initialize(self) -> bool:
        """初始化Supabase连接"""
        try:
            # 检查配置
            if not self.settings.supabase_url or not self.settings.supabase_key:
                logger.warning("Supabase URL or key not configured")
                return False
            
            # 创建客户端
            self.client = get_supabase_client()
            if not self.client:
                logger.error("Failed to create Supabase client")
                return False
            
            # 测试连接
            await self._test_connection()
            self._initialized = True
            logger.info(f"Supabase reader initialized for platform: {self.config.platform.value}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize Supabase reader: {e}")
            return False
    
    async def _test_connection(self):
        """测试数据库连接"""
        if not await check_supabase_connection():
            raise Exception("Supabase connection test failed")
    
    async def health_check(self) -> bool:
        """健康检查"""
        try:
            if not self.client:
                return False
            
            # 简单查询测试连接
            table_name = self.get_table_name("content")
            response = self.client.table(table_name).select("*").limit(1).execute()
            return response is not None
            
        except Exception as e:
            logger.error(f"Supabase health check failed: {e}")
            return False
    
    async def get_content_list(self, 
                             platform: PlatformType,
                             filters: Optional[QueryFilter] = None) -> DataAccessResult:
        """获取内容列表"""
        try:
            if not self.client:
                return DataAccessResult(False, message="Supabase client not initialized")
            
            table_name = self.get_table_name("content")
            query = self.client.table(table_name).select("*")
            
            # 应用过滤器
            if filters:
                query = self._apply_filters(query, filters)
            else:
                query = query.limit(100)
            
            response = query.execute()
            
            return DataAccessResult(
                success=True,
                data=response.data,
                total=len(response.data),
                message="Content list retrieved successfully"
            )
            
        except Exception as e:
            logger.error(f"Failed to get content list: {e}")
            return DataAccessResult(False, message=f"Failed to get content list: {str(e)}", error=e)
    
    async def get_content_by_id(self,
                              platform: PlatformType, 
                              content_id: str) -> DataAccessResult:
        """根据ID获取单个内容"""
        try:
            if not self.client:
                return DataAccessResult(False, message="Supabase client not initialized")
            
            table_name = self.get_table_name("content")
            primary_key = self.get_primary_key_field("content")
            
            response = self.client.table(table_name).select("*").eq(primary_key, content_id).execute()
            
            if response.data:
                return DataAccessResult(
                    success=True,
                    data=response.data[0],
                    total=1,
                    message="Content retrieved successfully"
                )
            else:
                return DataAccessResult(False, message="Content not found")
                
        except Exception as e:
            logger.error(f"Failed to get content by ID: {e}")
            return DataAccessResult(False, message=f"Failed to get content: {str(e)}", error=e)
    
    async def get_content_count(self,
                              platform: PlatformType,
                              filters: Optional[QueryFilter] = None) -> int:
        """获取内容数量"""
        try:
            if not self.client:
                return 0
            
            table_name = self.get_table_name("content")
            query = self.client.table(table_name).select("*", count="exact")
            
            # 应用过滤器（不包括limit和offset）
            if filters:
                query = self._apply_filters(query, filters, include_pagination=False)
            
            response = query.execute()
            return response.count or 0
            
        except Exception as e:
            logger.error(f"Failed to get content count: {e}")
            return 0
    
    async def get_user_content(self,
                             platform: PlatformType,
                             user_id: str,
                             filters: Optional[QueryFilter] = None) -> DataAccessResult:
        """获取用户内容"""
        try:
            if not self.client:
                return DataAccessResult(False, message="Supabase client not initialized")
            
            table_name = self.get_table_name("content")
            query = self.client.table(table_name).select("*").eq("user_id", user_id)
            
            # 应用其他过滤器
            if filters:
                query = self._apply_filters(query, filters)
            else:
                query = query.limit(100)
            
            response = query.execute()
            
            return DataAccessResult(
                success=True,
                data=response.data,
                total=len(response.data),
                message="User content retrieved successfully"
            )
            
        except Exception as e:
            logger.error(f"Failed to get user content: {e}")
            return DataAccessResult(False, message=f"Failed to get user content: {str(e)}", error=e)
    
    async def search_content(self,
                           platform: PlatformType,
                           keyword: str,
                           filters: Optional[QueryFilter] = None) -> DataAccessResult:
        """搜索内容"""
        try:
            if not self.client:
                return DataAccessResult(False, message="Supabase client not initialized")
            
            table_name = self.get_table_name("content")
            
            # 在标题、描述等字段中搜索关键词
            query = self.client.table(table_name).select("*").or_(
                f"title.ilike.%{keyword}%,desc.ilike.%{keyword}%"
            )
            
            # 应用其他过滤器
            if filters:
                query = self._apply_filters(query, filters)
            else:
                query = query.limit(100)
            
            response = query.execute()
            
            return DataAccessResult(
                success=True,
                data=response.data,
                total=len(response.data),
                message="Content search completed successfully"
            )
            
        except Exception as e:
            logger.error(f"Failed to search content: {e}")
            return DataAccessResult(False, message=f"Failed to search content: {str(e)}", error=e)
    
    async def get_task_results(self, task_id: str) -> DataAccessResult:
        """获取任务结果"""
        try:
            if not self.client:
                return DataAccessResult(False, message="Supabase client not initialized")
            
            table_name = self.get_table_name("content")
            
            response = self.client.table(table_name).select("*").eq("task_id", task_id).execute()
            
            return DataAccessResult(
                success=True,
                data=response.data,
                total=len(response.data),
                message="Task results retrieved successfully"
            )
            
        except Exception as e:
            logger.error(f"Failed to get task results: {e}")
            return DataAccessResult(False, message=f"Failed to get task results: {str(e)}", error=e)
    
    async def get_platform_stats(self, platform: PlatformType) -> Dict[str, Any]:
        """获取平台统计信息"""
        try:
            if not self.client:
                return {}
            
            table_name = self.get_table_name("content")
            
            # 获取总数
            total_response = self.client.table(table_name).select("*", count="exact").execute()
            
            # 获取今日数据数量
            today = datetime.now().date()
            today_response = self.client.table(table_name).select("*", count="exact").gte(
                "created_at", today.isoformat()
            ).execute()
            
            return {
                "total_content": total_response.count or 0,
                "today_content": today_response.count or 0,
                "platform": platform.value
            }
            
        except Exception as e:
            logger.error(f"Failed to get platform stats: {e}")
            return {}
    
    def _apply_filters(self, query, filters: QueryFilter, include_pagination: bool = True):
        """应用查询过滤器"""
        if filters.task_id:
            query = query.eq("task_id", filters.task_id)
        if filters.user_id:
            query = query.eq("user_id", filters.user_id)
        if filters.start_time:
            query = query.gte("created_at", filters.start_time.isoformat())
        if filters.end_time:
            query = query.lte("created_at", filters.end_time.isoformat())
        
        if include_pagination:
            query = query.range(filters.offset, filters.offset + filters.limit - 1)
        
        return query
    
    def get_table_name(self, data_type: str) -> str:
        """获取数据类型对应的表名"""
        return self.table_mapping.get_table_name(self.config.platform, data_type)
    
    def get_primary_key_field(self, data_type: str) -> str:
        """获取数据类型对应的主键字段名"""
        return self.table_mapping.get_primary_key(self.config.platform, data_type)
    
    async def close(self):
        """关闭连接"""
        self.client = None
        await super().close()
        logger.info("Supabase reader closed")
 