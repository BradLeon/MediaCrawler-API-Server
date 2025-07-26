# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Server Management
- **Start development server**: `python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload`
- **Start production server**: `python start_server.py`
- **Alternative server start**: `python run_server.py`

### Testing
- **Run comprehensive tests**: `python tests/test_comprehensive.py`
- **Run specific crawler tests**: `python test_xhs_content_crawler.py`
- **Run search crawler tests**: `python test_xhs_search_crawler.py`
- **Run data access tests**: `python tests/test_data_access.py`
- **Test search APIs**: `python test_search_apis.py`
- **Test API endpoint**: `curl "http://localhost:8000/api/v1/data/content/xhs/66e13f20000000000c01bab3"`
- **Test search ranking API**: `curl "http://localhost:8000/api/v1/data/search/xhs/ranking?keyword=车漆刮蹭修复&limit=5"`
- **Test search details API**: `curl "http://localhost:8000/api/v1/data/search/xhs/details?keyword=车漆刮蹭修复&limit=5"`
- **Test combined search API**: `curl "http://localhost:8000/api/v1/data/search/xhs/combined?keyword=车漆刮蹭修复&limit=5"`

### Python Environment
- **Install dependencies**: `pip install -r requirements.txt`
- **Activate virtual environment**: `source venv/bin/activate` (Linux/Mac) or `venv\Scripts\activate` (Windows)

## Architecture Overview

This is a FastAPI-based social media crawler API server that wraps the existing MediaCrawler project through an adapter pattern. The system provides unified RESTful APIs for crawling multiple social media platforms.

### Core Design Patterns

**Adapter Pattern**: The `app/crawler/adapter.py` wraps the original MediaCrawler functionality, providing a unified interface for the FastAPI layer.

**Configuration Management**: All configuration is centralized through `app/core/config_manager.py` using Pydantic models with multi-layer configuration merging (defaults + platform-specific + environment variables + API parameters).

**Factory Pattern**: Data readers (`app/dataReader/factory.py`) use factory pattern to create appropriate data access objects based on storage type (Supabase, MySQL, JSON, CSV).

### Key Components

**FastAPI Application** (`app/main.py`): Main application entry point with all API endpoints and middleware configuration.

**Crawler Adapter** (`app/crawler/adapter.py`): Core adapter that translates API requests to MediaCrawler operations. Handles task management, status tracking, and result processing.

**Configuration System** (`app/core/config_manager.py`): Manages multi-layered configuration with type validation using Pydantic models.

**Data Access Layer** (`app/dataReader/`): Abstracted data access with multiple backend support (Supabase, MySQL, JSON, CSV) and automatic fallback mechanisms.

**Login Management** (`app/core/login_manager.py`): Handles authentication sessions for different platforms with QR code and manual login support.

### Data Flow

1. **API Request** → FastAPI endpoint receives crawler task request
2. **Configuration Building** → ConfigManager merges default, platform, environment, and request-specific configs
3. **Task Creation** → CrawlerAdapter creates MediaCrawler task with validated configuration
4. **Crawler Execution** → Original MediaCrawler core executes the scraping task
5. **Result Processing** → Adapter processes results and stores in configured data source
6. **Response** → API returns task status, progress, or results to client

### Platform Support

**Currently Fully Supported Platform:**
- `xhs` - 小红书 (XHS) - **完全支持**
  - ✅ 搜索结果采集 (search)
  - ✅ 笔记内容采集 (content) 
  - ✅ 创作者信息采集 (creator)
  - ✅ 搜索排序API (search ranking)
  - ✅ 搜索详情API (search details)

**Other Platforms (Limited Support):**
- `douyin` - 抖音 (Douyin) - 基础功能
- `bilibili` - B站 (Bilibili) - 基础功能
- `kuaishou` - 快手 (Kuaishou) - 基础功能
- `weibo` - 微博 (Weibo) - 基础功能
- `tieba` - 百度贴吧 (Tieba) - 基础功能
- `zhihu` - 知乎 (Zhihu) - 基础功能

**Data Source Types:**
- `database` - Supabase PostgreSQL (推荐，生产环境)
- `json` - JSON文件存储 (开发测试)
- `csv` - CSV文件存储 (数据分析)

### Configuration Files

**Environment Configuration**: Copy `config.env.example` to `.env` and configure database URLs, proxy settings, and platform-specific parameters.

**MediaCrawler Integration**: The original MediaCrawler project is included as a submodule in the `MediaCrawler/` directory and provides the core crawling functionality.

### Data Storage

The system supports multiple data storage backends:
- **Supabase** (default and recommended for production) - PostgreSQL database with real-time capabilities
- **MySQL** (compatible with original MediaCrawler)
- **JSON files** (for development and small datasets)
- **CSV files** (for data analysis and exports)

**Important**: The default `source_type` for data queries is now `database` (Supabase), not `json`. This change was made to prioritize database storage for better performance and reliability.

### API Endpoints Structure

