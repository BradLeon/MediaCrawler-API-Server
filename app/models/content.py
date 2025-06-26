"""
内容模型
基类和各平台子类，兼容原MediaCrawler框架
"""

from sqlalchemy import Column, String, Text, Integer, BigInteger, JSON, Boolean, Index
from sqlalchemy.sql import func

from .base import Base


class ContentModel(Base):
    """内容模型基类 - 包含所有平台通用字段"""
    
    __abstract__ = True  # 抽象基类，不创建表
    
    # 通用基本信息
    user_id = Column(String(128), index=True, comment="用户ID")
    nickname = Column(String(64), comment="用户昵称")
    avatar = Column(String(255), comment="用户头像地址")
    ip_location = Column(String(255), comment="IP地理位置")
    
    # 内容信息
    title = Column(String(500), comment="标题")
    desc = Column(Text, comment="内容描述")
    
    # 时间信息 - 兼容原有时间戳格式
    add_ts = Column(BigInteger, default=func.extract('epoch', func.now()) * 1000, nullable=False, comment="记录添加时间戳")
    last_modify_ts = Column(BigInteger, default=func.extract('epoch', func.now()) * 1000, nullable=False, comment="记录最后修改时间戳")
    
    # 爬取信息
    task_id = Column(String(50), index=True, comment="任务ID")
    source_keyword = Column(String(255), default='', comment="搜索来源关键字")
    
    def __repr__(self):
        return f"<{self.__class__.__name__}(id={self.id}, title={self.title[:30] if self.title else 'N/A'}...)>"


class XhsContentModel(ContentModel):
    """小红书内容模型 - 兼容xhs_note表结构"""
    
    __tablename__ = "xhs_note"
    
    # 小红书特有字段 - 完全兼容原schema
    note_id = Column(String(64), unique=True, nullable=False, index=True, comment="笔记ID")
    type = Column(String(16), default="normal", comment="笔记类型(normal | video)")
    video_url = Column(Text, comment="视频地址")
    time = Column(BigInteger, nullable=False, index=True, comment="笔记发布时间戳")
    last_update_time = Column(BigInteger, nullable=False, comment="笔记最后更新时间戳")
    
    # 互动数据
    liked_count = Column(String(16), comment="笔记点赞数")
    collected_count = Column(String(16), comment="笔记收藏数")
    comment_count = Column(String(16), comment="笔记评论数")
    share_count = Column(String(16), comment="笔记分享数")
    
    # 媒体信息
    image_list = Column(Text, comment="笔记封面图片列表")
    tag_list = Column(Text, comment="标签列表")
    note_url = Column(String(255), comment="笔记详情页的URL")
    
    # 索引
    __table_args__ = (
        Index('idx_xhs_note_note_id_209457', 'note_id'),
        Index('idx_xhs_note_time_eaa910', 'time'),
    )


class DouyinContentModel(ContentModel):
    """抖音内容模型 - 兼容douyin_aweme表结构"""
    
    __tablename__ = "douyin_aweme"
    
    # 抖音特有字段 - 完全兼容原schema
    sec_uid = Column(String(128), comment="用户sec_uid")
    short_user_id = Column(String(64), comment="用户短ID")
    user_unique_id = Column(String(64), comment="用户唯一ID")
    user_signature = Column(String(500), comment="用户签名")
    
    aweme_id = Column(String(64), unique=True, nullable=False, index=True, comment="视频ID")
    aweme_type = Column(String(16), nullable=False, comment="视频类型")
    create_time = Column(BigInteger, nullable=False, index=True, comment="视频发布时间戳")
    
    # 互动数据
    liked_count = Column(String(16), comment="视频点赞数")
    comment_count = Column(String(16), comment="视频评论数")
    share_count = Column(String(16), comment="视频分享数")
    collected_count = Column(String(16), comment="视频收藏数")
    
    aweme_url = Column(String(255), comment="视频详情页URL")
    
    # 索引
    __table_args__ = (
        Index('idx_douyin_awem_aweme_i_6f7bc6', 'aweme_id'),
        Index('idx_douyin_awem_create__299dfe', 'create_time'),
    )


