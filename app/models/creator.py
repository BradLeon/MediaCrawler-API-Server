"""
创作者模型
基类和各平台子类，兼容原MediaCrawler框架
"""

from sqlalchemy import Column, String, Text, Integer, BigInteger, Index
from sqlalchemy.sql import func

from .base import Base


class CreatorModel(Base):
    """创作者模型基类 - 包含所有平台通用字段"""
    
    __abstract__ = True  # 抽象基类，不创建表
    
    # 通用字段
    user_id = Column(String(128), nullable=False, index=True, comment="用户ID")
    nickname = Column(String(64), comment="用户昵称")
    avatar = Column(String(255), comment="用户头像地址")
    ip_location = Column(String(255), comment="IP地理位置")
    
    # 个人信息
    desc = Column(Text, comment="用户描述/个人简介")
    gender = Column(String(2), comment="性别")
    
    # 社交数据
    follows = Column(String(16), comment="关注数")
    fans = Column(String(16), comment="粉丝数")
    
    # 时间信息 - 兼容原有时间戳格式
    add_ts = Column(BigInteger, default=func.extract('epoch', func.now()) * 1000, nullable=False, comment="记录添加时间戳")
    last_modify_ts = Column(BigInteger, default=func.extract('epoch', func.now()) * 1000, nullable=False, comment="记录最后修改时间戳")
    
    def __repr__(self):
        return f"<{self.__class__.__name__}(id={self.id}, nickname={self.nickname})>"


class XhsCreatorModel(CreatorModel):
    """小红书创作者模型 - 兼容xhs_creator表结构"""
    
    __tablename__ = "xhs_creator"
    
    # 小红书特有字段 - 完全兼容原schema
    interaction = Column(String(16), comment="获赞和收藏数")
    tag_list = Column(Text, comment="标签列表")
    
    # 索引
    __table_args__ = (
        Index('idx_xhs_creator_user_id', 'user_id'),
    )


class DouyinCreatorModel(CreatorModel):
    """抖音创作者模型 - 兼容dy_creator表结构"""
    
    __tablename__ = "dy_creator"
    
    # 抖音特有字段 - 完全兼容原schema
    interaction = Column(String(16), comment="获赞数")
    videos_count = Column(String(16), comment="作品数")
    
    # 索引
    __table_args__ = (
        Index('idx_dy_creator_user_id', 'user_id'),
    )


class BilibiliCreatorModel(CreatorModel):
    """B站UP主模型 - 兼容bilibili_up_info表结构"""
    
    __tablename__ = "bilibili_up_info"
    
    # B站特有字段 - 完全兼容原schema
    total_fans = Column(BigInteger, comment="粉丝数")
    total_liked = Column(BigInteger, comment="总获赞数")
    user_rank = Column(Integer, comment="用户等级")
    is_official = Column(Integer, comment="是否官号")
    
    # 索引
    __table_args__ = (
        Index('idx_bilibili_vi_user_123456', 'user_id'),
    )


class WeiboCreatorModel(CreatorModel):
    """微博创作者模型 - 兼容weibo_creator表结构"""
    
    __tablename__ = "weibo_creator"
    
    # 微博特有字段 - 根据原schema结构
    tag_list = Column(Text, comment="标签列表")
    
    # 索引
    __table_args__ = (
        Index('idx_weibo_creator_user_id', 'user_id'),
    )


class TiebaCreatorModel(CreatorModel):
    """贴吧创作者模型 - 兼容tieba_creator表结构"""
    
    __tablename__ = "tieba_creator"
    
    # 贴吧特有字段 - 完全兼容原schema
    user_name = Column(String(64), nullable=False, comment="用户名")
    registration_duration = Column(String(16), comment="吧龄")
    
    # 索引
    __table_args__ = (
        Index('idx_tieba_creator_user_id', 'user_id'),
    )


class ZhihuCreatorModel(CreatorModel):
    """知乎创作者模型 - 兼容zhihu_creator表结构"""
    
    __tablename__ = "zhihu_creator"
    
    # 知乎特有字段 - 根据原schema结构
    # 可以根据需要添加知乎特有字段
    
    # 索引
    __table_args__ = (
        Index('idx_zhihu_creator_user_id', 'user_id'),
    ) 