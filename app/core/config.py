"""
应用配置管理
使用Pydantic Settings进行环境变量和配置文件管理
"""

import os
from typing import List, Optional
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """应用配置类"""
    
    # 应用基础配置
    app_name: str = Field(default="MediaCrawler-ApiServer", description="应用名称")
    app_version: str = Field(default="1.0.0", description="应用版本")
    debug: bool = Field(default=False, description="调试模式")
    environment: str = Field(default="development", description="运行环境")
    
    # API配置
    api_v1_prefix: str = Field(default="/api/v1", description="API v1路径前缀")
    allowed_hosts: List[str] = Field(default=["*"], description="允许的主机列表")
    cors_origins: List[str] = Field(default=["*"], description="CORS允许的源")
    
    # 安全配置
    secret_key: str = Field(default="your-secret-key-change-in-production", description="JWT密钥")
    api_key_header: str = Field(default="X-API-Key", description="API Key请求头")
    access_token_expire_minutes: int = Field(default=60 * 24 * 8, description="访问令牌过期时间(分钟)")
    
    # 数据库配置
    database_url: Optional[str] = Field(default=None, description="数据库连接URL")
    database_echo: bool = Field(default=False, description="数据库SQL日志")
    database_pool_size: int = Field(default=5, description="数据库连接池大小")
    database_max_overflow: int = Field(default=10, description="数据库连接池最大溢出")
    
    # Redis配置
    redis_url: str = Field(default="redis://localhost:6379", description="Redis连接URL")
    redis_password: Optional[str] = Field(default=None, description="Redis密码")
    redis_db: int = Field(default=0, description="Redis数据库编号")
    
    # 爬虫配置
    max_concurrent_tasks: int = Field(default=10, description="最大并发任务数")
    task_timeout: int = Field(default=3600, description="任务超时时间(秒)")
    crawler_user_agent: str = Field(
        default="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
        description="爬虫User Agent"
    )
    enable_ip_proxy: bool = Field(default=False, description="是否启用IP代理")
    ip_proxy_pool_count: int = Field(default=100, description="代理IP池数量")
    
    # 存储配置
    data_storage_path: str = Field(default="data", description="数据存储路径")
    export_file_expire_hours: int = Field(default=24, description="导出文件过期时间(小时)")
    
    # 日志配置
    log_level: str = Field(default="INFO", description="日志级别")
    log_format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        description="日志格式"
    )
    
    # 监控配置
    enable_metrics: bool = Field(default=True, description="是否启用指标收集")
    metrics_port: int = Field(default=9090, description="指标服务端口")
    
    # Supabase配置（兼容原有项目）
    supabase_url: Optional[str] = Field(default=None, env="SUPABASE_URL", description="Supabase URL")
    supabase_key: Optional[str] = Field(default=None, env="SUPABASE_KEY", description="Supabase匿名密钥")
    
    # 数据存储选项
    save_data_option: str = Field(default="db", description="数据保存选项: db/json/csv")
    
    # =================================
    # 新增：原MediaCrawler数据库配置 (兼容)
    # =================================
    relation_db_user: str = Field(default="root", env="RELATION_DB_USER", description="MySQL用户名")
    relation_db_pwd: str = Field(default="123456", env="RELATION_DB_PWD", description="MySQL密码")
    relation_db_host: str = Field(default="localhost", env="RELATION_DB_HOST", description="MySQL主机")
    relation_db_port: int = Field(default=3306, env="RELATION_DB_PORT", description="MySQL端口")
    relation_db_name: str = Field(default="media_crawler", env="RELATION_DB_NAME", description="MySQL数据库名")
    
    redis_db_host: str = Field(default="127.0.0.1", env="REDIS_DB_HOST", description="Redis主机")
    redis_db_pwd: str = Field(default="123456", env="REDIS_DB_PWD", description="Redis密码")
    redis_db_port: int = Field(default=6379, env="REDIS_DB_PORT", description="Redis端口")
    redis_db_num: int = Field(default=0, env="REDIS_DB_NUM", description="Redis数据库编号")
    
    # =================================
    # 新增：文件存储路径配置
    # =================================
    mediacrawler_data_path: str = Field(default="./data", env="MEDIACRAWLER_DATA_PATH", description="MediaCrawler数据输出路径")
    csv_data_path: str = Field(default="./data/csv", env="CSV_DATA_PATH", description="CSV文件路径")
    json_data_path: str = Field(default="./data/json", env="JSON_DATA_PATH", description="JSON文件路径")
    
    # =================================
    # 新增：数据访问配置
    # =================================
    primary_data_source: str = Field(default="supabase", env="PRIMARY_DATA_SOURCE", description="主数据源类型")
    fallback_data_source: str = Field(default="csv", env="FALLBACK_DATA_SOURCE", description="备用数据源类型")
    auto_fallback_enabled: bool = Field(default=True, env="AUTO_FALLBACK_ENABLED", description="数据源自动切换")
    db_connection_timeout: int = Field(default=30, env="DB_CONNECTION_TIMEOUT", description="数据库连接超时(秒)")
    data_query_timeout: int = Field(default=60, env="DATA_QUERY_TIMEOUT", description="数据查询超时(秒)")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

    @property
    def database_url_sync(self) -> str:
        """同步数据库URL"""
        if not self.database_url:
            return "sqlite:///./app.db"
        return self.database_url.replace("postgresql+asyncpg://", "postgresql://")

    @property
    def database_url_async(self) -> str:
        """异步数据库URL"""
        if not self.database_url:
            return "sqlite+aiosqlite:///./app.db"
        if self.database_url.startswith("postgresql://"):
            return self.database_url.replace("postgresql://", "postgresql+asyncpg://")
        return self.database_url
    
    @property
    def mysql_url_async(self) -> str:
        """MySQL异步连接URL - 兼容原MediaCrawler"""
        return f"mysql+aiomysql://{self.relation_db_user}:{self.relation_db_pwd}@{self.relation_db_host}:{self.relation_db_port}/{self.relation_db_name}"
    
    @property
    def mysql_url_sync(self) -> str:
        """MySQL同步连接URL"""
        return f"mysql+pymysql://{self.relation_db_user}:{self.relation_db_pwd}@{self.relation_db_host}:{self.relation_db_port}/{self.relation_db_name}"
    
    @property
    def redis_url_from_components(self) -> str:
        """根据组件构建Redis URL"""
        auth_part = f":{self.redis_db_pwd}@" if self.redis_db_pwd else ""
        return f"redis://{auth_part}{self.redis_db_host}:{self.redis_db_port}/{self.redis_db_num}"
    
    def get_data_source_config(self, source_type: str) -> dict:
        """获取指定数据源的配置"""
        if source_type == "supabase":
            return {
                "url": self.supabase_url,
                "key": self.supabase_key,
                "database_url": self.database_url_async
            }
        elif source_type == "mysql":
            return {
                "database_url": self.mysql_url_async,
                "host": self.relation_db_host,
                "port": self.relation_db_port,
                "user": self.relation_db_user,
                "password": self.relation_db_pwd,
                "database": self.relation_db_name
            }
        elif source_type == "csv":
            return {
                "data_path": self.csv_data_path,
                "mediacrawler_path": self.mediacrawler_data_path
            }
        elif source_type == "json":
            return {
                "data_path": self.json_data_path,
                "mediacrawler_path": self.mediacrawler_data_path
            }
        else:
            raise ValueError(f"不支持的数据源类型: {source_type}")


# 全局配置实例
settings = Settings()


def get_settings() -> Settings:
    """获取应用配置实例"""
    return settings 