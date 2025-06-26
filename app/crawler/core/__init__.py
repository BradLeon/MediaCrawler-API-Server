"""
爬虫引擎核心模块

提供爬虫引擎的核心功能：
- 基础抽象类定义
- 工厂模式实现
- 浏览器管理
- 代理管理
- 任务调度
- 数据提取
"""

from .base import AbstractCrawler, AbstractLogin, AbstractStore, AbstractApiClient



__all__ = [
    'AbstractCrawler', 'AbstractLogin', 'AbstractStore', 'AbstractApiClient',
] 