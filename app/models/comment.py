"""
评论模型
基类和各平台子类，兼容原MediaCrawler框架
"""

from sqlalchemy import Column, String, Text, Integer, BigInteger, Index
from sqlalchemy.sql import func

from .base import Base


class CommentModel(Base):
    """评论模型基类 - 包含所有平台通用字段"""
    
    __abstract__ = True  # 抽象基类，不创建表
    
    # 通用字段
    user_id = Column(String(128), index=True, comment="用户ID")
    nickname = Column(String(64), comment="用户昵称")
    avatar = Column(String(255), comment="用户头像地址")
    ip_location = Column(String(255), comment="IP地理位置")
    
    # 评论内容
    content = Column(Text, nullable=False, comment="评论内容")
    
    # 时间信息 - 兼容原有时间戳格式
    add_ts = Column(BigInteger, default=func.extract('epoch', func.now()) * 1000, nullable=False, comment="记录添加时间戳")
    last_modify_ts = Column(BigInteger, default=func.extract('epoch', func.now()) * 1000, nullable=False, comment="记录最后修改时间戳")
    
    # 评论层级
    sub_comment_count = Column(Integer, default=0, comment="子评论数量")
    parent_comment_id = Column(String(64), comment="父评论ID")
    
    def __repr__(self):
        return f"<{self.__class__.__name__}(id={self.id}, content={self.content[:30]}...)>"


class XhsCommentModel(CommentModel):
    """小红书评论模型 - 兼容xhs_note_comment表结构"""
    
    __tablename__ = "xhs_note_comment"
    
    # 小红书特有字段 - 完全兼容原schema
    comment_id = Column(String(64), unique=True, nullable=False, index=True, comment="评论ID")
    note_id = Column(String(64), nullable=False, index=True, comment="笔记ID")
    create_time = Column(BigInteger, nullable=False, index=True, comment="评论时间戳")
    
    pictures = Column(String(512), comment="评论图片")
    like_count = Column(String(64), comment="评论点赞数量")
    
    # 索引
    __table_args__ = (
        Index('idx_xhs_note_co_comment_8e8349', 'comment_id'),
        Index('idx_xhs_note_co_create__204f8d', 'create_time'),
    )


class DouyinCommentModel(CommentModel):
    """抖音评论模型 - 兼容douyin_aweme_comment表结构"""
    
    __tablename__ = "douyin_aweme_comment"
    
    # 抖音特有字段 - 完全兼容原schema
    sec_uid = Column(String(128), comment="用户sec_uid")
    short_user_id = Column(String(64), comment="用户短ID")
    user_unique_id = Column(String(64), comment="用户唯一ID")
    user_signature = Column(String(500), comment="用户签名")
    
    comment_id = Column(String(64), unique=True, nullable=False, index=True, comment="评论ID")
    aweme_id = Column(String(64), nullable=False, index=True, comment="视频ID")
    create_time = Column(BigInteger, nullable=False, index=True, comment="评论时间戳")
    
    # 索引
    __table_args__ = (
        Index('idx_douyin_awem_comment_fcd7e4', 'comment_id'),
        Index('idx_douyin_awem_aweme_i_c50049', 'aweme_id'),
    )


class BilibiliCommentModel(CommentModel):
    """B站评论模型 - 兼容bilibili_video_comment表结构"""
    
    __tablename__ = "bilibili_video_comment"
    
    # B站特有字段 - 完全兼容原schema
    comment_id = Column(String(64), unique=True, nullable=False, index=True, comment="评论ID")
    video_id = Column(String(64), nullable=False, index=True, comment="视频ID")
    create_time = Column(BigInteger, nullable=False, index=True, comment="评论时间戳")
    
    # 索引
    __table_args__ = (
        Index('idx_bilibili_vi_comment_41c34e', 'comment_id'),
        Index('idx_bilibili_vi_video_i_f22873', 'video_id'),
    )


class KuaishouCommentModel(CommentModel):
    """快手评论模型 - 兼容kuaishou_video_comment表结构"""
    
    __tablename__ = "kuaishou_video_comment"
    
    # 快手特有字段 - 完全兼容原schema
    comment_id = Column(String(64), unique=True, nullable=False, index=True, comment="评论ID")
    video_id = Column(String(64), nullable=False, index=True, comment="视频ID")
    create_time = Column(BigInteger, nullable=False, index=True, comment="评论时间戳")
    
    # 索引
    __table_args__ = (
        Index('idx_kuaishou_vi_comment_ed48fa', 'comment_id'),
        Index('idx_kuaishou_vi_video_i_e50914', 'video_id'),
    )


class WeiboCommentModel(CommentModel):
    """微博评论模型 - 兼容weibo_note_comment表结构"""
    
    __tablename__ = "weibo_note_comment"
    
    # 微博特有字段 - 根据原schema结构
    comment_id = Column(String(64), unique=True, nullable=False, index=True, comment="评论ID")
    note_id = Column(String(64), nullable=False, index=True, comment="微博ID")
    create_time = Column(BigInteger, nullable=False, index=True, comment="评论时间戳")
    
    # 索引
    __table_args__ = (
        Index('idx_weibo_comment_id', 'comment_id'),
        Index('idx_weibo_note_id', 'note_id'),
    )


class TiebaCommentModel(CommentModel):
    """贴吧评论模型 - 兼容tieba_comment表结构"""
    
    __tablename__ = "tieba_comment"
    
    # 贴吧特有字段 - 完全兼容原schema
    comment_id = Column(String(255), unique=True, nullable=False, index=True, comment="评论ID")
    note_id = Column(String(255), nullable=False, index=True, comment="帖子ID")
    note_url = Column(String(255), nullable=False, comment="帖子链接")
    
    user_link = Column(String(255), default='', comment="用户主页链接")
    
    # 贴吧信息
    tieba_id = Column(String(255), default='', comment="贴吧ID")
    tieba_name = Column(String(255), nullable=False, comment="贴吧名称")
    tieba_link = Column(String(255), nullable=False, comment="贴吧链接")
    
    publish_time = Column(String(255), default='', index=True, comment="发布时间")
    
    # 索引
    __table_args__ = (
        Index('idx_tieba_comment_comment_id', 'comment_id'),
        Index('idx_tieba_comment_note_id', 'note_id'),
        Index('idx_tieba_comment_publish_time', 'publish_time'),
    )


class ZhihuCommentModel(CommentModel):
    """知乎评论模型 - 兼容zhihu_comment表结构"""
    
    __tablename__ = "zhihu_comment"
    
    # 知乎特有字段 - 根据原schema结构
    comment_id = Column(String(64), unique=True, nullable=False, index=True, comment="评论ID")
    content_id = Column(String(64), nullable=False, index=True, comment="内容ID")
    create_time = Column(BigInteger, nullable=False, index=True, comment="评论时间戳")
    
    # 索引
    __table_args__ = (
        Index('idx_zhihu_comment_id', 'comment_id'),
        Index('idx_zhihu_content_id', 'content_id'),
    ) 