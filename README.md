# MediaCrawler API Server

<div align="center">

![MediaCrawler API Server](frame.png)

**基于 FastAPI 的多平台社交媒体数据采集 API 服务**

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

</div>

## 📖 项目简介

MediaCrawler API Server 是一个基于 FastAPI 框架构建的高性能社交媒体数据采集服务，通过适配器模式复用原有的 MediaCrawler 爬虫功能，为开发者提供统一的 RESTful API 接口来采集和管理多平台社交媒体数据。

### 🎯 核心特性

- ✅ **小红书完全支持**: 目前完全支持小红书平台的所有功能
  - 🔍 搜索结果采集 (search)
  - 📄 笔记内容采集 (content)
  - 👤 创作者信息采集 (creator)
  - 📊 搜索排序和详情API
- 🔧 **统一接口**: 提供标准化的 RESTful API，简化数据采集流程
- 🛡️ **类型安全**: 基于 Pydantic 模型的完整类型检查和配置验证
- 🗄️ **Supabase存储**: 生产环境推荐使用 Supabase PostgreSQL 数据库
- 🔄 **异步处理**: 基于 FastAPI 的高性能异步处理架构
- 🎛️ **灵活配置**: 支持多层级配置管理，满足不同场景需求
- 📈 **实时监控**: 提供任务状态监控、进度跟踪和日志管理
- 🛠️ **命令行工具**: 提供原生 MediaCrawler 命令行工具支持

## ⚠️ 重要说明

### 平台支持状态
- **完全支持**: 仅 **小红书 (XHS)** 平台
- **其他平台**: 抖音、快手、B站、微博、百度贴吧、知乎等平台提供基础功能，但可能存在兼容性问题

### 数据源类型
- **生产推荐**: `database` (Supabase PostgreSQL)
- **开发测试**: `json` 和 `csv` 格式仍可用，但不推荐生产环境使用

### 支持的采集类型
- **搜索结果采集**: `search` - 基于关键词搜索内容
- **笔记内容采集**: `content` - 采集特定笔记详情
- **创作者信息采集**: `creator` - 采集创作者资料和作品

## 🏗️ 设计思想

### 核心架构原则

#### 1. **适配器模式 (Adapter Pattern)**
```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────────┐
│   FastAPI API   │ => │  Crawler Adapter │ => │  MediaCrawler Core  │
└─────────────────┘    └──────────────────┘    └─────────────────────┘
```

通过适配器模式封装原有的 MediaCrawler 功能，提供统一的 API 接口，实现新旧系统的无缝集成。

#### 2. **配置统一收口**
```
┌─────────────────────────────────────────────────────────────┐
│                   ConfigManager (统一配置管理)                │
├─────────────────┬─────────────────┬─────────────────────────┤
│   AppConfig     │  CrawlerConfig  │     StorageConfig       │
│   (应用级配置)    │  (爬虫任务配置)   │     (数据存储配置)       │
└─────────────────┴─────────────────┴─────────────────────────┘
```

所有配置统一通过 ConfigManager 管理，基于 Pydantic 模型提供类型安全的配置交互。

#### 3. **模块化分层架构**
```
┌─────────────────────────────────────────────────────────────┐
│                        API Layer                           │
├─────────────────────────────────────────────────────────────┤
│                      Business Layer                        │
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────┐ │
│  │ Crawler Adapter │  │  Data Reader    │  │ Login Manager│ │
│  └─────────────────┘  └─────────────────┘  └──────────────┘ │
├─────────────────────────────────────────────────────────────┤
│                        Core Layer                          │
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────┐ │
│  │ Config Manager  │  │ Logging Manager │  │Database Utils│ │
│  └─────────────────┘  └─────────────────┘  └──────────────┘ │
├─────────────────────────────────────────────────────────────┤
│                   Integration Layer                        │
│                  MediaCrawler Core                         │
└─────────────────────────────────────────────────────────────┘
```

## 🏗️ 代码框架