**Task Management:**
- `/api/v1/tasks` - Main crawler task management
- `/api/v1/tasks/{task_id}/status` - Task status monitoring
- `/api/v1/tasks/{task_id}/result` - Task result retrieval

**Data Query:**
- `/api/v1/data/content/{platform}` - Content list query
- `/api/v1/data/content/{platform}/{content_id}` - Content detail query
- `/api/v1/data/search/{platform}` - General content search
- `/api/v1/data/search/{platform}/ranking` - Search ranking results (from search_result table)
- `/api/v1/data/search/{platform}/details` - Search detail content (from note table)
- `/api/v1/data/search/{platform}/combined` - Combined search results (ranking + details)
- `/api/v1/data/creator/{platform}/{user_id}` - Creator profile and content

**Platform Management:**
- `/api/v1/login/` - Platform login management
- `/api/v1/cookies/` - Cookie management for maintaining sessions
- `/api/v1/system/` - System statistics and configuration

### Task Management

Tasks are managed asynchronously with status tracking:
- **Task Creation**: Returns task_id for tracking
- **Status Monitoring**: Real-time progress updates via `/tasks/{task_id}/status`
- **Result Retrieval**: Structured data via `/tasks/{task_id}/result`
- **Task Control**: Stop/cancel via DELETE `/tasks/{task_id}`

### Database Configuration

**Supabase Setup**: 
- The system uses environment variables from `.env` file for Supabase configuration
- `SUPABASE_URL` and `SUPABASE_KEY` are read directly from `.env` file, not from Settings
- Database client initialization is handled in `app/core/database.py:create_supabase_client()`
- Connection is established automatically on first API call

**Data Query API**:
- Default endpoint: `GET /api/v1/data/content/{platform}/{content_id}` (uses database by default)
- With explicit source: `GET /api/v1/data/content/{platform}/{content_id}?source_type=database`
- The API automatically falls back to configured storage if Supabase is unavailable

### Development Notes

When modifying the crawler functionality, focus on the adapter layer (`app/crawler/adapter.py`) rather than the core MediaCrawler code. The adapter handles the translation between the API interface and the underlying crawler implementation.

Configuration changes should be made through the ConfigManager system to ensure proper validation and type safety. Platform-specific configurations are defined in the `get_platform_config()` method.

**Database Development**:
- Supabase connection issues are automatically handled with fallback to alternative storage
- Debug logging has been cleaned up to remove emoji and verbose output
- All database operations use proper error handling and connection management

The system includes comprehensive logging and error handling with structured log output to both console and files in the `logs/` directory.

## MediaCrawler Command Line Tools

The original MediaCrawler project (`MediaCrawler/main.py`) provides direct command-line access to crawling functionality:

### Basic Usage
```bash
cd MediaCrawler
python main.py --platform xhs --lt search --keywords "美食推荐" --max_count 50
```

### Command Line Parameters
- `--platform`: Platform type (xhs, dy, ks, bili, wb, tieba, zhihu)
- `--lt`: Login type (qrcode, phone, cookie)
- `--keywords`: Search keywords (for search mode)
- `--max_count`: Maximum items to crawl
- `--headless`: Run browser in headless mode
- `--enable_proxy`: Enable proxy usage
- `--save_data_option`: Data storage option (db, json, csv)

### Search Mode Examples
```bash
# XHS search with keywords
python main.py --platform xhs --lt qrcode --keywords "车漆刮蹭修复,汽车保养" --max_count 100

# Douyin search
python main.py --platform dy --lt qrcode --keywords "舞蹈教学" --max_count 50

# Bilibili search
python main.py --platform bili --lt qrcode --keywords "编程教程" --max_count 30
```

### Detail Mode Examples
```bash
# XHS specific note crawling
python main.py --platform xhs --lt qrcode --note_ids "note_id1,note_id2"

# Douyin video crawling
python main.py --platform dy --lt qrcode --video_ids "video_id1,video_id2"
```

### Creator Mode Examples
```bash
# XHS creator content crawling
python main.py --platform xhs --lt qrcode --creator_ids "creator_id1" --max_count 20

# Douyin creator content
python main.py --platform dy --lt qrcode --creator_ids "creator_id1" --max_count 15
```

### Database Configuration
When using `--save_data_option db`, ensure environment variables are set:
```bash
export SEO_SUPABASE_URL="https://your-project.supabase.co"
export SEO_SUPABASE_ANON_KEY="your-anon-key"
```

### Advanced Configuration
```bash
# Using proxy with custom settings
python main.py --platform xhs --lt qrcode --keywords "美食" \
  --enable_proxy --proxy_provider kuaidaili \
  --headless --max_retries 3 --timeout 45

# Save to different formats
python main.py --platform xhs --lt qrcode --keywords "旅行" \
  --save_data_option json --max_count 20

# Multiple keywords search
python main.py --platform xhs --lt qrcode \
  --keywords "美食推荐,餐厅探店,下午茶" \
  --max_count 200 --headless
```