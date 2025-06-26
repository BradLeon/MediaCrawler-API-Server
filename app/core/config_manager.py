"""
统一配置管理器
基于Pydantic模型的类型安全配置管理

场景分类和对应的模型：
1. 应用级配置 - AppConfig
2. 爬虫任务级配置 - CrawlerConfig (请求: CrawlerConfigRequest)
3. 数据存储配置 - StorageConfig
"""

from typing import Dict, Any, List, Optional, Union
from pydantic import BaseModel, Field, validator
from app.core.config import get_settings


# ===== 1. 应用级配置模型 =====
class AppConfig(BaseModel):
    """应用级配置"""
    app_name: str = "MediaCrawler API Server"
    version: str = "1.0.0"
    environment: str = "development"
    debug: bool = False
    log_level: str = "INFO"
    cors_origins: List[str] = ["*"]
    api_prefix: str = "/api/v1"
    supported_platforms: List[str] = ["xhs", "douyin", "bilibili", "kuaishou", "weibo", "tieba", "zhihu"]


# ===== 2. 爬虫任务级配置模型 =====
class CrawlerConfigRequest(BaseModel):
    """爬虫任务配置请求（来自API，允许部分字段为空）"""
    enable_proxy: Optional[bool] = None
    proxy_provider: Optional[str] = None
    proxy_config: Optional[Dict[str, Any]] = None
    headless: Optional[bool] = None
    user_agent: Optional[str] = None
    window_size: Optional[str] = Field(None, pattern=r'^\d+,\d+$', description="窗口大小，格式: width,height")
    max_retries: Optional[int] = Field(None, ge=0, le=10)
    delay_range: Optional[List[int]] = Field(None, min_length=2, max_length=2)
    timeout: Optional[int] = Field(None, ge=10, le=300)
    enable_comments: Optional[bool] = None
    enable_sub_comments: Optional[bool] = None
    max_comments: Optional[int] = Field(None, ge=0, le=1000)
    save_data_option: Optional[str] = Field(None, pattern=r'^(db|json|csv)$')

    @validator('delay_range')
    def validate_delay_range(cls, v):
        if v and len(v) == 2 and v[0] > v[1]:
            raise ValueError('delay_range第一个值应该小于或等于第二个值')
        return v


class CrawlerConfig(BaseModel):
    """爬虫任务完整配置（内部使用，所有字段都有默认值）"""
    platform: str
    enable_proxy: bool = False
    proxy_provider: Optional[str] = None
    proxy_config: Optional[Dict[str, Any]] = None
    headless: bool = True
    user_agent: Optional[str] = None
    window_size: str = "1920,1080"
    max_retries: int = 3
    delay_range: List[int] = [1, 3]
    timeout: int = 30
    enable_comments: bool = True
    enable_sub_comments: bool = False
    max_comments: int = 50
    save_data_option: str = "db"

    @validator('delay_range')
    def validate_delay_range(cls, v):
        if len(v) == 2 and v[0] > v[1]:
            raise ValueError('delay_range第一个值应该小于或等于第二个值')
        return v

    class Config:
        extra = "forbid"  # 禁止额外字段


# ===== 3. 数据存储级配置模型 =====
class StorageConfig(BaseModel):
    """数据存储配置"""
    source_type: str = Field(..., pattern=r'^(json|csv|supabase)$')
    platform: Optional[str] = None
    connection_timeout: int = Field(30, ge=5, le=120)
    retry_times: int = Field(3, ge=0, le=10)
    batch_size: int = Field(100, ge=1, le=1000)
    
    # 文件存储特定配置
    base_path: Optional[str] = None
    file_encoding: str = "utf-8"
    ensure_dirs: bool = True
    
    # CSV特定配置
    delimiter: str = ","
    quotechar: str = '"'
    
    # Supabase特定配置
    url: Optional[str] = None
    key: Optional[str] = None
    
    class Config:
        extra = "forbid"


# ===== 4. 平台信息模型 =====
class PlatformInfo(BaseModel):
    """平台信息"""
    key: str
    name: str
    delay_range: List[int] = [1, 3]
    max_comments: int = 50
    timeout: int = 30


