"""
数据库连接和会话管理模块
主要支持Supabase (PostgreSQL) 数据库连接
"""
from typing import AsyncGenerator, Optional, Dict, Any
import logging
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    async_sessionmaker,
    AsyncEngine
)
from sqlalchemy.orm import declarative_base
from sqlalchemy.pool import QueuePool
from sqlalchemy.exc import SQLAlchemyError
from supabase import create_client, Client

from app.core.config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)

# SQLAlchemy声明基类
Base = declarative_base()

# 全局变量
_engine: Optional[AsyncEngine] = None
_async_session_maker: Optional[async_sessionmaker[AsyncSession]] = None
_supabase_client: Optional[Client] = None


def create_supabase_client() -> Optional[Client]:
    """创建Supabase客户端"""
    global _supabase_client
    
    if _supabase_client is not None:
        return _supabase_client
    
    if not settings.supabase_url or not settings.supabase_key:
        logger.warning("Supabase URL or key not configured")
        return None
    
    try:
        _supabase_client = create_client(settings.supabase_url, settings.supabase_key)
        logger.info("Supabase client created successfully")
        return _supabase_client
    except Exception as e:
        logger.error(f"Failed to create Supabase client: {e}")
        return None


def get_supabase_client() -> Optional[Client]:
    """获取Supabase客户端实例"""
    if _supabase_client is None:
        return create_supabase_client()
    return _supabase_client


def create_database_engine() -> AsyncEngine:
    """创建PostgreSQL数据库引擎"""
    # 如果配置了Supabase，构建PostgreSQL连接URL
    if settings.supabase_url and settings.supabase_key:
        # 从Supabase URL构建PostgreSQL连接字符串
        # Supabase URL格式: https://project-id.supabase.co
        # PostgreSQL URL格式: postgresql+asyncpg://postgres:password@host:5432/postgres
        project_id = settings.supabase_url.split("//")[1].split(".")[0]
        database_url = f"postgresql+asyncpg://postgres:{settings.supabase_key}@db.{project_id}.supabase.co:5432/postgres"
    else:
        # 回退到默认SQLite
        database_url = settings.database_url or "sqlite+aiosqlite:///./app.db"
    
    engine_kwargs = {
        "url": database_url,
        "echo": settings.debug,
        "pool_pre_ping": True,
        "pool_recycle": 3600,
    }
    
    # PostgreSQL连接池配置
    if "postgresql" in database_url:
        engine_kwargs.update({
            "poolclass": QueuePool,
            "pool_size": settings.db_pool_size,
            "max_overflow": settings.db_max_overflow,
            "pool_timeout": 30,
        })
    
    return create_async_engine(**engine_kwargs)


def get_async_session_maker() -> async_sessionmaker[AsyncSession]:
    """获取异步会话制造器"""
    global _async_session_maker, _engine
    
    if _async_session_maker is None:
        if _engine is None:
            _engine = create_database_engine()
        
        _async_session_maker = async_sessionmaker(
            bind=_engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autoflush=True,
            autocommit=False
        )
    
    return _async_session_maker


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """获取异步数据库会话（依赖注入用）"""
    session_maker = get_async_session_maker()
    async with session_maker() as session:
        try:
            yield session
        except SQLAlchemyError as e:
            logger.error(f"Database session error: {e}")
            await session.rollback()
            raise
        finally:
            await session.close()


@asynccontextmanager
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """获取数据库会话上下文管理器"""
    session_maker = get_async_session_maker()
    async with session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            logger.error(f"Database transaction error: {e}")
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_database() -> None:
    """初始化数据库（创建表）"""
    global _engine
    
    if _engine is None:
        _engine = create_database_engine()
    
    try:
        async with _engine.begin() as conn:
            # 导入所有模型以确保表被创建
            from app.models import (
                XhsContentModel, XhsCommentModel, XhsCreatorModel,
                DouyinContentModel, DouyinCommentModel, DouyinCreatorModel,
                BilibiliContentModel, BilibiliCommentModel, BilibiliCreatorModel,
                KuaishouContentModel, KuaishouCommentModel, KuaishouCreatorModel,
                WeiboContentModel, WeiboCommentModel, WeiboCreatorModel,
                TiebaContentModel, TiebaCommentModel, TiebaCreatorModel,
                ZhihuContentModel, ZhihuCommentModel, ZhihuCreatorModel,
                TaskModel
            )
            
            # 创建所有表
            await conn.run_sync(Base.metadata.create_all)
            logger.info("Database tables created successfully")
            
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise


