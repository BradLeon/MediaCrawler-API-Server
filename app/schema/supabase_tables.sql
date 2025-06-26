-- ======================================
-- Supabase PostgreSQL Tables Script
-- 适用于 MediaCrawler-ApiServer 项目
-- 基于原 MediaCrawler/schema/tables.sql 转换
-- ======================================

-- 启用必要的扩展
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ----------------------------
-- Table structure for bilibili_video
-- ----------------------------
DROP TABLE IF EXISTS bilibili_video CASCADE;
CREATE TABLE bilibili_video (
    id BIGSERIAL PRIMARY KEY,
    user_id VARCHAR(64) DEFAULT NULL,
    nickname VARCHAR(64) DEFAULT NULL,
    avatar VARCHAR(255) DEFAULT NULL,
    add_ts BIGINT NOT NULL,
    last_modify_ts BIGINT NOT NULL,
    video_id VARCHAR(64) NOT NULL,
    video_type VARCHAR(16) NOT NULL,
    title VARCHAR(500) DEFAULT NULL,
    "desc" TEXT DEFAULT NULL,
    create_time BIGINT NOT NULL,
    liked_count VARCHAR(16) DEFAULT NULL,
    video_play_count VARCHAR(16) DEFAULT NULL,
    video_danmaku VARCHAR(16) DEFAULT NULL,
    video_comment VARCHAR(16) DEFAULT NULL,
    video_url VARCHAR(512) DEFAULT NULL,
    video_cover_url VARCHAR(512) DEFAULT NULL,
    source_keyword VARCHAR(255) DEFAULT '',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 索引
CREATE INDEX idx_bilibili_video_video_id ON bilibili_video(video_id);
CREATE INDEX idx_bilibili_video_create_time ON bilibili_video(create_time);
CREATE INDEX idx_bilibili_video_add_ts ON bilibili_video(add_ts);

-- 注释
COMMENT ON TABLE bilibili_video IS 'B站视频';
COMMENT ON COLUMN bilibili_video.user_id IS '用户ID';
COMMENT ON COLUMN bilibili_video.nickname IS '用户昵称';
COMMENT ON COLUMN bilibili_video.avatar IS '用户头像地址';
COMMENT ON COLUMN bilibili_video.add_ts IS '记录添加时间戳';
COMMENT ON COLUMN bilibili_video.last_modify_ts IS '记录最后修改时间戳';
COMMENT ON COLUMN bilibili_video.video_id IS '视频ID';
COMMENT ON COLUMN bilibili_video.video_type IS '视频类型';
COMMENT ON COLUMN bilibili_video.title IS '视频标题';
COMMENT ON COLUMN bilibili_video."desc" IS '视频描述';
COMMENT ON COLUMN bilibili_video.create_time IS '视频发布时间戳';
COMMENT ON COLUMN bilibili_video.source_keyword IS '搜索来源关键字';

-- ----------------------------
-- Table structure for bilibili_video_comment
-- ----------------------------
DROP TABLE IF EXISTS bilibili_video_comment CASCADE;
CREATE TABLE bilibili_video_comment (
    id BIGSERIAL PRIMARY KEY,
    user_id VARCHAR(64) DEFAULT NULL,
    nickname VARCHAR(64) DEFAULT NULL,
    avatar VARCHAR(255) DEFAULT NULL,
    add_ts BIGINT NOT NULL,
    last_modify_ts BIGINT NOT NULL,
    comment_id VARCHAR(64) NOT NULL,
    video_id VARCHAR(64) NOT NULL,
    content TEXT DEFAULT NULL,
    create_time BIGINT NOT NULL,
    sub_comment_count VARCHAR(16) NOT NULL,
    parent_comment_id VARCHAR(64) DEFAULT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 索引
CREATE INDEX idx_bilibili_video_comment_comment_id ON bilibili_video_comment(comment_id);
CREATE INDEX idx_bilibili_video_comment_video_id ON bilibili_video_comment(video_id);
CREATE INDEX idx_bilibili_video_comment_create_time ON bilibili_video_comment(create_time);

-- 注释
COMMENT ON TABLE bilibili_video_comment IS 'B站视频评论';
COMMENT ON COLUMN bilibili_video_comment.parent_comment_id IS '父评论ID';

-- ----------------------------
-- Table structure for bilibili_up_info
-- ----------------------------
DROP TABLE IF EXISTS bilibili_up_info CASCADE;
CREATE TABLE bilibili_up_info (
    id BIGSERIAL PRIMARY KEY,
    user_id VARCHAR(64) DEFAULT NULL,
    nickname VARCHAR(64) DEFAULT NULL,
    avatar VARCHAR(255) DEFAULT NULL,
    add_ts BIGINT NOT NULL,
    last_modify_ts BIGINT NOT NULL,
    total_fans BIGINT DEFAULT NULL,
    total_liked BIGINT DEFAULT NULL,
    user_rank INTEGER DEFAULT NULL,
    is_official INTEGER DEFAULT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 索引
CREATE INDEX idx_bilibili_up_info_user_id ON bilibili_up_info(user_id);

-- 注释
COMMENT ON TABLE bilibili_up_info IS 'B站UP主信息';
COMMENT ON COLUMN bilibili_up_info.total_fans IS '粉丝数';
COMMENT ON COLUMN bilibili_up_info.total_liked IS '总获赞数';
COMMENT ON COLUMN bilibili_up_info.user_rank IS '用户等级';
COMMENT ON COLUMN bilibili_up_info.is_official IS '是否官号';

-- ----------------------------
-- Table structure for douyin_aweme
-- ----------------------------
DROP TABLE IF EXISTS douyin_aweme CASCADE;
CREATE TABLE douyin_aweme (
    id BIGSERIAL PRIMARY KEY,
    user_id VARCHAR(64) DEFAULT NULL,
    sec_uid VARCHAR(128) DEFAULT NULL,
    short_user_id VARCHAR(64) DEFAULT NULL,
    user_unique_id VARCHAR(64) DEFAULT NULL,
    nickname VARCHAR(64) DEFAULT NULL,
    avatar VARCHAR(255) DEFAULT NULL,
    user_signature VARCHAR(500) DEFAULT NULL,
    ip_location VARCHAR(255) DEFAULT NULL,
    add_ts BIGINT NOT NULL,
    last_modify_ts BIGINT NOT NULL,
    aweme_id VARCHAR(64) NOT NULL,
    aweme_type VARCHAR(16) NOT NULL,
    title VARCHAR(500) DEFAULT NULL,
    "desc" TEXT DEFAULT NULL,
    create_time BIGINT NOT NULL,
    liked_count VARCHAR(16) DEFAULT NULL,
    comment_count VARCHAR(16) DEFAULT NULL,
    share_count VARCHAR(16) DEFAULT NULL,
    collected_count VARCHAR(16) DEFAULT NULL,
    aweme_url VARCHAR(255) DEFAULT NULL,
    source_keyword VARCHAR(255) DEFAULT '',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 索引
CREATE INDEX idx_douyin_aweme_aweme_id ON douyin_aweme(aweme_id);
CREATE INDEX idx_douyin_aweme_create_time ON douyin_aweme(create_time);
CREATE INDEX idx_douyin_aweme_add_ts ON douyin_aweme(add_ts);

-- 注释
COMMENT ON TABLE douyin_aweme IS '抖音视频';
COMMENT ON COLUMN douyin_aweme.sec_uid IS '用户sec_uid';
COMMENT ON COLUMN douyin_aweme.short_user_id IS '用户短ID';
COMMENT ON COLUMN douyin_aweme.user_unique_id IS '用户唯一ID';
COMMENT ON COLUMN douyin_aweme.user_signature IS '用户签名';
COMMENT ON COLUMN douyin_aweme.ip_location IS '评论时的IP地址';
COMMENT ON COLUMN douyin_aweme.aweme_id IS '视频ID';
COMMENT ON COLUMN douyin_aweme.aweme_type IS '视频类型';
COMMENT ON COLUMN douyin_aweme.source_keyword IS '搜索来源关键字';

-- ----------------------------
-- Table structure for douyin_aweme_comment
-- ----------------------------
DROP TABLE IF EXISTS douyin_aweme_comment CASCADE;
CREATE TABLE douyin_aweme_comment (
    id BIGSERIAL PRIMARY KEY,
    user_id VARCHAR(64) DEFAULT NULL,
    sec_uid VARCHAR(128) DEFAULT NULL,
    short_user_id VARCHAR(64) DEFAULT NULL,
    user_unique_id VARCHAR(64) DEFAULT NULL,
    nickname VARCHAR(64) DEFAULT NULL,
    avatar VARCHAR(255) DEFAULT NULL,
    user_signature VARCHAR(500) DEFAULT NULL,
    ip_location VARCHAR(255) DEFAULT NULL,
    add_ts BIGINT NOT NULL,
    last_modify_ts BIGINT NOT NULL,
    comment_id VARCHAR(64) NOT NULL,
    aweme_id VARCHAR(64) NOT NULL,
    content TEXT DEFAULT NULL,
    create_time BIGINT NOT NULL,
    sub_comment_count VARCHAR(16) NOT NULL,
    parent_comment_id VARCHAR(64) DEFAULT NULL,
    like_count VARCHAR(255) NOT NULL DEFAULT '0',
    pictures VARCHAR(500) NOT NULL DEFAULT '',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 索引
CREATE INDEX idx_douyin_aweme_comment_comment_id ON douyin_aweme_comment(comment_id);
CREATE INDEX idx_douyin_aweme_comment_aweme_id ON douyin_aweme_comment(aweme_id);
CREATE INDEX idx_douyin_aweme_comment_create_time ON douyin_aweme_comment(create_time);

-- 注释
COMMENT ON TABLE douyin_aweme_comment IS '抖音视频评论';
COMMENT ON COLUMN douyin_aweme_comment.parent_comment_id IS '父评论ID';
COMMENT ON COLUMN douyin_aweme_comment.like_count IS '点赞数';
COMMENT ON COLUMN douyin_aweme_comment.pictures IS '评论图片列表';

-- ----------------------------
-- Table structure for dy_creator
-- ----------------------------
DROP TABLE IF EXISTS dy_creator CASCADE;
CREATE TABLE dy_creator (
    id BIGSERIAL PRIMARY KEY,
    user_id VARCHAR(128) NOT NULL,
    nickname VARCHAR(64) DEFAULT NULL,
    avatar VARCHAR(255) DEFAULT NULL,
    ip_location VARCHAR(255) DEFAULT NULL,
    add_ts BIGINT NOT NULL,
    last_modify_ts BIGINT NOT NULL,
    "desc" TEXT DEFAULT NULL,
    gender VARCHAR(1) DEFAULT NULL,
    follows VARCHAR(16) DEFAULT NULL,
    fans VARCHAR(16) DEFAULT NULL,
    interaction VARCHAR(16) DEFAULT NULL,
    videos_count VARCHAR(16) DEFAULT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 索引
CREATE INDEX idx_dy_creator_user_id ON dy_creator(user_id);

-- 注释
COMMENT ON TABLE dy_creator IS '抖音博主信息';
COMMENT ON COLUMN dy_creator."desc" IS '用户描述';
COMMENT ON COLUMN dy_creator.gender IS '性别';
COMMENT ON COLUMN dy_creator.follows IS '关注数';
COMMENT ON COLUMN dy_creator.fans IS '粉丝数';
COMMENT ON COLUMN dy_creator.interaction IS '获赞数';
COMMENT ON COLUMN dy_creator.videos_count IS '作品数';

-- ----------------------------
-- Table structure for kuaishou_video
-- ----------------------------
DROP TABLE IF EXISTS kuaishou_video CASCADE;
CREATE TABLE kuaishou_video (
    id BIGSERIAL PRIMARY KEY,
    user_id VARCHAR(64) DEFAULT NULL,
    nickname VARCHAR(64) DEFAULT NULL,
    avatar VARCHAR(255) DEFAULT NULL,
    add_ts BIGINT NOT NULL,
    last_modify_ts BIGINT NOT NULL,
    video_id VARCHAR(64) NOT NULL,
    video_type VARCHAR(16) NOT NULL,
    title VARCHAR(500) DEFAULT NULL,
    "desc" TEXT DEFAULT NULL,
    create_time BIGINT NOT NULL,
    liked_count VARCHAR(16) DEFAULT NULL,
    viewd_count VARCHAR(16) DEFAULT NULL,
    video_url VARCHAR(512) DEFAULT NULL,
    video_cover_url VARCHAR(512) DEFAULT NULL,
    video_play_url VARCHAR(512) DEFAULT NULL,
    source_keyword VARCHAR(255) DEFAULT '',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 索引
CREATE INDEX idx_kuaishou_video_video_id ON kuaishou_video(video_id);
CREATE INDEX idx_kuaishou_video_create_time ON kuaishou_video(create_time);
CREATE INDEX idx_kuaishou_video_add_ts ON kuaishou_video(add_ts);

-- 注释
COMMENT ON TABLE kuaishou_video IS '快手视频';
COMMENT ON COLUMN kuaishou_video.video_id IS '视频ID';
COMMENT ON COLUMN kuaishou_video.video_type IS '视频类型';
COMMENT ON COLUMN kuaishou_video.viewd_count IS '视频浏览数量';
COMMENT ON COLUMN kuaishou_video.video_play_url IS '视频播放URL';
COMMENT ON COLUMN kuaishou_video.source_keyword IS '搜索来源关键字';

-- ----------------------------
-- Table structure for kuaishou_video_comment
-- ----------------------------
DROP TABLE IF EXISTS kuaishou_video_comment CASCADE;
CREATE TABLE kuaishou_video_comment (
    id BIGSERIAL PRIMARY KEY,
    user_id VARCHAR(64) DEFAULT NULL,
    nickname VARCHAR(64) DEFAULT NULL,
    avatar VARCHAR(255) DEFAULT NULL,
    add_ts BIGINT NOT NULL,
    last_modify_ts BIGINT NOT NULL,
    comment_id VARCHAR(64) NOT NULL,
    video_id VARCHAR(64) NOT NULL,
    content TEXT DEFAULT NULL,
    create_time BIGINT NOT NULL,
    sub_comment_count VARCHAR(16) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 索引
CREATE INDEX idx_kuaishou_video_comment_comment_id ON kuaishou_video_comment(comment_id);
CREATE INDEX idx_kuaishou_video_comment_video_id ON kuaishou_video_comment(video_id);
CREATE INDEX idx_kuaishou_video_comment_create_time ON kuaishou_video_comment(create_time);

-- 注释
COMMENT ON TABLE kuaishou_video_comment IS '快手视频评论';

-- ----------------------------
-- Table structure for kuaishou_creator
-- ----------------------------
DROP TABLE IF EXISTS kuaishou_creator CASCADE;
CREATE TABLE kuaishou_creator (
    id BIGSERIAL PRIMARY KEY,
    user_id VARCHAR(64) NOT NULL,
    nickname VARCHAR(64) DEFAULT NULL,
    avatar VARCHAR(255) DEFAULT NULL,
    add_ts BIGINT NOT NULL,
    last_modify_ts BIGINT NOT NULL,
    "desc" TEXT DEFAULT NULL,
    gender VARCHAR(1) DEFAULT NULL,
    follows VARCHAR(16) DEFAULT NULL,
    fans VARCHAR(16) DEFAULT NULL,
    videos_count VARCHAR(16) DEFAULT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 索引
CREATE INDEX idx_kuaishou_creator_user_id ON kuaishou_creator(user_id);

-- 注释
COMMENT ON TABLE kuaishou_creator IS '快手创作者信息';

-- ----------------------------
-- Table structure for weibo_note
-- ----------------------------
DROP TABLE IF EXISTS weibo_note CASCADE;
CREATE TABLE weibo_note (
    id BIGSERIAL PRIMARY KEY,
    user_id VARCHAR(64) DEFAULT NULL,
    nickname VARCHAR(64) DEFAULT NULL,
    avatar VARCHAR(255) DEFAULT NULL,
    gender VARCHAR(12) DEFAULT NULL,
    profile_url VARCHAR(255) DEFAULT NULL,
    ip_location VARCHAR(32) DEFAULT NULL,
    add_ts BIGINT NOT NULL,
    last_modify_ts BIGINT NOT NULL,
    note_id VARCHAR(64) NOT NULL,
    content TEXT DEFAULT NULL,
    create_time BIGINT NOT NULL,
    create_date_time VARCHAR(32) NOT NULL,
    liked_count VARCHAR(16) DEFAULT NULL,
    comments_count VARCHAR(16) DEFAULT NULL,
    shared_count VARCHAR(16) DEFAULT NULL,
    note_url VARCHAR(512) DEFAULT NULL,
    source_keyword VARCHAR(255) DEFAULT '',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 索引
CREATE INDEX idx_weibo_note_note_id ON weibo_note(note_id);
CREATE INDEX idx_weibo_note_create_time ON weibo_note(create_time);
CREATE INDEX idx_weibo_note_create_date_time ON weibo_note(create_date_time);
CREATE INDEX idx_weibo_note_add_ts ON weibo_note(add_ts);

-- 注释
COMMENT ON TABLE weibo_note IS '微博帖子';
COMMENT ON COLUMN weibo_note.profile_url IS '用户主页地址';
COMMENT ON COLUMN weibo_note.ip_location IS '发布微博的地理信息';
COMMENT ON COLUMN weibo_note.note_id IS '帖子ID';
COMMENT ON COLUMN weibo_note.create_date_time IS '帖子发布日期时间';
COMMENT ON COLUMN weibo_note.source_keyword IS '搜索来源关键字';

-- ----------------------------
-- Table structure for weibo_note_comment
-- ----------------------------
DROP TABLE IF EXISTS weibo_note_comment CASCADE;
CREATE TABLE weibo_note_comment (
    id BIGSERIAL PRIMARY KEY,
    user_id VARCHAR(64) DEFAULT NULL,
    nickname VARCHAR(64) DEFAULT NULL,
    avatar VARCHAR(255) DEFAULT NULL,
    gender VARCHAR(12) DEFAULT NULL,
    profile_url VARCHAR(255) DEFAULT NULL,
    ip_location VARCHAR(32) DEFAULT NULL,
    add_ts BIGINT NOT NULL,
    last_modify_ts BIGINT NOT NULL,
    comment_id VARCHAR(64) NOT NULL,
    note_id VARCHAR(64) NOT NULL,
    content TEXT DEFAULT NULL,
    create_time BIGINT NOT NULL,
    create_date_time VARCHAR(32) NOT NULL,
    comment_like_count VARCHAR(16) NOT NULL,
    sub_comment_count VARCHAR(16) NOT NULL,
    parent_comment_id VARCHAR(64) DEFAULT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 索引
CREATE INDEX idx_weibo_note_comment_comment_id ON weibo_note_comment(comment_id);
CREATE INDEX idx_weibo_note_comment_note_id ON weibo_note_comment(note_id);
CREATE INDEX idx_weibo_note_comment_create_date_time ON weibo_note_comment(create_date_time);
CREATE INDEX idx_weibo_note_comment_create_time ON weibo_note_comment(create_time);

-- 注释
COMMENT ON TABLE weibo_note_comment IS '微博帖子评论';
COMMENT ON COLUMN weibo_note_comment.comment_like_count IS '评论点赞数量';
COMMENT ON COLUMN weibo_note_comment.parent_comment_id IS '父评论ID';

-- ----------------------------
-- Table structure for weibo_creator
-- ----------------------------
DROP TABLE IF EXISTS weibo_creator CASCADE;
CREATE TABLE weibo_creator (
    id BIGSERIAL PRIMARY KEY,
    user_id VARCHAR(64) NOT NULL,
    nickname VARCHAR(64) DEFAULT NULL,
    avatar VARCHAR(255) DEFAULT NULL,
    ip_location VARCHAR(255) DEFAULT NULL,
    add_ts BIGINT NOT NULL,
    last_modify_ts BIGINT NOT NULL,
    "desc" TEXT DEFAULT NULL,
    gender VARCHAR(2) DEFAULT NULL,
    follows VARCHAR(16) DEFAULT NULL,
    fans VARCHAR(16) DEFAULT NULL,
    tag_list TEXT DEFAULT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 索引
CREATE INDEX idx_weibo_creator_user_id ON weibo_creator(user_id);

-- 注释
COMMENT ON TABLE weibo_creator IS '微博博主';
COMMENT ON COLUMN weibo_creator.tag_list IS '标签列表';

-- ----------------------------
-- Table structure for xhs_note
-- ----------------------------
DROP TABLE IF EXISTS xhs_note CASCADE;
CREATE TABLE xhs_note (
    id BIGSERIAL PRIMARY KEY,
    user_id VARCHAR(64) NOT NULL,
    nickname VARCHAR(64) DEFAULT NULL,
    avatar VARCHAR(255) DEFAULT NULL,
    ip_location VARCHAR(255) DEFAULT NULL,
    add_ts BIGINT NOT NULL,
    last_modify_ts BIGINT NOT NULL,
    note_id VARCHAR(64) NOT NULL,
    "type" VARCHAR(16) DEFAULT NULL,
    title VARCHAR(255) DEFAULT NULL,
    "desc" TEXT DEFAULT NULL,
    video_url TEXT DEFAULT NULL,
    "time" BIGINT NOT NULL,
    last_update_time BIGINT NOT NULL,
    liked_count VARCHAR(16) DEFAULT NULL,
    collected_count VARCHAR(16) DEFAULT NULL,
    comment_count VARCHAR(16) DEFAULT NULL,
    share_count VARCHAR(16) DEFAULT NULL,
    image_list TEXT DEFAULT NULL,
    tag_list TEXT DEFAULT NULL,
    note_url VARCHAR(255) DEFAULT NULL,
    source_keyword VARCHAR(255) DEFAULT '',
    xsec_token VARCHAR(50) DEFAULT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 索引
CREATE INDEX idx_xhs_note_note_id ON xhs_note(note_id);
CREATE INDEX idx_xhs_note_time ON xhs_note("time");
CREATE INDEX idx_xhs_note_add_ts ON xhs_note(add_ts);

-- 注释
COMMENT ON TABLE xhs_note IS '小红书笔记';
COMMENT ON COLUMN xhs_note.note_id IS '笔记ID';
COMMENT ON COLUMN xhs_note."type" IS '笔记类型(normal | video)';
COMMENT ON COLUMN xhs_note."time" IS '笔记发布时间戳';
COMMENT ON COLUMN xhs_note.last_update_time IS '笔记最后更新时间戳';
COMMENT ON COLUMN xhs_note.image_list IS '笔记封面图片列表';
COMMENT ON COLUMN xhs_note.tag_list IS '标签列表';
COMMENT ON COLUMN xhs_note.source_keyword IS '搜索来源关键字';
COMMENT ON COLUMN xhs_note.xsec_token IS '签名算法';

-- ----------------------------
-- Table structure for xhs_note_comment
-- ----------------------------
DROP TABLE IF EXISTS xhs_note_comment CASCADE;
CREATE TABLE xhs_note_comment (
    id BIGSERIAL PRIMARY KEY,
    user_id VARCHAR(64) NOT NULL,
    nickname VARCHAR(64) DEFAULT NULL,
    avatar VARCHAR(255) DEFAULT NULL,
    ip_location VARCHAR(255) DEFAULT NULL,
    add_ts BIGINT NOT NULL,
    last_modify_ts BIGINT NOT NULL,
    comment_id VARCHAR(64) NOT NULL,
    create_time BIGINT NOT NULL,
    note_id VARCHAR(64) NOT NULL,
    content TEXT NOT NULL,
    sub_comment_count INTEGER NOT NULL,
    pictures VARCHAR(512) DEFAULT NULL,
    parent_comment_id VARCHAR(64) DEFAULT NULL,
    like_count VARCHAR(64) DEFAULT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 索引
CREATE INDEX idx_xhs_note_comment_comment_id ON xhs_note_comment(comment_id);
CREATE INDEX idx_xhs_note_comment_create_time ON xhs_note_comment(create_time);
CREATE INDEX idx_xhs_note_comment_note_id ON xhs_note_comment(note_id);

-- 注释
COMMENT ON TABLE xhs_note_comment IS '小红书笔记评论';
COMMENT ON COLUMN xhs_note_comment.parent_comment_id IS '父评论ID';
COMMENT ON COLUMN xhs_note_comment.like_count IS '评论点赞数量';

-- ----------------------------
-- Table structure for xhs_creator
-- ----------------------------
DROP TABLE IF EXISTS xhs_creator CASCADE;
CREATE TABLE xhs_creator (
    id BIGSERIAL PRIMARY KEY,
    user_id VARCHAR(64) NOT NULL,
    nickname VARCHAR(64) DEFAULT NULL,
    avatar VARCHAR(255) DEFAULT NULL,
    ip_location VARCHAR(255) DEFAULT NULL,
    add_ts BIGINT NOT NULL,
    last_modify_ts BIGINT NOT NULL,
    "desc" TEXT DEFAULT NULL,
    gender VARCHAR(1) DEFAULT NULL,
    follows VARCHAR(16) DEFAULT NULL,
    fans VARCHAR(16) DEFAULT NULL,
    interaction VARCHAR(16) DEFAULT NULL,
    tag_list TEXT DEFAULT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 索引
CREATE INDEX idx_xhs_creator_user_id ON xhs_creator(user_id);

-- 注释
COMMENT ON TABLE xhs_creator IS '小红书博主';
COMMENT ON COLUMN xhs_creator.interaction IS '获赞和收藏数';
COMMENT ON COLUMN xhs_creator.tag_list IS '标签列表';

-- ----------------------------
-- Table structure for tieba_note
-- ----------------------------
DROP TABLE IF EXISTS tieba_note CASCADE;
CREATE TABLE tieba_note (
    id BIGSERIAL PRIMARY KEY,
    note_id VARCHAR(644) NOT NULL,
    title VARCHAR(255) NOT NULL,
    "desc" TEXT DEFAULT NULL,
    note_url VARCHAR(255) NOT NULL,
    publish_time VARCHAR(255) NOT NULL,
    user_link VARCHAR(255) DEFAULT '',
    user_nickname VARCHAR(255) DEFAULT '',
    user_avatar VARCHAR(255) DEFAULT '',
    tieba_id VARCHAR(255) DEFAULT '',
    tieba_name VARCHAR(255) NOT NULL,
    tieba_link VARCHAR(255) NOT NULL,
    total_replay_num INTEGER DEFAULT 0,
    total_replay_page INTEGER DEFAULT 0,
    ip_location VARCHAR(255) DEFAULT '',
    add_ts BIGINT NOT NULL,
    last_modify_ts BIGINT NOT NULL,
    source_keyword VARCHAR(255) DEFAULT '',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 索引
CREATE INDEX idx_tieba_note_note_id ON tieba_note(note_id);
CREATE INDEX idx_tieba_note_publish_time ON tieba_note(publish_time);
CREATE INDEX idx_tieba_note_add_ts ON tieba_note(add_ts);

-- 注释
COMMENT ON TABLE tieba_note IS '贴吧帖子表';
COMMENT ON COLUMN tieba_note.note_id IS '帖子ID';
COMMENT ON COLUMN tieba_note.tieba_id IS '贴吧ID';
COMMENT ON COLUMN tieba_note.tieba_name IS '贴吧名称';
COMMENT ON COLUMN tieba_note.total_replay_num IS '帖子回复总数';
COMMENT ON COLUMN tieba_note.total_replay_page IS '帖子回复总页数';
COMMENT ON COLUMN tieba_note.source_keyword IS '搜索来源关键字';

-- ----------------------------
-- Table structure for tieba_comment
-- ----------------------------
DROP TABLE IF EXISTS tieba_comment CASCADE;
CREATE TABLE tieba_comment (
    id BIGSERIAL PRIMARY KEY,
    comment_id VARCHAR(255) NOT NULL,
    parent_comment_id VARCHAR(255) DEFAULT '',
    content TEXT NOT NULL,
    user_link VARCHAR(255) DEFAULT '',
    user_nickname VARCHAR(255) DEFAULT '',
    user_avatar VARCHAR(255) DEFAULT '',
    tieba_id VARCHAR(255) DEFAULT '',
    tieba_name VARCHAR(255) NOT NULL,
    tieba_link VARCHAR(255) NOT NULL,
    publish_time VARCHAR(255) DEFAULT '',
    ip_location VARCHAR(255) DEFAULT '',
    sub_comment_count INTEGER DEFAULT 0,
    note_id VARCHAR(255) NOT NULL,
    note_url VARCHAR(255) NOT NULL,
    add_ts BIGINT NOT NULL,
    last_modify_ts BIGINT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);



-- 索引
CREATE INDEX idx_tieba_comment_comment_id ON tieba_comment(comment_id);
CREATE INDEX idx_tieba_comment_note_id ON tieba_comment(note_id);
CREATE INDEX idx_tieba_comment_publish_time ON tieba_comment(publish_time);
CREATE INDEX idx_tieba_comment_add_ts ON tieba_comment(add_ts);

-- 注释
COMMENT ON TABLE tieba_comment IS '贴吧评论表';
COMMENT ON COLUMN tieba_comment.sub_comment_count IS '子评论数';

-- ----------------------------
-- Table structure for tieba_creator
-- ----------------------------
DROP TABLE IF EXISTS tieba_creator CASCADE;
CREATE TABLE tieba_creator (
    id BIGSERIAL PRIMARY KEY,
    user_id VARCHAR(64) NOT NULL,
    user_name VARCHAR(64) NOT NULL,
    nickname VARCHAR(64) DEFAULT NULL,
    avatar VARCHAR(255) DEFAULT NULL,
    ip_location VARCHAR(255) DEFAULT NULL,
    add_ts BIGINT NOT NULL,
    last_modify_ts BIGINT NOT NULL,
    gender VARCHAR(2) DEFAULT NULL,
    follows VARCHAR(16) DEFAULT NULL,
    fans VARCHAR(16) DEFAULT NULL,
    registration_duration VARCHAR(16) DEFAULT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 索引
CREATE INDEX idx_tieba_creator_user_id ON tieba_creator(user_id);

-- 注释
COMMENT ON TABLE tieba_creator IS '贴吧创作者';
COMMENT ON COLUMN tieba_creator.registration_duration IS '吧龄';

-- ----------------------------
-- Table structure for zhihu_note (renamed from zhihu_content)
-- ----------------------------
DROP TABLE IF EXISTS zhihu_note CASCADE;
CREATE TABLE zhihu_note (
    id BIGSERIAL PRIMARY KEY,
    note_id VARCHAR(64) NOT NULL,
    content_type VARCHAR(16) NOT NULL,
    content_text TEXT DEFAULT NULL,
    content_url VARCHAR(255) NOT NULL,
    question_id VARCHAR(64) DEFAULT NULL,
    title VARCHAR(255) NOT NULL,
    "desc" TEXT DEFAULT NULL,
    created_time VARCHAR(32) NOT NULL,
    updated_time VARCHAR(32) NOT NULL,
    voteup_count INTEGER NOT NULL DEFAULT 0,
    comment_count INTEGER NOT NULL DEFAULT 0,
    source_keyword VARCHAR(64) DEFAULT NULL,
    user_id VARCHAR(64) NOT NULL,
    user_link VARCHAR(255) NOT NULL,
    user_nickname VARCHAR(64) NOT NULL,
    user_avatar VARCHAR(255) NOT NULL,
    user_url_token VARCHAR(255) NOT NULL,
    add_ts BIGINT NOT NULL,
    last_modify_ts BIGINT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 索引
CREATE INDEX idx_zhihu_note_note_id ON zhihu_note(note_id);
CREATE INDEX idx_zhihu_note_created_time ON zhihu_note(created_time);
CREATE INDEX idx_zhihu_note_add_ts ON zhihu_note(add_ts);

-- 注释
COMMENT ON TABLE zhihu_note IS '知乎内容（回答、文章、视频）';
COMMENT ON COLUMN zhihu_note.note_id IS '内容ID';
COMMENT ON COLUMN zhihu_note.content_type IS '内容类型(article | answer | zvideo)';
COMMENT ON COLUMN zhihu_note.content_text IS '内容文本，如果是视频类型这里为空';
COMMENT ON COLUMN zhihu_note.question_id IS '问题ID，type为answer时有值';
COMMENT ON COLUMN zhihu_note.voteup_count IS '赞同人数';
COMMENT ON COLUMN zhihu_note.user_url_token IS '用户url_token';

-- ----------------------------
-- Table structure for zhihu_note_comment (renamed from zhihu_comment)
-- ----------------------------
DROP TABLE IF EXISTS zhihu_note_comment CASCADE;
CREATE TABLE zhihu_note_comment (
    id BIGSERIAL PRIMARY KEY,
    comment_id VARCHAR(64) NOT NULL,
    parent_comment_id VARCHAR(64) DEFAULT NULL,
    content TEXT NOT NULL,
    publish_time VARCHAR(32) NOT NULL,
    ip_location VARCHAR(64) DEFAULT NULL,
    sub_comment_count INTEGER NOT NULL DEFAULT 0,
    like_count INTEGER NOT NULL DEFAULT 0,
    dislike_count INTEGER NOT NULL DEFAULT 0,
    note_id VARCHAR(64) NOT NULL,
    content_type VARCHAR(16) NOT NULL,
    user_id VARCHAR(64) NOT NULL,
    user_link VARCHAR(255) NOT NULL,
    user_nickname VARCHAR(64) NOT NULL,
    user_avatar VARCHAR(255) NOT NULL,
    add_ts BIGINT NOT NULL,
    last_modify_ts BIGINT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 索引
CREATE INDEX idx_zhihu_note_comment_comment_id ON zhihu_note_comment(comment_id);
CREATE INDEX idx_zhihu_note_comment_note_id ON zhihu_note_comment(note_id);
CREATE INDEX idx_zhihu_note_comment_publish_time ON zhihu_note_comment(publish_time);
CREATE INDEX idx_zhihu_note_comment_add_ts ON zhihu_note_comment(add_ts);

-- 注释
COMMENT ON TABLE zhihu_note_comment IS '知乎评论';
COMMENT ON COLUMN zhihu_note_comment.note_id IS '内容ID';
COMMENT ON COLUMN zhihu_note_comment.content_type IS '内容类型(article | answer | zvideo)';
COMMENT ON COLUMN zhihu_note_comment.dislike_count IS '踩数';

-- ----------------------------
-- Table structure for zhihu_creator
-- ----------------------------
DROP TABLE IF EXISTS zhihu_creator CASCADE;
CREATE TABLE zhihu_creator (
    id BIGSERIAL PRIMARY KEY,
    user_id VARCHAR(64) NOT NULL,
    user_link VARCHAR(255) NOT NULL,
    user_nickname VARCHAR(64) NOT NULL,
    user_avatar VARCHAR(255) NOT NULL,
    url_token VARCHAR(64) NOT NULL,
    gender VARCHAR(16) DEFAULT NULL,
    ip_location VARCHAR(64) DEFAULT NULL,
    follows INTEGER NOT NULL DEFAULT 0,
    fans INTEGER NOT NULL DEFAULT 0,
    anwser_count INTEGER NOT NULL DEFAULT 0,
    video_count INTEGER NOT NULL DEFAULT 0,
    question_count INTEGER NOT NULL DEFAULT 0,
    article_count INTEGER NOT NULL DEFAULT 0,
    column_count INTEGER NOT NULL DEFAULT 0,
    get_voteup_count INTEGER NOT NULL DEFAULT 0,
    add_ts BIGINT NOT NULL,
    last_modify_ts BIGINT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 索引
CREATE UNIQUE INDEX idx_zhihu_creator_user_id ON zhihu_creator(user_id);

-- 注释
COMMENT ON TABLE zhihu_creator IS '知乎创作者';
COMMENT ON COLUMN zhihu_creator.url_token IS '用户URL Token';
COMMENT ON COLUMN zhihu_creator.anwser_count IS '回答数';
COMMENT ON COLUMN zhihu_creator.question_count IS '问题数';
COMMENT ON COLUMN zhihu_creator.article_count IS '文章数';
COMMENT ON COLUMN zhihu_creator.column_count IS '专栏数';
COMMENT ON COLUMN zhihu_creator.get_voteup_count IS '获得的赞同数';

-- ======================================
-- 创建触发器函数用于自动更新updated_at字段
-- ======================================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- 为所有表添加updated_at触发器
CREATE TRIGGER update_bilibili_video_updated_at BEFORE UPDATE ON bilibili_video FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_bilibili_video_comment_updated_at BEFORE UPDATE ON bilibili_video_comment FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_bilibili_up_info_updated_at BEFORE UPDATE ON bilibili_up_info FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_douyin_aweme_updated_at BEFORE UPDATE ON douyin_aweme FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_douyin_aweme_comment_updated_at BEFORE UPDATE ON douyin_aweme_comment FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_dy_creator_updated_at BEFORE UPDATE ON dy_creator FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_kuaishou_video_updated_at BEFORE UPDATE ON kuaishou_video FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_kuaishou_video_comment_updated_at BEFORE UPDATE ON kuaishou_video_comment FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_kuaishou_creator_updated_at BEFORE UPDATE ON kuaishou_creator FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_weibo_note_updated_at BEFORE UPDATE ON weibo_note FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_weibo_note_comment_updated_at BEFORE UPDATE ON weibo_note_comment FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_weibo_creator_updated_at BEFORE UPDATE ON weibo_creator FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_xhs_note_updated_at BEFORE UPDATE ON xhs_note FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_xhs_note_comment_updated_at BEFORE UPDATE ON xhs_note_comment FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_xhs_creator_updated_at BEFORE UPDATE ON xhs_creator FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_tieba_note_updated_at BEFORE UPDATE ON tieba_note FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_tieba_comment_updated_at BEFORE UPDATE ON tieba_comment FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_tieba_creator_updated_at BEFORE UPDATE ON tieba_creator FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_zhihu_note_updated_at BEFORE UPDATE ON zhihu_note FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_zhihu_note_comment_updated_at BEFORE UPDATE ON zhihu_note_comment FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_zhihu_creator_updated_at BEFORE UPDATE ON zhihu_creator FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ======================================
-- 创建RLS (Row Level Security) 策略示例
-- ======================================

-- 启用RLS (可选，根据需要开启)
-- ALTER TABLE bilibili_video ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE douyin_aweme ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE kuaishou_video ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE weibo_note ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE xhs_note ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE tieba_note ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE zhihu_note ENABLE ROW LEVEL SECURITY;

-- 创建策略示例 (可选)
-- CREATE POLICY "Users can read all content" ON bilibili_video FOR SELECT USING (true);
-- CREATE POLICY "Service role can manage content" ON bilibili_video FOR ALL USING (auth.role() = 'service_role');

-- ======================================
-- 优化设置
-- ======================================

-- 创建复合索引以优化查询性能
CREATE INDEX idx_bilibili_video_user_create ON bilibili_video(user_id, create_time);
CREATE INDEX idx_douyin_aweme_user_create ON douyin_aweme(user_id, create_time);
CREATE INDEX idx_kuaishou_video_user_create ON kuaishou_video(user_id, create_time);
CREATE INDEX idx_weibo_note_user_create ON weibo_note(user_id, create_time);
CREATE INDEX idx_xhs_note_user_time ON xhs_note(user_id, "time");
CREATE INDEX idx_tieba_note_user_publish ON tieba_note(user_nickname, publish_time);
CREATE INDEX idx_zhihu_note_user_created ON zhihu_note(user_id, created_time);

-- 评论表的复合索引
CREATE INDEX idx_bilibili_comment_video_create ON bilibili_video_comment(video_id, create_time);
CREATE INDEX idx_douyin_comment_aweme_create ON douyin_aweme_comment(aweme_id, create_time);
CREATE INDEX idx_kuaishou_comment_video_create ON kuaishou_video_comment(video_id, create_time);
CREATE INDEX idx_weibo_comment_note_create ON weibo_note_comment(note_id, create_time);
CREATE INDEX idx_xhs_comment_note_create ON xhs_note_comment(note_id, create_time);
CREATE INDEX idx_tieba_comment_note_publish ON tieba_comment(note_id, publish_time);
CREATE INDEX idx_zhihu_comment_note_publish ON zhihu_note_comment(note_id, publish_time);

-- ======================================
-- 数据完整性约束
-- ======================================

-- 添加检查约束
ALTER TABLE bilibili_video ADD CONSTRAINT chk_bilibili_video_add_ts CHECK (add_ts > 0);
ALTER TABLE bilibili_video ADD CONSTRAINT chk_bilibili_video_last_modify_ts CHECK (last_modify_ts > 0);
ALTER TABLE bilibili_video ADD CONSTRAINT chk_bilibili_video_create_time CHECK (create_time > 0);

ALTER TABLE douyin_aweme ADD CONSTRAINT chk_douyin_aweme_add_ts CHECK (add_ts > 0);
ALTER TABLE douyin_aweme ADD CONSTRAINT chk_douyin_aweme_last_modify_ts CHECK (last_modify_ts > 0);
ALTER TABLE douyin_aweme ADD CONSTRAINT chk_douyin_aweme_create_time CHECK (create_time > 0);

ALTER TABLE kuaishou_video ADD CONSTRAINT chk_kuaishou_video_add_ts CHECK (add_ts > 0);
ALTER TABLE kuaishou_video ADD CONSTRAINT chk_kuaishou_video_last_modify_ts CHECK (last_modify_ts > 0);
ALTER TABLE kuaishou_video ADD CONSTRAINT chk_kuaishou_video_create_time CHECK (create_time > 0);

ALTER TABLE weibo_note ADD CONSTRAINT chk_weibo_note_add_ts CHECK (add_ts > 0);
ALTER TABLE weibo_note ADD CONSTRAINT chk_weibo_note_last_modify_ts CHECK (last_modify_ts > 0);
ALTER TABLE weibo_note ADD CONSTRAINT chk_weibo_note_create_time CHECK (create_time > 0);

ALTER TABLE xhs_note ADD CONSTRAINT chk_xhs_note_add_ts CHECK (add_ts > 0);
ALTER TABLE xhs_note ADD CONSTRAINT chk_xhs_note_last_modify_ts CHECK (last_modify_ts > 0);
ALTER TABLE xhs_note ADD CONSTRAINT chk_xhs_note_time CHECK ("time" > 0);

ALTER TABLE tieba_note ADD CONSTRAINT chk_tieba_note_add_ts CHECK (add_ts > 0);
ALTER TABLE tieba_note ADD CONSTRAINT chk_tieba_note_last_modify_ts CHECK (last_modify_ts > 0);

ALTER TABLE zhihu_note ADD CONSTRAINT chk_zhihu_note_add_ts CHECK (add_ts > 0);
ALTER TABLE zhihu_note ADD CONSTRAINT chk_zhihu_note_last_modify_ts CHECK (last_modify_ts > 0);

-- ======================================
-- 脚本执行完成
-- ======================================
SELECT 'Supabase tables creation completed successfully!' as status; 