# ===== 统一配置管理器 =====
class ConfigManager:
    """统一配置管理器 - 基于Pydantic模型的类型安全配置管理"""
    
    def __init__(self):
        self.settings = get_settings()
        self._app_config_cache: Optional[AppConfig] = None
        self._platform_configs: Dict[str, PlatformInfo] = {}
        self._init_platform_configs()
    
    def _init_platform_configs(self):
        """初始化平台配置"""
        platforms_data = {
            "xhs": {"key": "xhs", "name": "小红书", "delay_range": [2, 4], "max_comments": 100, "timeout": 45},
            "douyin": {"key": "douyin", "name": "抖音", "delay_range": [1, 2], "max_comments": 50, "timeout": 30},
            "bilibili": {"key": "bilibili", "name": "哔哩哔哩", "delay_range": [1, 3], "max_comments": 80, "timeout": 40},
            "kuaishou": {"key": "kuaishou", "name": "快手", "delay_range": [2, 3], "max_comments": 60, "timeout": 35},
            "weibo": {"key": "weibo", "name": "微博", "delay_range": [1, 2], "max_comments": 50, "timeout": 30},
            "tieba": {"key": "tieba", "name": "百度贴吧", "delay_range": [2, 4], "max_comments": 100, "timeout": 50},
            "zhihu": {"key": "zhihu", "name": "知乎", "delay_range": [1, 3], "max_comments": 80, "timeout": 40}
        }
        
        for platform_key, data in platforms_data.items():
            self._platform_configs[platform_key] = PlatformInfo(**data)
    
    # ===== 1. 应用级配置 =====
    def get_app_config(self) -> AppConfig:
        """获取应用级配置"""
        if self._app_config_cache is None:
            config_data = {
                "app_name": "MediaCrawler API Server",
                "version": "1.0.0",
                "environment": getattr(self.settings, 'environment', 'development'),
                "debug": getattr(self.settings, 'debug', False),
                "log_level": getattr(self.settings, 'log_level', 'INFO'),
                "cors_origins": getattr(self.settings, 'cors_origins', ["*"]),
                "api_prefix": "/api/v1",
                "supported_platforms": list(self._platform_configs.keys())
            }
            self._app_config_cache = AppConfig(**config_data)
        return self._app_config_cache
    
    def get_supported_platforms(self) -> List[PlatformInfo]:
        """获取支持的平台列表"""
        return list(self._platform_configs.values())
    
    # ===== 2. 爬虫任务级配置 =====
    def build_crawler_config(self, platform: str, request_config: Optional[CrawlerConfigRequest] = None) -> CrawlerConfig:
        """
        构建爬虫任务配置
        
        Args:
            platform: 平台名称
            request_config: API请求配置（可选）
        
        Returns:
            完整的爬虫配置
        """
        # 1. 基础默认配置
        base_config = {
            "platform": platform,
            "headless": True,
            "enable_proxy": False,
            "proxy_provider": None,
            "proxy_config": None,
            "user_agent": None,
            "window_size": "1920,1080",
            "max_retries": 3,
            "delay_range": [1, 3],
            "timeout": 30,
            "enable_comments": True,
            "enable_sub_comments": False,
            "max_comments": 50,
            "save_data_option": "db"
        }
        
        # 2. 应用平台特定配置
        if platform in self._platform_configs:
            platform_info = self._platform_configs[platform]
            base_config.update({
                "delay_range": platform_info.delay_range,
                "max_comments": platform_info.max_comments,
                "timeout": platform_info.timeout
            })
        
        # 3. 应用环境变量配置覆盖
        env_overrides = self._get_env_config_overrides()
        base_config.update(env_overrides)
        
        # 4. 应用API请求配置覆盖
        if request_config:
            # 只更新非None的字段
            request_dict = request_config.dict(exclude_unset=True, exclude_none=True)
            base_config.update(request_dict)
        
        # 5. 创建并返回类型安全的配置对象
        return CrawlerConfig(**base_config)
    
    def _get_env_config_overrides(self) -> Dict[str, Any]:
        """从环境变量获取配置覆盖"""
        env_overrides = {}
        
        # 映射环境变量到配置字段
        env_mappings = {
            'default_headless': 'headless',
            'default_enable_proxy': 'enable_proxy', 
            'default_proxy_provider': 'proxy_provider',
            'default_max_retries': 'max_retries',
            'default_timeout': 'timeout'
        }
        
        for env_key, config_key in env_mappings.items():
            if hasattr(self.settings, env_key):
                value = getattr(self.settings, env_key)
                if value is not None:
                    env_overrides[config_key] = value
        
        return env_overrides
    
    # ===== 3. 数据存储级配置 =====
    def build_storage_config(self, source_type: str, platform: Optional[str] = None) -> StorageConfig:
        """
        构建数据存储配置
        
        Args:
            source_type: 存储类型 (json, csv, supabase)
            platform: 平台名称（可选）
        
        Returns:
            存储配置对象
        """
        config_data = {
            "source_type": source_type,
            "platform": platform,
            "connection_timeout": 30,
            "retry_times": 3,
            "batch_size": 100
        }
        
        # 根据存储类型设置特定配置
        if source_type == "json":
            config_data.update({
                "base_path": "data",
                "file_encoding": "utf-8",
                "ensure_dirs": True
            })
        elif source_type == "csv":
            config_data.update({
                "base_path": "data", 
                "file_encoding": "utf-8",
                "ensure_dirs": True,
                "delimiter": ",",
                "quotechar": '"'
            })
        elif source_type == "supabase":
            config_data.update({
                "url": getattr(self.settings, 'supabase_url', None),
                "key": getattr(self.settings, 'supabase_key', None),
                "connection_timeout": getattr(self.settings, 'supabase_timeout', 30),
                "retry_times": getattr(self.settings, 'supabase_max_retries', 3)
            })
        
        return StorageConfig(**config_data)
    
    # ===== 工具方法 =====
    def get_supported_config_options(self) -> Dict[str, Any]:
        """获取支持的配置选项（用于API文档）"""
        return {
            "crawler_config_request": {
                "model": "CrawlerConfigRequest",
                "fields": CrawlerConfigRequest.__fields__,
                "description": "API请求中可传递的爬虫配置参数"
            },
            "crawler_config": {
                "model": "CrawlerConfig", 
                "fields": CrawlerConfig.__fields__,
                "description": "最终生效的完整爬虫配置"
            },
            "storage_config": {
                "model": "StorageConfig",
                "fields": StorageConfig.__fields__,
                "description": "数据存储配置"
            },
            "supported_platforms": [platform.dict() for platform in self.get_supported_platforms()]
        }
    
    def validate_crawler_request(self, request_data: Dict[str, Any]) -> CrawlerConfigRequest:
        """验证并创建爬虫配置请求对象"""
        return CrawlerConfigRequest(**request_data)


# 全局配置管理器实例
_config_manager = None

def get_config_manager() -> ConfigManager:
    """获取全局配置管理器实例"""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager 