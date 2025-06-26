"""
模型工厂类
用于管理不同平台的模型实例化和数据转换
"""

from typing import Dict, Any, Optional, Union, Type
from sqlalchemy.orm import Session

from . import (
    PLATFORM_MODELS,
    ContentModel, CommentModel, CreatorModel,
    XhsContentModel, DouyinContentModel, BilibiliContentModel,
    KuaishouContentModel, WeiboContentModel, TiebaContentModel, ZhihuContentModel
)


class ModelFactory:
    """模型工厂类"""
    
    @staticmethod
    def get_content_model(platform: str) -> Type[ContentModel]:
        """获取指定平台的内容模型类"""
        model_class = PLATFORM_MODELS.get(platform, {}).get("content")
        if not model_class:
            raise ValueError(f"Unsupported platform for content: {platform}")
        return model_class
    
    @staticmethod
    def get_comment_model(platform: str) -> Type[CommentModel]:
        """获取指定平台的评论模型类"""
        model_class = PLATFORM_MODELS.get(platform, {}).get("comment")
        if not model_class:
            raise ValueError(f"Unsupported platform for comment: {platform}")
        return model_class
    
    @staticmethod
    def get_creator_model(platform: str) -> Type[CreatorModel]:
        """获取指定平台的创作者模型类"""
        model_class = PLATFORM_MODELS.get(platform, {}).get("creator")
        if not model_class:
            raise ValueError(f"Unsupported platform for creator: {platform}")
        return model_class
    
    @staticmethod
    def create_content_from_data(platform: str, data: Dict[str, Any]) -> ContentModel:
        """从数据字典创建内容模型实例"""
        model_class = ModelFactory.get_content_model(platform)
        instance = model_class()
        
        # 通用字段映射
        if "user_id" in data:
            instance.user_id = data["user_id"]
        if "nickname" in data:
            instance.nickname = data["nickname"]
        if "avatar" in data:
            instance.avatar = data["avatar"]
        if "ip_location" in data:
            instance.ip_location = data["ip_location"]
        if "title" in data:
            instance.title = data["title"]
        if "desc" in data:
            instance.desc = data["desc"]
        if "add_ts" in data:
            instance.add_ts = data["add_ts"]
        if "last_modify_ts" in data:
            instance.last_modify_ts = data["last_modify_ts"]
        if "task_id" in data:
            instance.task_id = data["task_id"]
        if "source_keyword" in data:
            instance.source_keyword = data["source_keyword"]
        
        # 平台特定字段映射
        if platform == "xhs":
            _map_xhs_content_fields(instance, data)
        elif platform == "douyin":
            _map_douyin_content_fields(instance, data)
        elif platform == "bilibili":
            _map_bilibili_content_fields(instance, data)
        elif platform == "kuaishou":
            _map_kuaishou_content_fields(instance, data)
        elif platform == "weibo":
            _map_weibo_content_fields(instance, data)
        elif platform == "tieba":
            _map_tieba_content_fields(instance, data)
        elif platform == "zhihu":
            _map_zhihu_content_fields(instance, data)
        
        return instance
    
    @staticmethod
    def create_comment_from_data(platform: str, data: Dict[str, Any]) -> CommentModel:
        """从数据字典创建评论模型实例"""
        model_class = ModelFactory.get_comment_model(platform)
        instance = model_class()
        
        # 通用字段映射
        if "user_id" in data:
            instance.user_id = data["user_id"]
        if "nickname" in data:
            instance.nickname = data["nickname"]
        if "avatar" in data:
            instance.avatar = data["avatar"]
        if "ip_location" in data:
            instance.ip_location = data["ip_location"]
        if "content" in data:
            instance.content = data["content"]
        if "add_ts" in data:
            instance.add_ts = data["add_ts"]
        if "last_modify_ts" in data:
            instance.last_modify_ts = data["last_modify_ts"]
        if "sub_comment_count" in data:
            instance.sub_comment_count = data["sub_comment_count"]
        if "parent_comment_id" in data:
            instance.parent_comment_id = data["parent_comment_id"]
        
        # 平台特定字段映射
        if platform == "xhs":
            _map_xhs_comment_fields(instance, data)
        elif platform == "douyin":
            _map_douyin_comment_fields(instance, data)
        elif platform == "bilibili":
            _map_bilibili_comment_fields(instance, data)
        elif platform == "kuaishou":
            _map_kuaishou_comment_fields(instance, data)
        elif platform == "weibo":
            _map_weibo_comment_fields(instance, data)
        elif platform == "tieba":
            _map_tieba_comment_fields(instance, data)
        elif platform == "zhihu":
            _map_zhihu_comment_fields(instance, data)
        
        return instance
    
    @staticmethod
    def create_creator_from_data(platform: str, data: Dict[str, Any]) -> CreatorModel:
        """从数据字典创建创作者模型实例"""
        model_class = ModelFactory.get_creator_model(platform)
        instance = model_class()
        
        # 通用字段映射
        if "user_id" in data:
            instance.user_id = data["user_id"]
        if "nickname" in data:
            instance.nickname = data["nickname"]
        if "avatar" in data:
            instance.avatar = data["avatar"]
        if "ip_location" in data:
            instance.ip_location = data["ip_location"]
        if "desc" in data:
            instance.desc = data["desc"]
        if "gender" in data:
            instance.gender = data["gender"]
        if "follows" in data:
            instance.follows = data["follows"]
        if "fans" in data:
            instance.fans = data["fans"]
        if "add_ts" in data:
            instance.add_ts = data["add_ts"]
        if "last_modify_ts" in data:
            instance.last_modify_ts = data["last_modify_ts"]
        
        # 平台特定字段映射
        if platform == "xhs":
            _map_xhs_creator_fields(instance, data)
        elif platform == "douyin":
            _map_douyin_creator_fields(instance, data)
        elif platform == "bilibili":
            _map_bilibili_creator_fields(instance, data)
        elif platform == "weibo":
            _map_weibo_creator_fields(instance, data)
        elif platform == "tieba":
            _map_tieba_creator_fields(instance, data)
        elif platform == "zhihu":
            _map_zhihu_creator_fields(instance, data)
        
        return instance