class BilibiliContentModel(ContentModel):
    """B站内容模型 - 兼容bilibili_video表结构"""
    
    __tablename__ = "bilibili_video"
    
    # B站特有字段 - 完全兼容原schema
    video_id = Column(String(64), unique=True, nullable=False, index=True, comment="视频ID")
    video_type = Column(String(16), nullable=False, comment="视频类型")
    create_time = Column(BigInteger, nullable=False, index=True, comment="视频发布时间戳")
    
    # 互动数据
    liked_count = Column(String(16), comment="视频点赞数")
    video_play_count = Column(String(16), comment="视频播放数量")
    video_danmaku = Column(String(16), comment="视频弹幕数量")
    video_comment = Column(String(16), comment="视频评论数量")
    
    video_url = Column(String(512), comment="视频详情URL")
    video_cover_url = Column(String(512), comment="视频封面图 URL")
    
    # 索引
    __table_args__ = (
        Index('idx_bilibili_vi_video_i_31c36e', 'video_id'),
        Index('idx_bilibili_vi_create__73e0ec', 'create_time'),
    )


class KuaishouContentModel(ContentModel):
    """快手内容模型 - 兼容kuaishou_video表结构"""
    
    __tablename__ = "kuaishou_video"
    
    # 快手特有字段 - 完全兼容原schema
    video_id = Column(String(64), unique=True, nullable=False, index=True, comment="视频ID")
    video_type = Column(String(16), nullable=False, comment="视频类型")
    create_time = Column(BigInteger, nullable=False, index=True, comment="视频发布时间戳")
    
    # 互动数据
    liked_count = Column(String(16), comment="视频点赞数")
    viewd_count = Column(String(16), comment="视频浏览数量")
    
    video_url = Column(String(512), comment="视频详情URL")
    video_cover_url = Column(String(512), comment="视频封面图 URL")
    video_play_url = Column(String(512), comment="视频播放 URL")
    
    # 索引
    __table_args__ = (
        Index('idx_kuaishou_vi_video_i_c5c6a6', 'video_id'),
        Index('idx_kuaishou_vi_create__a10dee', 'create_time'),
    )


class WeiboContentModel(ContentModel):
    """微博内容模型 - 兼容weibo_note表结构"""
    
    __tablename__ = "weibo_note"
    
    # 微博特有字段 - 根据原schema结构添加
    note_id = Column(String(64), unique=True, nullable=False, index=True, comment="微博ID")
    create_time = Column(BigInteger, nullable=False, index=True, comment="微博发布时间戳")
    
    # 互动数据
    liked_count = Column(String(16), comment="点赞数")
    comment_count = Column(String(16), comment="评论数")
    share_count = Column(String(16), comment="转发数")
    
    # 索引
    __table_args__ = (
        Index('idx_weibo_note_note_id', 'note_id'),
        Index('idx_weibo_note_create_time', 'create_time'),
    )


class TiebaContentModel(ContentModel):
    """贴吧内容模型 - 兼容tieba_note表结构"""
    
    __tablename__ = "tieba_note"
    
    # 贴吧特有字段 - 完全兼容原schema
    note_id = Column(String(644), unique=True, nullable=False, index=True, comment="帖子ID")
    note_url = Column(String(255), nullable=False, comment="帖子链接")
    publish_time = Column(String(255), nullable=False, index=True, comment="发布时间")
    
    user_link = Column(String(255), default='', comment="用户主页链接")
    
    # 贴吧信息
    tieba_id = Column(String(255), default='', comment="贴吧ID")
    tieba_name = Column(String(255), nullable=False, comment="贴吧名称")
    tieba_link = Column(String(255), nullable=False, comment="贴吧链接")
    
    # 回复信息
    total_replay_num = Column(Integer, default=0, comment="帖子回复总数")
    total_replay_page = Column(Integer, default=0, comment="帖子回复总页数")
    
    # 索引
    __table_args__ = (
        Index('idx_tieba_note_note_id', 'note_id'),
        Index('idx_tieba_note_publish_time', 'publish_time'),
    )


class ZhihuContentModel(ContentModel):
    """知乎内容模型 - 兼容zhihu_content表结构"""
    
    __tablename__ = "zhihu_content"
    
    # 知乎特有字段 - 根据原schema结构
    content_id = Column(String(64), unique=True, nullable=False, index=True, comment="内容ID")
    content_type = Column(String(16), nullable=False, comment="内容类型(article | answer | zvideo)")
    create_time = Column(BigInteger, nullable=False, index=True, comment="发布时间戳")
    
    # 知乎特有字段
    question_id = Column(String(64), comment="问题ID")
    answer_id = Column(String(64), comment="回答ID")
    
    # 互动数据
    liked_count = Column(String(16), comment="点赞数")
    comment_count = Column(String(16), comment="评论数")
    
    # 索引
    __table_args__ = (
        Index('idx_zhihu_content_id', 'content_id'),
        Index('idx_zhihu_create_time', 'create_time'),
    ) 