### 目录结构
```
MediaCrawler-ApiServer/
├── app/                          # 应用主目录
│   ├── api/                      # API路由层
│   │   ├── data.py              # 数据查询API
│   │   └── login.py             # 登录管理API
│   ├── core/                     # 核心模块
│   │   ├── config_manager.py    # 统一配置管理
│   │   ├── config.py            # 基础配置
│   │   ├── logging.py           # 日志管理
│   │   ├── database.py          # 数据库工具
│   │   └── login_manager.py     # 登录状态管理
│   ├── crawler/                  # 爬虫适配器
│   │   ├── adapter.py           # 主适配器
│   │   └── core/                # 爬虫核心组件
│   ├── dataReader/              # 数据读取器
│   │   ├── base.py              # 基础抽象类
│   │   ├── factory.py           # 工厂模式
│   │   ├── json_reader.py       # JSON数据读取
│   │   ├── csv_reader.py        # CSV数据读取
│   │   └── supabase_reader.py   # Supabase数据读取
│   ├── models/                   # 数据模型
│   │   ├── base.py              # 基础模型
│   │   ├── comment.py           # 评论模型
│   │   ├── content.py           # 内容模型
│   │   └── task.py              # 任务模型
│   └── main.py                   # FastAPI应用入口
├── MediaCrawler/                 # 原MediaCrawler项目
├── data/                         # 数据存储目录
├── logs/                         # 日志文件
├── tests/                        # 测试文件
├── examples/                     # 示例代码
└── config.env.example           # 配置文件模板
```

### 核心模块说明

#### 1. **配置管理模块** (`app/core/config_manager.py`)
```python
# 应用级配置
class AppConfig(BaseModel):
    app_name: str = "MediaCrawler API Server"
    version: str = "1.0.0"
    supported_platforms: List[str]

# 爬虫配置请求（API层）
class CrawlerConfigRequest(BaseModel):
    enable_proxy: Optional[bool] = None
    headless: Optional[bool] = None
    max_retries: Optional[int] = None

# 完整爬虫配置（内部使用）
class CrawlerConfig(BaseModel):
    platform: str
    enable_proxy: bool = False
    headless: bool = True
    max_retries: int = 3

# 存储配置
class StorageConfig(BaseModel):
    source_type: str
    connection_timeout: int = 30
    retry_times: int = 3
```

#### 2. **爬虫适配器** (`app/crawler/adapter.py`)
```python
class MediaCrawlerAdapter:
    async def start_crawler_task(self, task: CrawlerTask)
    async def get_task_status(self, task_id: str)
    async def get_task_result(self, task_id: str)
    async def stop_task(self, task_id: str)
```

#### 3. **数据读取器** (`app/dataReader/`)
```python
class BaseDataReader(ABC):
    @abstractmethod
    async def get_content_list(self, platform, filters)
    @abstractmethod
    async def get_content_by_id(self, platform, content_id)
    @abstractmethod
    async def search_content(self, platform, keyword, filters)
```

## 🔄 模块流程

### 1. 爬虫任务执行流程
```
Client Request → FastAPI → ConfigManager → CrawlerAdapter → MediaCrawler
                                ↓
Response ← JSON Result ← Task Result ← Crawler Execution ← Core Engine
```

### 2. 配置管理流程
```
API Request → CrawlerConfigRequest → ConfigManager.build_crawler_config()
                                           ↓
默认配置 + 平台配置 + 环境变量 + API配置 → CrawlerConfig → 类型验证 → 最终配置
```

### 3. 数据查询流程
```
Data API Request → DataReaderFactory → DataReader → DataSource
                                          ↓
JSON Response ← Formatted Result ← Query Result ← Raw Data
```

## 📡 完整 API 接口规范

### 1. 爬虫任务管理 API

#### 1.1 创建爬虫任务

**小红书搜索模式:**
```bash
curl -X POST "http://localhost:8000/api/v1/tasks" \
-H "Content-Type: application/json" \
-d '{
  "platform": "xhs",
  "task_type": "search",
  "keywords": ["车漆刮蹭修复", "汽车保养"],
  "max_count": 50,
  "max_comments": 20,
  "headless": true,
  "enable_proxy": false,
  "save_data_option": "db"
}'
```

**小红书笔记详情模式:**
```bash
curl -X POST "http://localhost:8000/api/v1/tasks" \
-H "Content-Type: application/json" \
-d '{
  "platform": "xhs",
  "task_type": "detail",
  "content_ids": ["6877460d00000000110016de"],
  "xhs_note_urls": ["https://www.xiaohongshu.com/explore/6877460d00000000110016de?xsec_token=ABcd123&xsec_source=pc_user"],
  "max_count": 1,
  "max_comments": 20,
  "headless": false
}'
```