# 平台特定字段映射函数

def _map_xhs_content_fields(instance: XhsContentModel, data: Dict[str, Any]):
    """映射小红书内容特定字段"""
    if "note_id" in data:
        instance.note_id = data["note_id"]
    if "type" in data:
        instance.type = data["type"]
    if "video_url" in data:
        instance.video_url = data["video_url"]
    if "time" in data:
        instance.time = data["time"]
    if "last_update_time" in data:
        instance.last_update_time = data["last_update_time"]
    if "liked_count" in data:
        instance.liked_count = data["liked_count"]
    if "collected_count" in data:
        instance.collected_count = data["collected_count"]
    if "comment_count" in data:
        instance.comment_count = data["comment_count"]
    if "share_count" in data:
        instance.share_count = data["share_count"]
    if "image_list" in data:
        instance.image_list = data["image_list"]
    if "tag_list" in data:
        instance.tag_list = data["tag_list"]
    if "note_url" in data:
        instance.note_url = data["note_url"]


def _map_douyin_content_fields(instance: DouyinContentModel, data: Dict[str, Any]):
    """映射抖音内容特定字段"""
    if "sec_uid" in data:
        instance.sec_uid = data["sec_uid"]
    if "short_user_id" in data:
        instance.short_user_id = data["short_user_id"]
    if "user_unique_id" in data:
        instance.user_unique_id = data["user_unique_id"]
    if "user_signature" in data:
        instance.user_signature = data["user_signature"]
    if "aweme_id" in data:
        instance.aweme_id = data["aweme_id"]
    if "aweme_type" in data:
        instance.aweme_type = data["aweme_type"]
    if "create_time" in data:
        instance.create_time = data["create_time"]
    if "liked_count" in data:
        instance.liked_count = data["liked_count"]
    if "comment_count" in data:
        instance.comment_count = data["comment_count"]
    if "share_count" in data:
        instance.share_count = data["share_count"]
    if "collected_count" in data:
        instance.collected_count = data["collected_count"]
    if "aweme_url" in data:
        instance.aweme_url = data["aweme_url"]


