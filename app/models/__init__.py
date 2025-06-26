"""
数据模型包
包含所有数据库模型定义，兼容原MediaCrawler框架
"""

from .base import Base
from .task import TaskModel

# 内容模型
from .content import (
    ContentModel,
    XhsContentModel,
    DouyinContentModel, 
    BilibiliContentModel,
    KuaishouContentModel,
    WeiboContentModel,
    TiebaContentModel,
    ZhihuContentModel
)

# 评论模型
from .comment import (
    CommentModel,
    XhsCommentModel,
    DouyinCommentModel,
    BilibiliCommentModel,
    KuaishouCommentModel,
    WeiboCommentModel,
    TiebaCommentModel,
    ZhihuCommentModel
)

# 创作者模型
from .creator import (
    CreatorModel,
    XhsCreatorModel,
    DouyinCreatorModel,
    BilibiliCreatorModel,
    WeiboCreatorModel,
    TiebaCreatorModel,
    ZhihuCreatorModel
)

# 导出所有模型
__all__ = [
    "Base",
    "TaskModel",
    
    # 基类
    "ContentModel",
    "CommentModel", 
    "CreatorModel",
    
    # 小红书
    "XhsContentModel",
    "XhsCommentModel",
    "XhsCreatorModel",
    
    # 抖音
    "DouyinContentModel",
    "DouyinCommentModel",
    "DouyinCreatorModel",
    
    # B站
    "BilibiliContentModel",
    "BilibiliCommentModel",
    "BilibiliCreatorModel",
    
    # 快手
    "KuaishouContentModel",
    "KuaishouCommentModel",
    
    # 微博
    "WeiboContentModel",
    "WeiboCommentModel",
    "WeiboCreatorModel",
    
    # 贴吧
    "TiebaContentModel", 
    "TiebaCommentModel",
    "TiebaCreatorModel",
    
    # 知乎
    "ZhihuContentModel",
    "ZhihuCommentModel",
    "ZhihuCreatorModel",
]

# 平台模型映射 - 便于根据平台名获取对应的模型类
PLATFORM_MODELS = {
    "xhs": {
        "content": XhsContentModel,
        "comment": XhsCommentModel,
        "creator": XhsCreatorModel,
    },
    "douyin": {
        "content": DouyinContentModel,
        "comment": DouyinCommentModel,
        "creator": DouyinCreatorModel,
    },
    "bilibili": {
        "content": BilibiliContentModel,
        "comment": BilibiliCommentModel,
        "creator": BilibiliCreatorModel,
    },
    "kuaishou": {
        "content": KuaishouContentModel,
        "comment": KuaishouCommentModel,
    },
    "weibo": {
        "content": WeiboContentModel,
        "comment": WeiboCommentModel,
        "creator": WeiboCreatorModel,
    },
    "tieba": {
        "content": TiebaContentModel,
        "comment": TiebaCommentModel,
        "creator": TiebaCreatorModel,
    },
    "zhihu": {
        "content": ZhihuContentModel,
        "comment": ZhihuCommentModel,
        "creator": ZhihuCreatorModel,
    },
}

# 平台标识映射
PLATFORM_MAPPING = {
    "xhs": "小红书",
    "douyin": "抖音",
    "dy": "抖音",
    "bilibili": "B站",
    "bili": "B站",
    "kuaishou": "快手",
    "ks": "快手",
    "weibo": "微博",
    "wb": "微博",
    "tieba": "百度贴吧",
    "zhihu": "知乎",
}

def get_model_by_platform(platform: str, model_type: str):
    """
    根据平台和模型类型获取对应的模型类
    
    Args:
        platform: 平台标识 (xhs, douyin, bilibili等)
        model_type: 模型类型 (content, comment, creator)
    
    Returns:
        对应的模型类
    """
    return PLATFORM_MODELS.get(platform, {}).get(model_type)