**小红书创作者模式:**
```bash
curl -X POST "http://localhost:8000/api/v1/tasks" \
-H "Content-Type: application/json" \
-d '{
  "platform": "xhs",
  "task_type": "creator", 
  "creator_ids": ["user123456"],
  "max_count": 30,
  "max_comments": 10,
  "headless": true
}'
```

**响应示例:**
```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "message": "任务已创建并开始执行"
}
```

#### 1.2 查询任务状态
```bash
curl "http://localhost:8000/api/v1/tasks/{task_id}/status"
```

**响应示例:**
```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "running",
  "done": false,
  "success": null,
  "message": "正在执行数据采集...",
  "data_count": 45,
  "error_count": 2,
  "progress": {
    "current_stage": "数据采集中",
    "progress_percent": 45.6,
    "items_completed": 45,
    "items_total": 100,
    "items_failed": 2,
    "estimated_remaining_time": 120
  }
}
```

#### 1.3 获取任务结果
```bash
curl "http://localhost:8000/api/v1/tasks/{task_id}/result"
```

**响应示例:**
```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "success": true,
  "message": "任务执行成功",
  "data_count": 98,
  "error_count": 2,
  "data": [
    {
      "note_id": "67e6c0c30000000009016264",
      "title": "车漆刮蹭修复技巧分享",
      "desc": "今天分享一些实用的车漆修复方法...",
      "nickname": "汽车保养专家",
      "liked_count": 1234,
      "comments_count": 56,
      "publish_time": "2024-01-01 12:00:00",
      "note_url": "https://www.xiaohongshu.com/explore/67e6c0c30000000009016264"
    }
  ]
}
```

#### 1.4 停止任务
```bash
curl -X DELETE "http://localhost:8000/api/v1/tasks/{task_id}"
```

#### 1.5 列出运行中的任务
```bash
curl "http://localhost:8000/api/v1/tasks"
```

### 2. 数据查询 API

#### 2.1 获取内容列表
```bash
# 获取小红书内容列表（默认使用database数据源）
curl "http://localhost:8000/api/v1/data/content/xhs?limit=20&offset=0"

# 按任务ID过滤
curl "http://localhost:8000/api/v1/data/content/xhs?task_id=550e8400-e29b-41d4-a716-446655440000&limit=10"

# 关键词搜索
curl "http://localhost:8000/api/v1/data/content/xhs?keyword=车漆修复&limit=15"
```

#### 2.2 获取内容详情
```bash
# 获取特定笔记详情
curl "http://localhost:8000/api/v1/data/content/xhs/67e6c0c30000000009016264"

# 指定数据源
curl "http://localhost:8000/api/v1/data/content/xhs/67e6c0c30000000009016264?source_type=database"
```

#### 2.3 搜索相关 API

**通用搜索接口:**
```bash
curl "http://localhost:8000/api/v1/data/search/xhs?keyword=车漆刮蹭修复&limit=20"
```

**搜索排序结果（来自search_result表）:**
```bash
curl "http://localhost:8000/api/v1/data/search/xhs/ranking?keyword=车漆刮蹭修复&limit=20"
```

**搜索详细内容（来自note表）:**
```bash
curl "http://localhost:8000/api/v1/data/search/xhs/details?keyword=车漆刮蹭修复&limit=20"
```

**组合搜索结果（排序+详情）:**
```bash
curl "http://localhost:8000/api/v1/data/search/xhs/combined?keyword=车漆刮蹭修复&limit=10"
```

**指定笔记ID查询详情:**
```bash
curl "http://localhost:8000/api/v1/data/search/xhs/details?keyword=车漆刮蹭修复&note_ids=note1,note2,note3"
```

#### 2.4 创作者相关 API
```bash
# 获取创作者资料
curl "http://localhost:8000/api/v1/data/creator/xhs/user123456/profile"

# 获取创作者内容
curl "http://localhost:8000/api/v1/data/creator/xhs/user123456/content?limit=20"
```

### 3. 登录管理 API

#### 3.1 创建登录会话
```bash
curl -X POST "http://localhost:8000/api/v1/login/create-session" \
-H "Content-Type: application/json" \
-d '{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "platform": "xhs",
  "login_type": "qrcode",
  "timeout": 300
}'
```

#### 3.2 获取登录状态
```bash
curl "http://localhost:8000/api/v1/login/status/550e8400-e29b-41d4-a716-446655440000"
```