def _map_bilibili_content_fields(instance: BilibiliContentModel, data: Dict[str, Any]):
    """映射B站内容特定字段"""
    if "video_id" in data:
        instance.video_id = data["video_id"]
    if "video_type" in data:
        instance.video_type = data["video_type"]
    if "create_time" in data:
        instance.create_time = data["create_time"]
    if "liked_count" in data:
        instance.liked_count = data["liked_count"]
    if "video_play_count" in data:
        instance.video_play_count = data["video_play_count"]
    if "video_danmaku" in data:
        instance.video_danmaku = data["video_danmaku"]
    if "video_comment" in data:
        instance.video_comment = data["video_comment"]
    if "video_url" in data:
        instance.video_url = data["video_url"]
    if "video_cover_url" in data:
        instance.video_cover_url = data["video_cover_url"]


def _map_kuaishou_content_fields(instance: KuaishouContentModel, data: Dict[str, Any]):
    """映射快手内容特定字段"""
    if "video_id" in data:
        instance.video_id = data["video_id"]
    if "video_type" in data:
        instance.video_type = data["video_type"]
    if "create_time" in data:
        instance.create_time = data["create_time"]
    if "liked_count" in data:
        instance.liked_count = data["liked_count"]
    if "viewd_count" in data:
        instance.viewd_count = data["viewd_count"]
    if "video_url" in data:
        instance.video_url = data["video_url"]
    if "video_cover_url" in data:
        instance.video_cover_url = data["video_cover_url"]
    if "video_play_url" in data:
        instance.video_play_url = data["video_play_url"]


def _map_weibo_content_fields(instance: WeiboContentModel, data: Dict[str, Any]):
    """映射微博内容特定字段"""
    if "note_id" in data:
        instance.note_id = data["note_id"]
    if "create_time" in data:
        instance.create_time = data["create_time"]
    if "liked_count" in data:
        instance.liked_count = data["liked_count"]
    if "comment_count" in data:
        instance.comment_count = data["comment_count"]
    if "share_count" in data:
        instance.share_count = data["share_count"]


def _map_tieba_content_fields(instance: TiebaContentModel, data: Dict[str, Any]):
    """映射贴吧内容特定字段"""
    if "note_id" in data:
        instance.note_id = data["note_id"]
    if "note_url" in data:
        instance.note_url = data["note_url"]
    if "publish_time" in data:
        instance.publish_time = data["publish_time"]
    if "user_link" in data:
        instance.user_link = data["user_link"]
    if "tieba_id" in data:
        instance.tieba_id = data["tieba_id"]
    if "tieba_name" in data:
        instance.tieba_name = data["tieba_name"]
    if "tieba_link" in data:
        instance.tieba_link = data["tieba_link"]
    if "total_replay_num" in data:
        instance.total_replay_num = data["total_replay_num"]
    if "total_replay_page" in data:
        instance.total_replay_page = data["total_replay_page"]


def _map_zhihu_content_fields(instance: ZhihuContentModel, data: Dict[str, Any]):
    """映射知乎内容特定字段"""
    if "content_id" in data:
        instance.content_id = data["content_id"]
    if "content_type" in data:
        instance.content_type = data["content_type"]
    if "create_time" in data:
        instance.create_time = data["create_time"]
    if "question_id" in data:
        instance.question_id = data["question_id"]
    if "answer_id" in data:
        instance.answer_id = data["answer_id"]
    if "liked_count" in data:
        instance.liked_count = data["liked_count"]
    if "comment_count" in data:
        instance.comment_count = data["comment_count"]


# 评论字段映射函数
def _map_xhs_comment_fields(instance, data: Dict[str, Any]):
    """映射小红书评论特定字段"""
    if "comment_id" in data:
        instance.comment_id = data["comment_id"]
    if "note_id" in data:
        instance.note_id = data["note_id"]
    if "create_time" in data:
        instance.create_time = data["create_time"]
    if "pictures" in data:
        instance.pictures = data["pictures"]
    if "like_count" in data:
        instance.like_count = data["like_count"]


