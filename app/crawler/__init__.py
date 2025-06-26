"""
MediaCrawler-ApiServer 爬虫引擎模块

该模块提供了多平台爬虫引擎的核心功能，包括：
- 适配器层：通过进程调用复用原MediaCrawler功能
- 核心组件：浏览器管理、代理管理、任务调度等占位符
- 平台支持：7个主流社交媒体平台

支持的平台：
- 小红书 (XHS)
- 抖音 (Douyin)  
- 哔哩哔哩 (Bilibili)
- 快手 (Kuaishou)
- 微博 (Weibo)
- 百度贴吧 (Tieba)
- 知乎 (Zhihu)

主要功能：
1. 关键词搜索爬取
2. 指定内容详情获取
3. 创作者主页数据爬取
4. 评论数据抓取
5. 媒体文件下载
"""

# 核心适配器 - 主要入口
from .adapter import crawler_adapter, MediaCrawlerAdapter, CrawlerTask, CrawlerTaskType, CrawlerResult

# 核心组件（基础抽象类）
from .core.base import AbstractCrawler, AbstractLogin, AbstractStore, AbstractApiClient
# 核心组件占位符（尚未实现）
# from .core.browser import BrowserManager
# from .core.proxy import ProxyManager  
# from .core.scheduler import TaskScheduler
# from .core.extractor import DataExtractor

# 平台登录实现
from .platforms.xhs_login import XhsLoginAdapter
from app.dataReader.base import PlatformType, DataSourceType

__all__ = [
    # 核心适配器
    'crawler_adapter', 'MediaCrawlerAdapter', 'CrawlerTask', 'CrawlerTaskType', 'CrawlerResult',
    
    # 基础抽象类
    'AbstractCrawler', 'AbstractLogin', 'AbstractStore', 'AbstractApiClient',
    
    # 平台登录
    'XhsLoginAdapter',
]

# 版本信息
__version__ = "1.0.0"
__author__ = "MediaCrawler-ApiServer Team"
__description__ = "Multi-platform social media crawler adapter"

# 支持的平台列表
SUPPORTED_PLATFORMS = [
    "xhs",       # 小红书
    "douyin",    # 抖音
    "bilibili",  # 哔哩哔哩
    "kuaishou",  # 快手
    "weibo",     # 微博
    "tieba",     # 百度贴吧
    "zhihu",     # 知乎
]

# 爬虫类型
CRAWLER_TYPES = [
    "search",    # 关键词搜索
    "detail",    # 指定内容详情
    "creator",   # 创作者主页
]

# 登录方式
LOGIN_TYPES = [
    "qrcode",    # 二维码登录
    "mobile",    # 手机号登录
    "cookie",    # Cookie登录
] 