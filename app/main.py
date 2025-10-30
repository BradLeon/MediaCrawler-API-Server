"""
MediaCrawler API Server

基于原MediaCrawler项目的FastAPI服务，
通过适配器模式复用原有的爬虫功能。
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import uuid
import logging

from app.crawler.adapter import (
    crawler_adapter, 
    CrawlerTask, 
    CrawlerTaskType,
    CrawlerResult
)
from app.dataReader.base import PlatformType
from app.core.config_manager import CrawlerConfigRequest, get_config_manager
from app.core.logging import logging_manager
from app.api.login import router as login_router
from app.api.data import router as data_router
from app.dataReader.factory import DataReaderFactory
from app.dataReader.base import DataSourceType

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="MediaCrawler API Server",
    description="基于MediaCrawler的社交媒体数据采集API服务",
    version="1.0.0"
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(login_router)
app.include_router(data_router)


# 应用生命周期事件
@app.on_event("startup")
async def startup_event():
    """应用启动时初始化"""
    logger.info("Initializing MediaCrawler API Server...")
    
    # 初始化数据访问管理器
    try:
        # 预热数据读取器（创建一个默认实例）
        await DataReaderFactory.create_data_reader(DataSourceType.JSON, PlatformType.XHS)
        logger.info("Data access manager initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize data access manager: {e}")
        # 不阻止应用启动，允许降级服务
    
    logger.info("MediaCrawler API Server startup complete")


@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭时清理"""
    logger.info("Shutting down MediaCrawler API Server...")
    
    try:
        await DataReaderFactory.close_all()
        logger.info("Data access manager closed successfully")
    except Exception as e:
        logger.error(f"Error during data access manager shutdown: {e}")
    
    logger.info("MediaCrawler API Server shutdown complete")


# Pydantic模型定义
class CrawlerTaskRequest(BaseModel):
    """爬虫任务请求"""
    platform: str = Field(..., description="平台名称(xhs, dy, ks, bili, wb, zhihu, tieba)")
    task_type: str = Field(..., description="任务类型(search, detail, creator)")
    keywords: Optional[List[str]] = None
    content_ids: Optional[List[str]] = None
    xhs_note_urls: Optional[List[str]] = Field(None, description="小红书完整URL列表(detail模式必需,需包含xsec_token&xsec_source)")
    creator_ids: Optional[List[str]] = None
    max_count: int = Field(default=100, ge=1, le=1000)
    max_comments: int = Field(default=50, ge=0, le=500)
    start_page: int = Field(default=1, ge=1)
    enable_proxy: bool = False
    headless: bool = False  # 修改默认值为False，显示浏览器窗口
    enable_comments: bool = False
    enable_sub_comments: bool = False
    save_data_option: str = Field(default="db", pattern="^(db|json|csv)$")
    config: Optional[CrawlerConfigRequest] = None
    clear_cookies: bool = Field(default=False, description="是否清除cookies重新登录")


class CrawlerTaskResponse(BaseModel):
    task_id: str
    message: str


class TaskProgressInfo(BaseModel):
    current_stage: str
    progress_percent: float
    items_total: int
    items_completed: int
    items_failed: int
    current_item: Optional[str] = None
    estimated_remaining_time: Optional[int] = None
    last_update: Optional[str] = None


class TaskStatusResponse(BaseModel):
    task_id: str
    status: str  # "running", "completed", "not_found"
    done: bool
    success: Optional[bool] = None
    message: Optional[str] = None
    data_count: Optional[int] = None
    error_count: Optional[int] = None
    progress: Optional[TaskProgressInfo] = None


class TaskResultResponse(BaseModel):
    task_id: str
    success: bool
    message: str
    data_count: int = 0
    error_count: int = 0
    data: Optional[List[Dict]] = None
    errors: Optional[List[str]] = None


# 平台映射
PLATFORM_MAPPING = {
    "xhs": PlatformType.XHS,
    "douyin": PlatformType.DOUYIN,
    "bilibili": PlatformType.BILIBILI,
    "kuaishou": PlatformType.KUAISHOU,
    "weibo": PlatformType.WEIBO,
    "tieba": PlatformType.TIEBA,
    "zhihu": PlatformType.ZHIHU
}


@app.get("/")
async def root():
    """健康检查"""
    import os
    from app.core.config import get_settings
    settings = get_settings()
    return {
        "message": "MediaCrawler API Server is running",
        "version": "1.0.0",
        "supported_platforms": list(PLATFORM_MAPPING.keys()),
        "supabase_configured": bool(settings.supabase_url and settings.supabase_key),
        "supabase_url": settings.supabase_url[:30] + "..." if settings.supabase_url else None,
        "seo_supabase_url": os.getenv("SEO_SUPABASE_URL", "NOT_FOUND")[:30] + "..." if os.getenv("SEO_SUPABASE_URL") else "NOT_FOUND",
        "old_supabase_url": os.getenv("SUPABASE_URL", "NOT_FOUND")[:30] + "..." if os.getenv("SUPABASE_URL") else "NOT_FOUND",
        "cwd": os.getcwd()
    }