def _map_douyin_comment_fields(instance, data: Dict[str, Any]):
    """映射抖音评论特定字段"""
    if "sec_uid" in data:
        instance.sec_uid = data["sec_uid"]
    if "short_user_id" in data:
        instance.short_user_id = data["short_user_id"]
    if "user_unique_id" in data:
        instance.user_unique_id = data["user_unique_id"]
    if "user_signature" in data:
        instance.user_signature = data["user_signature"]
    if "comment_id" in data:
        instance.comment_id = data["comment_id"]
    if "aweme_id" in data:
        instance.aweme_id = data["aweme_id"]
    if "create_time" in data:
        instance.create_time = data["create_time"]


def _map_bilibili_comment_fields(instance, data: Dict[str, Any]):
    """映射B站评论特定字段"""
    if "comment_id" in data:
        instance.comment_id = data["comment_id"]
    if "video_id" in data:
        instance.video_id = data["video_id"]
    if "create_time" in data:
        instance.create_time = data["create_time"]


def _map_kuaishou_comment_fields(instance, data: Dict[str, Any]):
    """映射快手评论特定字段"""
    if "comment_id" in data:
        instance.comment_id = data["comment_id"]
    if "video_id" in data:
        instance.video_id = data["video_id"]
    if "create_time" in data:
        instance.create_time = data["create_time"]


def _map_weibo_comment_fields(instance, data: Dict[str, Any]):
    """映射微博评论特定字段"""
    if "comment_id" in data:
        instance.comment_id = data["comment_id"]
    if "note_id" in data:
        instance.note_id = data["note_id"]
    if "create_time" in data:
        instance.create_time = data["create_time"]


def _map_tieba_comment_fields(instance, data: Dict[str, Any]):
    """映射贴吧评论特定字段"""
    if "comment_id" in data:
        instance.comment_id = data["comment_id"]
    if "note_id" in data:
        instance.note_id = data["note_id"]
    if "note_url" in data:
        instance.note_url = data["note_url"]
    if "user_link" in data:
        instance.user_link = data["user_link"]
    if "tieba_id" in data:
        instance.tieba_id = data["tieba_id"]
    if "tieba_name" in data:
        instance.tieba_name = data["tieba_name"]
    if "tieba_link" in data:
        instance.tieba_link = data["tieba_link"]
    if "publish_time" in data:
        instance.publish_time = data["publish_time"]


def _map_zhihu_comment_fields(instance, data: Dict[str, Any]):
    """映射知乎评论特定字段"""
    if "comment_id" in data:
        instance.comment_id = data["comment_id"]
    if "content_id" in data:
        instance.content_id = data["content_id"]
    if "create_time" in data:
        instance.create_time = data["create_time"]


# 创作者字段映射函数
def _map_xhs_creator_fields(instance, data: Dict[str, Any]):
    """映射小红书创作者特定字段"""
    if "interaction" in data:
        instance.interaction = data["interaction"]
    if "tag_list" in data:
        instance.tag_list = data["tag_list"]


def _map_douyin_creator_fields(instance, data: Dict[str, Any]):
    """映射抖音创作者特定字段"""
    if "interaction" in data:
        instance.interaction = data["interaction"]
    if "videos_count" in data:
        instance.videos_count = data["videos_count"]


def _map_bilibili_creator_fields(instance, data: Dict[str, Any]):
    """映射B站创作者特定字段"""
    if "total_fans" in data:
        instance.total_fans = data["total_fans"]
    if "total_liked" in data:
        instance.total_liked = data["total_liked"]
    if "user_rank" in data:
        instance.user_rank = data["user_rank"]
    if "is_official" in data:
        instance.is_official = data["is_official"]


def _map_weibo_creator_fields(instance, data: Dict[str, Any]):
    """映射微博创作者特定字段"""
    if "tag_list" in data:
        instance.tag_list = data["tag_list"]


def _map_tieba_creator_fields(instance, data: Dict[str, Any]):
    """映射贴吧创作者特定字段"""
    if "user_name" in data:
        instance.user_name = data["user_name"]
    if "registration_duration" in data:
        instance.registration_duration = data["registration_duration"]


def _map_zhihu_creator_fields(instance, data: Dict[str, Any]):
    """映射知乎创作者特定字段"""
    # 知乎创作者暂无特殊字段
    pass 