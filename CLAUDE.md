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
- **Run data access tests**: `python tests/test_data_access.py`
- **Test API endpoint**: `curl "http://localhost:8000/api/v1/data/content/xhs/66e13f20000000000c01bab3"`

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

Supported platforms (via `PLATFORM_MAPPING` in app/main.py:143):
- `xhs` - 小红书 (XHS)
- `douyin` - 抖音 (Douyin) 
- `bilibili` - B站 (Bilibili)
- `kuaishou` - 快手 (Kuaishou)
- `weibo` - 微博 (Weibo)
- `tieba` - 百度贴吧 (Tieba)
- `zhihu` - 知乎 (Zhihu)

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

- `/api/v1/tasks` - Main crawler task management
- `/api/v1/data/` - Data query and retrieval
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