@app.post("/api/v1/tasks", response_model=CrawlerTaskResponse)
async def create_crawler_task(
    request: CrawlerTaskRequest,
    background_tasks: BackgroundTasks
):
    """创建爬虫任务"""
    try:
        # 验证平台
        if request.platform not in PLATFORM_MAPPING:
            raise HTTPException(
                status_code=400,
                detail=f"不支持的平台: {request.platform}"
            )
        
        # 验证任务类型
        try:
            task_type = CrawlerTaskType(request.task_type)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"不支持的任务类型: {request.task_type}"
            )
        
        # 参数验证
        if request.task_type == "search" and not request.keywords:
            raise HTTPException(status_code=400, detail="搜索模式需要提供keywords参数")
        
        if request.task_type == "detail":
            if not request.content_ids:
                raise HTTPException(status_code=400, detail="详情模式需要提供content_ids参数")
            if request.platform == "xhs" and not request.xhs_note_urls:
                raise HTTPException(status_code=400, detail="小红书详情模式需要提供xhs_note_urls参数(包含xsec_token和xsec_source的完整URL)")
        
        if request.task_type == "creator" and not request.creator_ids:
            raise HTTPException(status_code=400, detail="创作者模式需要提供creator_ids参数")

        # 🍪 处理cookies清除请求
        if request.clear_cookies:
            from app.core.cookies_manager import cookies_manager
            platform_str = crawler_adapter._get_platform_string(PlatformType(request.platform))
            success = cookies_manager.clear_cookies(platform_str)
            logger.info(f"🗑️  清除cookies {'成功' if success else '失败'}: {platform_str}")

        # 生成任务ID
        task_id = str(uuid.uuid4())
        
        # 创建任务
        task = CrawlerTask(
            task_id=task_id,
            platform=PLATFORM_MAPPING[request.platform],
            task_type=task_type,
            keywords=request.keywords,
            content_ids=request.content_ids,
            xhs_note_urls=request.xhs_note_urls,
            creator_ids=request.creator_ids,
            max_count=request.max_count,
            max_comments=request.max_comments,
            start_page=request.start_page,
            enable_proxy=request.enable_proxy,
            headless=request.headless,
            enable_comments=request.enable_comments,
            enable_sub_comments=request.enable_sub_comments,
            save_data_option=request.save_data_option,
            config=request.config,
            clear_cookies=request.clear_cookies
        )
        
        # 启动任务
        await crawler_adapter.start_crawler_task(task)
        
        return CrawlerTaskResponse(
            task_id=task_id,
            message="任务已创建并开始执行"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"创建爬虫任务失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/tasks/{task_id}/status", response_model=TaskStatusResponse)
async def get_task_status(task_id: str):
    """获取任务状态"""
    try:
        status = await crawler_adapter.get_task_status(task_id)
        return TaskStatusResponse(**status)
    except Exception as e:
        logger.error(f"获取任务状态失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/tasks/{task_id}/result", response_model=TaskResultResponse)