#### 3.3 提交登录输入
```bash
curl -X POST "http://localhost:8000/api/v1/login/input/550e8400-e29b-41d4-a716-446655440000" \
-H "Content-Type: application/json" \
-d '{
  "input_type": "phone",
  "value": "13800138000"
}'
```

### 4. 系统管理 API

#### 4.1 健康检查
```bash
curl "http://localhost:8000/api/v1/data/health"
```

#### 4.2 获取支持的平台
```bash
curl "http://localhost:8000/api/v1/data/platforms"
```

#### 4.3 获取数据源类型
```bash
curl "http://localhost:8000/api/v1/data/sources"
```

#### 4.4 获取配置选项
```bash
curl "http://localhost:8000/api/v1/system/config/options"
```

#### 4.5 系统统计
```bash
curl "http://localhost:8000/api/v1/system/stats"
```

### 5. Cookie管理 API

#### 5.1 获取Cookie状态
```bash
curl "http://localhost:8000/api/v1/cookies/xhs/status"
```

#### 5.2 列出所有Cookies
```bash
curl "http://localhost:8000/api/v1/cookies"
```

#### 5.3 清除平台Cookies
```bash
curl -X DELETE "http://localhost:8000/api/v1/cookies/xhs"
```

## 🛠️ MediaCrawler 命令行工具

除了API接口，本项目还提供原生的MediaCrawler命令行工具，位于 `MediaCrawler/main.py`：

### 基本语法
```bash
cd MediaCrawler
python main.py --platform {平台} --lt {登录方式} [其他参数]
```

### 命令行参数说明
- `--platform`: 平台类型 (xhs, dy, ks, bili, wb, tieba, zhihu)
- `--lt`: 登录类型 (qrcode, phone, cookie)
- `--keywords`: 搜索关键词 (搜索模式必需)
- `--note_ids`: 笔记ID列表 (详情模式必需)
- `--creator_ids`: 创作者ID列表 (创作者模式必需)
- `--max_count`: 最大采集数量
- `--headless`: 无头浏览器模式
- `--enable_proxy`: 启用代理
- `--save_data_option`: 存储方式 (db, json, csv)

### 使用示例

#### 小红书搜索采集
```bash
# 基础搜索
cd MediaCrawler
python main.py --platform xhs --lt qrcode --keywords "车漆刮蹭修复" --max_count 50

# 多关键词搜索
python main.py --platform xhs --lt qrcode --keywords "车漆刮蹭修复,汽车保养,车辆维护" --max_count 100

# 使用代理和无头模式
python main.py --platform xhs --lt qrcode --keywords "美食推荐" --max_count 30 --headless --enable_proxy
```

#### 小红书笔记详情采集
```bash
# 单个笔记
python main.py --platform xhs --lt qrcode --note_ids "67e6c0c30000000009016264"

# 多个笔记
python main.py --platform xhs --lt qrcode --note_ids "note1,note2,note3" --max_comments 50
```

#### 小红书创作者采集
```bash
# 采集创作者内容
python main.py --platform xhs --lt qrcode --creator_ids "user123456" --max_count 20

# 采集多个创作者
python main.py --platform xhs --lt qrcode --creator_ids "user1,user2,user3" --max_count 50
```

#### 数据存储配置
```bash
# 保存到数据库 (需要配置环境变量)
export SEO_SUPABASE_URL="https://your-project.supabase.co"
export SEO_SUPABASE_ANON_KEY="your-anon-key"
python main.py --platform xhs --lt qrcode --keywords "美食" --save_data_option db

# 保存到JSON文件
python main.py --platform xhs --lt qrcode --keywords "旅行" --save_data_option json

# 保存到CSV文件
python main.py --platform xhs --lt qrcode --keywords "摄影" --save_data_option csv
```

#### 高级配置示例
```bash
# 完整配置示例
python main.py \
  --platform xhs \
  --lt qrcode \
  --keywords "编程学习,Python教程" \
  --max_count 200 \
  --max_comments 30 \
  --headless \
  --enable_proxy \
  --save_data_option db \
  --timeout 60 \
  --max_retries 5
```

### 注意事项
1. **环境要求**: 确保已安装所有依赖和浏览器驱动
2. **登录状态**: 首次使用需要扫码或输入验证码登录
3. **数据存储**: 使用 `--save_data_option db` 时需配置Supabase环境变量
4. **代理设置**: 启用代理需要配置代理服务商API
5. **平台限制**: 目前完全支持小红书，其他平台功能有限