async def check_database_connection() -> bool:
    """检查数据库连接状态"""
    try:
        async with get_session() as session:
            result = await session.execute("SELECT 1")
            return result.scalar() == 1
    except Exception as e:
        logger.error(f"Database connection check failed: {e}")
        return False


async def check_supabase_connection() -> bool:
    """检查Supabase连接状态"""
    client = get_supabase_client()
    if not client:
        return False
    
    try:
        # 测试连接：查询一个简单的表或执行简单查询
        result = client.table("xhs_note").select("note_id").limit(1).execute()
        return True
    except Exception as e:
        logger.error(f"Supabase connection check failed: {e}")
        return False


async def close_database() -> None:
    """关闭数据库连接"""
    global _engine, _async_session_maker, _supabase_client
    
    if _engine:
        await _engine.dispose()
        _engine = None
        _async_session_maker = None
    
    _supabase_client = None
    logger.info("Database connections closed")


class DatabaseManager:
    """数据库管理器，同时管理SQLAlchemy和Supabase连接"""
    
    def __init__(self):
        self._engine: Optional[AsyncEngine] = None
        self._session_maker: Optional[async_sessionmaker[AsyncSession]] = None
        self._supabase_client: Optional[Client] = None
        self._initialized = False
    
    async def initialize(self) -> None:
        """初始化数据库管理器"""
        if self._initialized:
            return
        
        # 初始化SQLAlchemy引擎
        self._engine = create_database_engine()
        self._session_maker = async_sessionmaker(
            bind=self._engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
        
        # 初始化Supabase客户端
        self._supabase_client = create_supabase_client()
        
        # 测试连接
        sqlalchemy_ok = await self._check_sqlalchemy_connection()
        supabase_ok = await self._check_supabase_connection()
        
        if not sqlalchemy_ok and not supabase_ok:
            raise RuntimeError("Failed to establish any database connection")
        
        self._initialized = True
        logger.info(f"Database manager initialized - SQLAlchemy: {sqlalchemy_ok}, Supabase: {supabase_ok}")
    
    async def _check_sqlalchemy_connection(self) -> bool:
        """检查SQLAlchemy连接"""
        if not self._session_maker:
            return False
        
        try:
            async with self._session_maker() as session:
                await session.execute("SELECT 1")
                return True
        except Exception as e:
            logger.error(f"SQLAlchemy connection failed: {e}")
            return False
    
    async def _check_supabase_connection(self) -> bool:
        """检查Supabase连接"""
        if not self._supabase_client:
            return False
        
        try:
            # 简单的健康检查
            self._supabase_client.table("xhs_note").select("note_id").limit(1).execute()
            return True
        except Exception as e:
            logger.error(f"Supabase connection failed: {e}")
            return False
    
    @property
    def supabase_client(self) -> Optional[Client]:
        """获取Supabase客户端"""
        return self._supabase_client
    
    @asynccontextmanager
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """获取SQLAlchemy数据库会话"""
        if not self._initialized:
            await self.initialize()
        
        if not self._session_maker:
            raise RuntimeError("SQLAlchemy session maker not initialized")
        
        async with self._session_maker() as session:
            try:
                yield session
                await session.commit()
            except Exception as e:
                logger.error(f"Database session error: {e}")
                await session.rollback()
                raise
            finally:
                await session.close()
    
    async def close(self) -> None:
        """关闭数据库连接"""
        if self._engine:
            await self._engine.dispose()
            self._engine = None
            self._session_maker = None
            self._supabase_client = None
            self._initialized = False
            logger.info("Database manager closed")


# 全局数据库管理器实例
db_manager = DatabaseManager() 