async def get_task_result(task_id: str):
    """获取任务结果"""
    try:
        result = await crawler_adapter.get_task_result(task_id)
        
        if result is None:
            raise HTTPException(
                status_code=404,
                detail="任务不存在"
            )
        
        return TaskResultResponse(
            task_id=result.task_id,
            success=result.success,
            message=result.message,
            data_count=result.data_count,
            error_count=result.error_count,
            data=result.data,
            errors=result.errors
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取任务结果失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/v1/tasks/{task_id}")
async def stop_task(task_id: str):
    """停止任务"""
    try:
        success = await crawler_adapter.stop_task(task_id)
        
        if not success:
            raise HTTPException(
                status_code=404,
                detail="任务不存在或已完成"
            )
        
        return {"message": "任务已停止"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"停止任务失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/tasks")
async def list_running_tasks():
    """列出运行中的任务"""
    try:
        running_tasks = await crawler_adapter.list_running_tasks()
        return {
            "running_tasks": running_tasks,
            "count": len(running_tasks)
        }
    except Exception as e:
        logger.error(f"列出运行任务失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/tasks/{task_id}/events")
async def get_task_events(task_id: str, limit: int = 50):
    """获取任务事件日志"""
    try:
        events = await crawler_adapter.get_task_events(task_id, limit)
        return {
            "task_id": task_id,
            "events": events,
            "count": len(events)
        }
    except Exception as e:
        logger.error(f"获取任务事件失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取任务事件失败: {str(e)}")


@app.get("/api/v1/system/stats")
async def get_system_stats():
    """获取系统统计信息"""
    try:
        stats = await crawler_adapter.get_system_stats()
        return stats
    except Exception as e:
        logger.error(f"获取系统统计信息失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/system/config/options")
async def get_config_options():
    """获取支持的配置选项"""
    try:
        config_manager = get_config_manager()
        options = config_manager.get_supported_config_options()
        return {
            "message": "支持的配置选项",
            "options": options
        }
    except Exception as e:
        logger.error(f"获取配置选项失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/maintenance/cleanup")
async def cleanup_completed_tasks():
    """清理已完成的任务结果"""
    try:
        await crawler_adapter.cleanup_completed_tasks()
        return {"message": "清理完成"}
    except Exception as e:
        logger.error(f"清理任务失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# 便捷的平台特定端点
class QuickSearchRequest(BaseModel):
    keywords: List[str]
    max_count: int = 100
    max_comments: int = 50
    enable_proxy: bool = False
    config: Optional[CrawlerConfigRequest] = None


@app.post("/api/v1/xhs/search")
async def xhs_search(request: QuickSearchRequest):
    """小红书搜索"""
    task_id = str(uuid.uuid4())
    task = CrawlerTask(
        task_id=task_id,
        platform=PlatformType.XHS,
        task_type=CrawlerTaskType.SEARCH,
        keywords=request.keywords,
        max_count=request.max_count,
        max_comments=request.max_comments,
        enable_proxy=request.enable_proxy,
        config=request.config
    )
    
    await crawler_adapter.start_crawler_task(task)
    return {"task_id": task_id, "message": "小红书搜索任务已启动"}


@app.post("/api/v1/douyin/search")
async def douyin_search(request: QuickSearchRequest):
    """抖音搜索"""
    task_id = str(uuid.uuid4())
    task = CrawlerTask(
        task_id=task_id,
        platform=PlatformType.DOUYIN,
        task_type=CrawlerTaskType.SEARCH,
        keywords=request.keywords,
        max_count=request.max_count,
        max_comments=request.max_comments,
        enable_proxy=request.enable_proxy,
        config=request.config
    )
    
    await crawler_adapter.start_crawler_task(task)
    return {"task_id": task_id, "message": "抖音搜索任务已启动"}


# ===== Cookies管理API =====

@app.get("/api/v1/cookies/{platform}/status")
async def get_cookies_status(platform: str):
    """获取指定平台的cookies状态"""
    try:
        from app.core.cookies_manager import cookies_manager
        
        status = cookies_manager.get_cookies_status(platform, max_age_days=7)
        return {
            "success": True,
            "data": status,
            "message": f"Cookies状态获取成功: {platform}"
        }
    except Exception as e:
        logger.error(f"获取cookies状态失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取cookies状态失败: {str(e)}")


@app.get("/api/v1/cookies")
async def list_all_cookies():
    """列出所有平台的cookies缓存信息"""
    try:
        from app.core.cookies_manager import cookies_manager
        
        cookies_info = cookies_manager.list_cached_cookies()
        return {
            "success": True,
            "data": cookies_info,
            "count": len(cookies_info),
            "message": "Cookies列表获取成功"
        }
    except Exception as e:
        logger.error(f"获取cookies列表失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取cookies列表失败: {str(e)}")


@app.delete("/api/v1/cookies/{platform}")
async def clear_platform_cookies(platform: str):
    """清除指定平台的cookies"""
    try:
        from app.core.cookies_manager import cookies_manager
        
        success = cookies_manager.clear_cookies(platform)
        return {
            "success": success,
            "platform": platform,
            "message": f"Cookies清除{'成功' if success else '失败'}: {platform}"
        }
    except Exception as e:
        logger.error(f"清除cookies失败: {e}")
        raise HTTPException(status_code=500, detail=f"清除cookies失败: {str(e)}")


@app.delete("/api/v1/cookies")
async def clear_all_cookies():
    """清除所有平台的cookies"""
    try:
        from app.core.cookies_manager import cookies_manager
        
        success = cookies_manager.clear_cookies()
        return {
            "success": success,
            "message": f"所有cookies清除{'成功' if success else '失败'}"
        }
    except Exception as e:
        logger.error(f"清除所有cookies失败: {e}")
        raise HTTPException(status_code=500, detail=f"清除所有cookies失败: {str(e)}")


class SaveCookiesRequest(BaseModel):
    """保存cookies请求"""
    platform: str = Field(..., description="平台名称")
    cookies: str = Field(..., description="Cookies字符串")
    task_id: Optional[str] = Field(None, description="任务ID")


@app.post("/api/v1/cookies")
async def save_cookies(request: SaveCookiesRequest):
    """手动保存cookies"""
    try:
        from app.core.cookies_manager import cookies_manager
        
        success = cookies_manager.save_cookies(
            request.platform, 
            request.cookies, 
            request.task_id
        )
        
        return {
            "success": success,
            "platform": request.platform,
            "task_id": request.task_id,
            "message": f"Cookies保存{'成功' if success else '失败'}: {request.platform}"
        }
    except Exception as e:
        logger.error(f"保存cookies失败: {e}")
        raise HTTPException(status_code=500, detail=f"保存cookies失败: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 