## 📚 使用手册

### 1. 环境搭建

#### 系统要求
- Python 3.8+
- 内存: 4GB+
- 存储: 10GB+

#### 安装步骤

1. **克隆项目**
```bash
git clone https://github.com/your-repo/MediaCrawler-ApiServer.git
cd MediaCrawler-ApiServer
```

2. **创建虚拟环境**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate     # Windows
```

3. **安装依赖**
```bash
pip install -r requirements.txt
```

4. **配置环境变量**
```bash
cp config.env.example .env
# 编辑 .env 文件，配置必要的环境变量
```

5. **启动服务**
```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 2. 配置说明

#### 环境变量配置 (`.env`)
```bash
# Supabase配置（生产环境必需）
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_supabase_anon_key

# MediaCrawler命令行工具专用（与API服务器使用相同配置）
SEO_SUPABASE_URL=https://your-project.supabase.co
SEO_SUPABASE_ANON_KEY=your_supabase_anon_key

# 代理配置
DEFAULT_ENABLE_PROXY=false
DEFAULT_PROXY_PROVIDER=kuaidaili

# 爬虫配置
DEFAULT_HEADLESS=true
DEFAULT_MAX_RETRIES=3
DEFAULT_TIMEOUT=30

# 日志配置
LOG_LEVEL=INFO
LOG_FILE=logs/app.log
```

