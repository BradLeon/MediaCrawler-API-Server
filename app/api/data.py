"""
数据查询API
提供爬取数据的查询接口
"""
from fastapi import APIRouter, HTTPException, Query, Path
from typing import Dict, Any, List, Optional
import logging

from app.dataReader.factory import DataReaderFactory
from app.dataReader.base import DataSourceType, PlatformType, QueryFilter
from app.core.config_manager import get_config_manager, AppConfig

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/health")
async def health_check():
    """健康检查"""
    try:
        # 检查各种数据源的健康状态
        health_results = await DataReaderFactory.health_check_all()
        
        # 检查配置管理器
        config_manager = get_config_manager()
        app_config: AppConfig = config_manager.get_app_config()
        
        return {
            "status": "healthy",
            "data_sources": health_results,
            "app_version": app_config.version,
            "supported_platforms": len(config_manager.get_supported_platforms())
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")


@router.get("/platforms")
async def get_platforms():
    """获取支持的平台列表"""
    try:
        config_manager = get_config_manager()
        platforms = config_manager.get_supported_platforms()
        
        return {
            "platforms": [platform.dict() for platform in platforms],
            "total": len(platforms)
        }
    except Exception as e:
        logger.error(f"Failed to get platforms: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get platforms: {str(e)}")


@router.get("/content/{platform}")
async def get_content_list(
    platform: str = Path(..., description="平台名称"),
    source_type: str = Query("json", description="数据源类型"),
    limit: int = Query(20, description="返回数量限制"),
    offset: int = Query(0, description="偏移量"),
    task_id: Optional[str] = Query(None, description="任务ID过滤"),
    user_id: Optional[str] = Query(None, description="用户ID过滤"),
    keyword: Optional[str] = Query(None, description="关键词搜索")
):
    """获取内容列表"""
    try:
        # 验证平台
        config_manager = get_config_manager()
        supported_platforms = config_manager.get_supported_platforms()
        if not any(p.key == platform for p in supported_platforms):
            raise HTTPException(status_code=400, detail=f"不支持的平台: {platform}")
        
        # 验证数据源类型
        try:
            data_source = DataSourceType(source_type)
            platform_type = PlatformType(platform)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=f"无效的参数: {str(e)}")
        
        # 创建数据读取器
        reader = await DataReaderFactory.get_reader(data_source, platform_type)
        if not reader:
            raise HTTPException(status_code=500, detail=f"无法创建{source_type}数据读取器")
        
        # 创建查询过滤器
        filters = QueryFilter(
            limit=limit,
            offset=offset,
            task_id=task_id,
            user_id=user_id,
            keyword=keyword
        )
        
        # 查询数据
        result = await reader.get_content_list(platform_type, filters)
        
        if not result.success:
            raise HTTPException(status_code=500, detail=result.message)
        
        return {
            "data": result.data,
            "total": result.total,
            "limit": limit,
            "offset": offset,
            "platform": platform,
            "source_type": source_type,
            "message": result.message
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get content list: {e}")
        raise HTTPException(status_code=500, detail=f"获取内容列表失败: {str(e)}")


@router.get("/content/{platform}/{content_id}")
async def get_content_detail(
    platform: str = Path(..., description="平台名称"),
    content_id: str = Path(..., description="内容ID"),
    source_type: str = Query("json", description="数据源类型")
):
    """获取单个内容详情"""
    try:
        # 验证参数
        try:
            data_source = DataSourceType(source_type)
            platform_type = PlatformType(platform)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=f"无效的参数: {str(e)}")
        
        # 创建数据读取器
        reader = await DataReaderFactory.get_reader(data_source, platform_type)
        if not reader:
            raise HTTPException(status_code=500, detail=f"无法创建{source_type}数据读取器")
        
        # 查询数据
        result = await reader.get_content_by_id(platform_type, content_id)
        
        if not result.success:
            if "not found" in result.message.lower():
                raise HTTPException(status_code=404, detail="内容不存在")
            else:
                raise HTTPException(status_code=500, detail=result.message)
        
        return {
            "data": result.data,
            "platform": platform,
            "content_id": content_id,
            "source_type": source_type,
            "message": result.message
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get content detail: {e}")
        raise HTTPException(status_code=500, detail=f"获取内容详情失败: {str(e)}")


@router.get("/user/{platform}/{user_id}/content")
async def get_user_content(
    platform: str = Path(..., description="平台名称"),
    user_id: str = Path(..., description="用户ID"),
    source_type: str = Query("json", description="数据源类型"),
    limit: int = Query(20, description="返回数量限制"),
    offset: int = Query(0, description="偏移量")
):
    """获取用户内容"""
    try:
        # 验证参数
        try:
            data_source = DataSourceType(source_type)
            platform_type = PlatformType(platform)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=f"无效的参数: {str(e)}")
        
        # 创建数据读取器
        reader = await DataReaderFactory.get_reader(data_source, platform_type)
        if not reader:
            raise HTTPException(status_code=500, detail=f"无法创建{source_type}数据读取器")
        
        # 创建查询过滤器
        filters = QueryFilter(
            limit=limit,
            offset=offset,
            user_id=user_id
        )
        
        # 查询数据
        result = await reader.get_user_content(platform_type, user_id, filters)
        
        if not result.success:
            raise HTTPException(status_code=500, detail=result.message)
        
        return {
            "data": result.data,
            "total": result.total,
            "limit": limit,
            "offset": offset,
            "platform": platform,
            "user_id": user_id,
            "source_type": source_type,
            "message": result.message
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get user content: {e}")
        raise HTTPException(status_code=500, detail=f"获取用户内容失败: {str(e)}")


@router.get("/search/{platform}")
async def search_content(
    platform: str = Path(..., description="平台名称"),
    keyword: str = Query(..., description="搜索关键词"),
    source_type: str = Query("json", description="数据源类型"),
    limit: int = Query(20, description="返回数量限制"),
    offset: int = Query(0, description="偏移量")
):
    """搜索内容"""
    try:
        # 验证参数
        try:
            data_source = DataSourceType(source_type)
            platform_type = PlatformType(platform)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=f"无效的参数: {str(e)}")
        
        # 创建数据读取器
        reader = await DataReaderFactory.get_reader(data_source, platform_type)
        if not reader:
            raise HTTPException(status_code=500, detail=f"无法创建{source_type}数据读取器")
        
        # 创建查询过滤器
        filters = QueryFilter(
            limit=limit,
            offset=offset,
            keyword=keyword
        )
        
        # 搜索数据
        result = await reader.search_content(platform_type, keyword, filters)
        
        if not result.success:
            raise HTTPException(status_code=500, detail=result.message)
        
        return {
            "data": result.data,
            "total": result.total,
            "limit": limit,
            "offset": offset,
            "platform": platform,
            "keyword": keyword,
            "source_type": source_type,
            "message": result.message
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to search content: {e}")
        raise HTTPException(status_code=500, detail=f"搜索内容失败: {str(e)}")


@router.get("/task/{task_id}/results")
async def get_task_results(
    task_id: str = Path(..., description="任务ID"),
    source_type: str = Query("json", description="数据源类型"),
    platform: str = Query("xhs", description="平台名称")
):
    """获取任务结果"""
    try:
        # 验证参数
        try:
            data_source = DataSourceType(source_type)
            platform_type = PlatformType(platform)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=f"无效的参数: {str(e)}")
        
        # 创建数据读取器
        reader = await DataReaderFactory.get_reader(data_source, platform_type)
        if not reader:
            raise HTTPException(status_code=500, detail=f"无法创建{source_type}数据读取器")
        
        # 查询任务结果
        result = await reader.get_task_results(task_id)
        
        if not result.success:
            raise HTTPException(status_code=500, detail=result.message)
        
        return {
            "data": result.data,
            "total": result.total,
            "task_id": task_id,
            "platform": platform,
            "source_type": source_type,
            "message": result.message
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get task results: {e}")
        raise HTTPException(status_code=500, detail=f"获取任务结果失败: {str(e)}")


@router.get("/stats/{platform}")
async def get_platform_stats(
    platform: str = Path(..., description="平台名称"),
    source_type: str = Query("json", description="数据源类型")
):
    """获取平台统计信息"""
    try:
        # 验证参数
        try:
            data_source = DataSourceType(source_type)
            platform_type = PlatformType(platform)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=f"无效的参数: {str(e)}")
        
        # 创建数据读取器
        reader = await DataReaderFactory.get_reader(data_source, platform_type)
        if not reader:
            raise HTTPException(status_code=500, detail=f"无法创建{source_type}数据读取器")
        
        # 获取统计信息
        stats = await reader.get_platform_stats(platform_type)
        
        return {
            "stats": stats,
            "platform": platform,
            "source_type": source_type
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get platform stats: {e}")
        raise HTTPException(status_code=500, detail=f"获取平台统计失败: {str(e)}")


@router.get("/sources")
async def get_data_sources():
    """获取可用的数据源类型"""
    try:
        available_types = DataReaderFactory.get_available_types()
        health_status = await DataReaderFactory.health_check_all()
        
        sources = []
        for source_type in available_types:
            sources.append({
                "type": source_type,
                "name": source_type.upper(),
                "healthy": any(source_type in key and status for key, status in health_status.items()),
                "description": f"{source_type.upper()} 数据存储"
            })
        
        return {
            "sources": sources,
            "total": len(sources)
        }
        
    except Exception as e:
        logger.error(f"Failed to get data sources: {e}")
        raise HTTPException(status_code=500, detail=f"获取数据源失败: {str(e)}") 