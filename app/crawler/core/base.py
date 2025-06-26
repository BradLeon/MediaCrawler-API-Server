"""
爬虫引擎基础抽象类

定义了爬虫引擎的核心接口，所有平台的爬虫实现都必须继承这些抽象类。
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Union
from enum import Enum
from dataclasses import dataclass
from datetime import datetime

from playwright.async_api import BrowserContext, BrowserType, Page
 
from app.dataReader.base import PlatformType


class CrawlerType(Enum):
    """爬虫类型枚举"""
    SEARCH = "search"        # 关键词搜索
    DETAIL = "detail"        # 指定内容详情
    CREATOR = "creator"      # 创作者主页
    COMMENTS = "comments"    # 评论数据
    TRENDING = "trending"    # 热门内容


class LoginType(Enum):
    """登录方式枚举"""
    QRCODE = "qrcode"       # 二维码登录
    MOBILE = "mobile"       # 手机号登录
    COOKIE = "cookie"       # Cookie登录
    PASSWORD = "password"   # 用户名密码登录


class CrawlerStatus(Enum):
    """爬虫状态枚举"""
    IDLE = "idle"           # 空闲
    RUNNING = "running"     # 运行中
    PAUSED = "paused"       # 暂停
    STOPPED = "stopped"     # 已停止
    ERROR = "error"         # 错误状态


@dataclass
class CrawlerConfig:
    """爬虫配置"""
    platform: PlatformType
    crawler_type: CrawlerType
    keywords: List[str] = None
    content_ids: List[str] = None
    creator_ids: List[str] = None
    max_content_count: int = 100
    max_comments_count: int = 50
    start_page: int = 1
    enable_proxy: bool = False
    enable_stealth: bool = True
    headless: bool = True
    user_agent: str = None
    login_type: LoginType = LoginType.COOKIE
    save_media: bool = False
    concurrent_limit: int = 3
    delay_range: tuple = (1, 3)


@dataclass
class CrawlerResult:
    """爬虫结果"""
    success: bool
    message: str
    platform: PlatformType
    crawler_type: CrawlerType
    data_count: int = 0
    error_count: int = 0
    start_time: datetime = None
    end_time: datetime = None
    data: Optional[List[Dict[str, Any]]] = None
    errors: Optional[List[str]] = None

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "success": self.success,
            "message": self.message,
            "platform": self.platform.value,
            "crawler_type": self.crawler_type.value,
            "data_count": self.data_count,
            "error_count": self.error_count,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "duration_seconds": (
                (self.end_time - self.start_time).total_seconds() 
                if self.start_time and self.end_time else 0
            ),
            "data": self.data,
            "errors": self.errors
        }


class AbstractCrawler(ABC):
    """抽象爬虫基类"""
    
    def __init__(self, config: CrawlerConfig):
        self.config = config
        self.status = CrawlerStatus.IDLE
        self.browser_context: Optional[BrowserContext] = None
        self.current_page: Optional[Page] = None
        self.result = CrawlerResult(
            success=False,
            message="",
            platform=config.platform,
            crawler_type=config.crawler_type
        )

    @abstractmethod
    async def start(self) -> CrawlerResult:
        """启动爬虫"""
        pass

    @abstractmethod
    async def stop(self) -> None:
        """停止爬虫并清理资源"""
        pass

    @abstractmethod
    async def pause(self) -> None:
        """暂停爬虫"""
        pass

    @abstractmethod
    async def resume(self) -> None:
        """恢复爬虫"""
        pass

    @abstractmethod
    async def search(self, keywords: List[str]) -> List[Dict[str, Any]]:
        """根据关键词搜索内容"""
        pass

    @abstractmethod
    async def get_content_detail(self, content_ids: List[str]) -> List[Dict[str, Any]]:
        """获取指定内容的详细信息"""
        pass

    @abstractmethod
    async def get_creator_info(self, creator_ids: List[str]) -> List[Dict[str, Any]]:
        """获取创作者信息"""
        pass

    @abstractmethod
    async def get_comments(self, content_id: str, max_count: int = 50) -> List[Dict[str, Any]]:
        """获取内容的评论"""
        pass

    @abstractmethod
    async def login(self, login_type: LoginType, **kwargs) -> bool:
        """登录平台"""
        pass

    @abstractmethod
    async def init_browser(self, headless: bool = True) -> BrowserContext:
        """初始化浏览器"""
        pass

    async def get_status(self) -> CrawlerStatus:
        """获取爬虫当前状态"""
        return self.status

    async def get_result(self) -> CrawlerResult:
        """获取爬虫执行结果"""
        return self.result


class AbstractLogin(ABC):
    """抽象登录管理基类"""

    def __init__(self, platform: PlatformType, browser_context: BrowserContext):
        self.platform = platform
        self.browser_context = browser_context

    @abstractmethod
    async def login_by_qrcode(self) -> bool:
        """二维码登录"""
        pass

    @abstractmethod
    async def login_by_mobile(self, phone: str, code: str = None) -> bool:
        """手机号登录"""
        pass

    @abstractmethod
    async def login_by_cookie(self, cookies: Union[str, List[Dict]]) -> bool:
        """Cookie登录"""
        pass

    @abstractmethod
    async def login_by_password(self, username: str, password: str) -> bool:
        """用户名密码登录"""
        pass

    @abstractmethod
    async def check_login_status(self) -> bool:
        """检查登录状态"""
        pass

    @abstractmethod
    async def save_login_state(self, file_path: str = None) -> bool:
        """保存登录状态"""
        pass

    @abstractmethod
    async def load_login_state(self, file_path: str = None) -> bool:
        """加载登录状态"""
        pass

    @abstractmethod
    async def logout(self) -> bool:
        """退出登录"""
        pass


class AbstractStore(ABC):
    """抽象存储管理基类"""

    @abstractmethod
    async def store_content(self, content_items: List[Dict[str, Any]]) -> bool:
        """存储内容数据"""
        pass

    @abstractmethod
    async def store_comments(self, comment_items: List[Dict[str, Any]]) -> bool:
        """存储评论数据"""
        pass

    @abstractmethod
    async def store_creators(self, creator_items: List[Dict[str, Any]]) -> bool:
        """存储创作者数据"""
        pass

    @abstractmethod
    async def store_media(self, media_items: List[Dict[str, Any]]) -> bool:
        """存储媒体文件"""
        pass

    @abstractmethod
    async def get_stored_content(self, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """获取已存储的内容"""
        pass


class AbstractApiClient(ABC):
    """抽象API客户端基类"""

    def __init__(self, platform: PlatformType, base_url: str = None):
        self.platform = platform
        self.base_url = base_url
        self.headers = {}
        self.cookies = {}

    @abstractmethod
    async def request(self, method: str, url: str, **kwargs) -> Dict[str, Any]:
        """发送HTTP请求"""
        pass

    @abstractmethod
    async def get(self, url: str, **kwargs) -> Dict[str, Any]:
        """发送GET请求"""
        pass

    @abstractmethod
    async def post(self, url: str, **kwargs) -> Dict[str, Any]:
        """发送POST请求"""
        pass

    @abstractmethod
    async def update_cookies(self, browser_context: BrowserContext) -> None:
        """从浏览器上下文更新Cookie"""
        pass

    @abstractmethod
    async def update_headers(self, headers: Dict[str, str]) -> None:
        """更新请求头"""
        pass

    @abstractmethod
    async def close(self) -> None:
        """关闭客户端连接"""
        pass

    async def ping(self) -> bool:
        """测试连接是否正常"""
        try:
            response = await self.get("/")
            return response.get("status_code", 0) < 400
        except Exception:
            return False


class AbstractDataExtractor(ABC):
    """抽象数据提取器基类"""

    @abstractmethod
    async def extract_content_info(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """提取内容信息"""
        pass

    @abstractmethod
    async def extract_comment_info(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """提取评论信息"""
        pass

    @abstractmethod
    async def extract_creator_info(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """提取创作者信息"""
        pass

    @abstractmethod
    async def clean_text(self, text: str) -> str:
        """清理文本内容"""
        pass

    @abstractmethod
    async def extract_media_urls(self, raw_data: Dict[str, Any]) -> List[str]:
        """提取媒体文件URL"""
        pass 