**Supabase配置获取步骤：**
1. 访问 [Supabase Dashboard](https://supabase.com/dashboard)
2. 选择您的项目
3. 进入 Settings > API
4. 复制 Project URL 和 anon/public key
5. 配置到 `.env` 文件中

#### 平台配置
每个平台都有默认的配置参数，可以通过 API 请求进行覆盖：

```python
# 小红书平台默认配置
{
    "delay_range": [2, 4],
    "max_comments": 100,
    "timeout": 45
}

# 抖音平台默认配置  
{
    "delay_range": [1, 2],
    "max_comments": 50,
    "timeout": 30
}
```

### 3. 快速开始

**注意**: 以下示例均基于小红书平台，这是目前唯一完全支持的平台。

#### 示例1: 小红书关键词搜索
```python
import requests

# 创建搜索任务（使用数据库存储）
task_data = {
    "platform": "xhs",
    "task_type": "search", 
    "keywords": ["车漆刮蹭修复"],
    "max_count": 50,
    "max_comments": 20,
    "headless": True,
    "save_data_option": "db"  # 推荐使用数据库存储
}

response = requests.post("http://localhost:8000/api/v1/tasks", json=task_data)
task_id = response.json()["task_id"]

# 监控任务状态
import time
while True:
    status = requests.get(f"http://localhost:8000/api/v1/tasks/{task_id}/status")
    if status.json()["done"]:
        break
    time.sleep(3)

# 获取结果
result = requests.get(f"http://localhost:8000/api/v1/tasks/{task_id}/result")
print(result.json())
```

#### 示例2: 查询已有数据（使用新的搜索API）
```python
import requests

# 查询搜索排序结果
response = requests.get(
    "http://localhost:8000/api/v1/data/search/xhs/ranking",
    params={"keyword": "车漆刮蹭修复", "limit": 20}
)
ranking_data = response.json()

# 查询搜索详细内容
response = requests.get(
    "http://localhost:8000/api/v1/data/search/xhs/details", 
    params={"keyword": "车漆刮蹭修复", "limit": 20}
)
details_data = response.json()

# 组合查询
response = requests.get(
    "http://localhost:8000/api/v1/data/search/xhs/combined",
    params={"keyword": "车漆刮蹭修复", "limit": 10}
)
combined_data = response.json()

print(f"排序结果: {len(ranking_data['data'])} 条")
print(f"详细内容: {len(details_data['data'])} 条")
```

#### 示例3: 小红书笔记详情采集
```python
import requests

# 采集特定笔记详情
task_data = {
    "platform": "xhs",
    "task_type": "detail",
    "content_ids": ["67e6c0c30000000009016264"],
    "xhs_note_urls": ["https://www.xiaohongshu.com/explore/67e6c0c30000000009016264?xsec_token=ABC&xsec_source=pc_user"],
    "max_count": 1,
    "max_comments": 50,
    "save_data_option": "db",
    "config": {
        "headless": False,
        "max_retries": 3,
        "timeout": 45
    }
}

response = requests.post("http://localhost:8000/api/v1/tasks", json=task_data)
```

#### 示例4: 小红书创作者内容采集
```python
import requests

# 采集创作者发布的内容
task_data = {
    "platform": "xhs", 
    "task_type": "creator",
    "creator_ids": ["user123456"],
    "max_count": 30,
    "max_comments": 20,
    "save_data_option": "db",
    "headless": True
}

response = requests.post("http://localhost:8000/api/v1/tasks", json=task_data)
```

### 4. 部署指南

#### Docker 部署
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```bash
# 构建镜像
docker build -t mediacrawler-api .

# 运行容器
docker run -d -p 8000:8000 \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/logs:/app/logs \
  --env-file .env \
  mediacrawler-api
```

#### Nginx 配置
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

### 5. 性能优化

#### 并发控制
```python
# 在配置中设置合理的并发参数
config = {
    "max_retries": 3,           # 重试次数
    "timeout": 30,              # 超时时间
    "delay_range": [2, 4],      # 请求间隔
    "enable_proxy": True,       # 使用代理池
    "batch_size": 100           # 批处理大小
}
```

#### 内存管理
- 合理设置 `max_count` 参数，避免一次性采集过多数据
- 定期清理完成的任务结果
- 使用流式处理大型数据集

#### 存储优化
- **Database (Supabase) - 强烈推荐**: 
  - 生产环境首选，支持高性能查询和实时数据同步
  - 支持复杂的搜索和数据关联操作
  - 多用户并发访问，数据一致性保障
  - 自动备份和恢复功能
- **JSON**: 开发测试环境，适合小规模数据验证
- **CSV**: 数据分析专用，不推荐作为主要存储方式

**重要**: 生产环境必须使用 `source_type=database`，其他存储方式仅供开发测试使用。

## 🔧 其他

### 故障排除

#### 常见问题

1. **端口占用**
```bash
# 检查端口占用
lsof -i :8000
# 杀死进程
kill -9 <pid>
```

2. **依赖冲突**
```bash
# 重新创建虚拟环境
rm -rf venv
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

3. **权限问题**
```bash
# 确保数据目录有写权限
chmod 755 data logs
```

4. **浏览器驱动问题**
```bash
# 安装Chrome驱动
apt-get update
apt-get install -y chromium-browser chromium-chromedriver
```

### 监控和日志

#### 日志级别
- `DEBUG`: 详细调试信息
- `INFO`: 一般信息 (默认)
- `WARNING`: 警告信息
- `ERROR`: 错误信息

#### 日志文件
```
logs/
├── app.log          # 应用主日志
├── errors.log       # 错误日志  
├── access.log       # 访问日志
└── crawler.log      # 爬虫执行日志
```

#### 监控指标
- 任务成功率
- 平均响应时间
- 数据采集量
- 错误率统计

### 扩展开发

#### 添加新平台支持
1. 在 `MediaCrawler` 中实现平台爬虫
2. 在 `PlatformType` 枚举中添加新平台
3. 在 `ConfigManager` 中配置平台参数
4. 编写对应的测试用例

#### 自定义数据读取器
```python
class CustomDataReader(BaseDataReader):
    async def get_content_list(self, platform, filters):
        # 实现自定义读取逻辑
        pass
```

#### 添加新的存储方式
```python
class CustomStorageConfig(BaseModel):
    # 定义存储配置
    pass

# 在 ConfigManager 中注册
def build_storage_config(self, source_type: str, platform: str = None):
    if source_type == "custom":
        return CustomStorageConfig(...)
```

### 社区贡献

欢迎提交 Issue 和 Pull Request！

1. Fork 项目
2. 创建特性分支: `git checkout -b feature/new-feature`
3. 提交更改: `git commit -am 'Add new feature'`
4. 推送分支: `git push origin feature/new-feature`
5. 提交 Pull Request

### 许可证

本项目基于 MIT 许可证开源，详见 [LICENSE](LICENSE) 文件。

### 联系方式

- 项目主页: https://github.com/your-repo/MediaCrawler-ApiServer
- 问题反馈: https://github.com/your-repo/MediaCrawler-ApiServer/issues
- 讨论社区: https://github.com/your-repo/MediaCrawler-ApiServer/discussions

---

<div align="center">

**如果这个项目对您有帮助，请给个 ⭐ Star 支持一下！**

</div> 