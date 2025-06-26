# MediaCrawler 命令行参数完善总结

## 📋 概述

完善了MediaCrawler API Server的命令行参数传递功能，现在完全支持所有三种爬取模式：
- **Search模式** - 关键词搜索
- **Detail模式** - 指定内容详情爬取 
- **Creator模式** - 创作者内容爬取

## ✅ 支持的参数类型

### 1. 基础参数
所有模式都支持的基础配置：

```bash
--platform {xhs,dy,ks,bili,wb,zhihu,tieba}  # 平台选择
--type {search,detail,creator}               # 爬取类型
--max_count N                                # 最大爬取数量
--max_comments N                             # 最大评论数量
--headless {true,false}                      # 无头模式
--enable_proxy {true,false}                  # 代理开关
--save_data_option {db,json,csv}             # 数据保存方式
```

### 2. Search模式参数
```bash
--keywords "关键词1,关键词2"                  # 搜索关键词(逗号分隔)
```

### 3. Detail模式参数
每个平台都有对应的内容ID/URL参数(分号分隔)：

```bash
# 小红书
--xhs_note_urls "url1;url2;url3"

# 抖音
--dy_ids "id1;id2;id3"

# 快手
--ks_ids "id1;id2;id3"

# B站
--bili_ids "BV1xx;BV2xx;BV3xx"

# 微博
--weibo_ids "id1;id2;id3"

# 知乎
--zhihu_urls "url1;url2;url3"
```

### 4. Creator模式参数
每个平台都有对应的创作者ID/URL参数(分号分隔)：

```bash
# 小红书
--xhs_creator_ids "creator1;creator2"

# 抖音
--dy_creator_ids "creator1;creator2"

# 快手
--ks_creator_ids "creator1;creator2"

# B站
--bili_creator_ids "creator1;creator2"

# 微博
--weibo_creator_ids "creator1;creator2"

# 知乎 (使用URL格式)
--zhihu_creator_urls "url1;url2"

# 贴吧 (使用URL格式)
--tieba_creator_urls "url1;url2"
```

## 🔧 实现细节

### 1. MediaCrawler命令行扩展
修改了 `MediaCrawler/cmd_arg/arg.py`，添加了：
- 7个平台的创作者参数支持
- 配置文件覆盖逻辑
- 自动分割分号分隔的参数列表

### 2. API Server适配器改进
修改了 `app/crawler/adapter.py`，完善了：
- Creator模式的完整参数传递
- 所有平台的创作者ID/URL支持
- 详细的日志记录

### 3. 参数分隔符约定
- **关键词**：使用逗号(`,`)分隔
- **ID/URL列表**：使用分号(`;`)分隔
- **配置项**：自动映射到MediaCrawler配置

## 🚀 使用示例

### API请求示例

#### 搜索模式
```json
{
    "platform": "xhs",
    "task_type": "search",
    "keywords": ["护肤", "美妆"],
    "max_count": 50,
    "headless": true
}
```

#### 详情模式
```json
{
    "platform": "xhs", 
    "task_type": "detail",
    "content_ids": [
        "https://www.xiaohongshu.com/explore/67e6c0c30000000009016264",
        "68429435000000002102f671"
    ],
    "max_comments": 10
}
```

#### 创作者模式
```json
{
    "platform": "xhs",
    "task_type": "creator", 
    "creator_ids": ["55d34272f5a26377d1b784dd"],
    "max_count": 20
}
```

### 生成的命令行示例

#### 搜索模式命令
```bash
python main.py --platform xhs --type search --keywords "护肤,美妆" --max_count 50 --headless true
```

#### 详情模式命令
```bash
python main.py --platform xhs --type detail --xhs_note_urls "https://www.xiaohongshu.com/explore/note1;https://www.xiaohongshu.com/explore/note2" --max_comments 10
```

#### 创作者模式命令
```bash
python main.py --platform xhs --type creator --xhs_creator_ids "creator1;creator2" --max_count 20
```

## ✨ 优势

1. **完整性** - 支持所有爬取模式和平台
2. **一致性** - 统一的参数命名和分隔符约定
3. **灵活性** - 支持多个ID/URL同时处理
4. **调试友好** - 命令行可见，便于问题排查
5. **并发安全** - 每个任务独立参数，避免配置冲突

## 🧪 测试

运行 `test_all_modes.py` 可以测试所有模式：

```bash
python test_all_modes.py
```

支持测试：
1. 搜索模式
2. 详情模式  
3. 创作者模式
4. 全部模式对比测试 