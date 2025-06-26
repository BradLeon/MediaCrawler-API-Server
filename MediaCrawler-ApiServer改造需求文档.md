# MediaCrawler-ApiServer 改造需求文档

## 项目概述

### 1.1 项目背景
将现有的命令行爬虫程序改造为基于FastAPI的Web服务，提供RESTful API接口，支持多平台媒体数据采集服务。

### 1.2 当前架构分析
- **架构模式**: 命令行单体应用
- **支持平台**: 小红书、抖音、快手、B站、微博、百度贴吧、知乎
- **核心功能**: 
  - 关键词搜索爬取
  - 指定内容详情爬取  
  - 创作者主页数据爬取
  - 评论数据爬取
- **数据存储**: CSV、JSON、MySQL/Supabase
- **登录方式**: 二维码、手机号、Cookie

### 1.3 改造目标
- 构建高性能、可扩展的爬虫服务API
- 支持并发任务处理和任务队列管理
- 提供完整的API文档和监控功能
- 保持原有爬虫功能的完整性

## 2. 系统架构设计

### 2.1 整体架构
采用分层架构模式：
```
表现层(Presentation) -> 业务层(Business) -> 数据访问层(Data Access) -> 基础设施层(Infrastructure)
```

### 2.2 核心组件

#### 2.2.1 API网关层
- **FastAPI应用**: 主应用入口
- **路由管理**: 按功能模块分组的路由
- **中间件**: 认证、限流、日志、CORS等

#### 2.2.2 业务服务层
- **爬虫管理服务**: 统一管理各平台爬虫
- **任务调度服务**: 异步任务队列和调度
- **数据处理服务**: 数据清洗、格式化、存储

#### 2.2.3 爬虫引擎层
- **爬虫工厂**: 动态创建各平台爬虫实例
- **会话管理**: 浏览器上下文和登录状态管理
- **代理管理**: IP代理池和轮换机制

#### 2.2.4 数据存储层
- **关系型数据库**: MySQL/Supabase存储结构化数据
- **缓存系统**: Redis缓存热点数据和会话信息
- **文件存储**: 媒体文件和导出数据存储

## 3. API设计规范

### 3.1 RESTful API设计原则
- 使用HTTP动词表示操作类型
- 资源路径清晰明确
- 统一的响应格式
- 适当的HTTP状态码

### 3.2 API端点设计

#### 3.2.1 任务管理API
```
POST   /api/v1/tasks/search          # 创建搜索任务
POST   /api/v1/tasks/detail          # 创建详情获取任务
POST   /api/v1/tasks/creator         # 创建创作者数据任务
GET    /api/v1/tasks/{task_id}       # 获取任务状态
DELETE /api/v1/tasks/{task_id}       # 取消任务
GET    /api/v1/tasks                 # 获取任务列表
```

#### 3.2.2 平台管理API
```
GET    /api/v1/platforms             # 获取支持的平台列表
GET    /api/v1/platforms/{platform}/status  # 获取平台状态
POST   /api/v1/platforms/{platform}/login   # 平台登录
DELETE /api/v1/platforms/{platform}/logout  # 平台登出
```

#### 3.2.3 数据查询API
```
GET    /api/v1/data/contents         # 获取内容数据
GET    /api/v1/data/comments         # 获取评论数据
GET    /api/v1/data/creators         # 获取创作者数据
GET    /api/v1/data/export/{format}  # 导出数据(csv/json)
```

#### 3.2.4 系统管理API
```
GET    /api/v1/system/health         # 健康检查
GET    /api/v1/system/metrics        # 系统指标
GET    /api/v1/system/config         # 配置信息
POST   /api/v1/system/config         # 更新配置
```

### 3.3 请求/响应格式

#### 3.3.1 统一响应格式
```json
{
  "code": 200,
  "message": "success",
  "data": {},
  "timestamp": "2024-01-01T00:00:00Z",
  "request_id": "uuid"
}
```

#### 3.3.2 错误响应格式
```json
{
  "code": 400,
  "message": "Invalid parameters",
  "error": "详细错误信息",
  "timestamp": "2024-01-01T00:00:00Z",
  "request_id": "uuid"
}
```

## 4. 数据模型设计

### 4.1 任务模型
```python
class TaskModel(BaseModel):
    task_id: str
    platform: str
    task_type: str  # search/detail/creator
    parameters: Dict
    status: str     # pending/running/completed/failed
    progress: int   # 0-100
    result_count: int
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime]
    error_message: Optional[str]
```

### 4.2 内容模型
```python
class ContentModel(BaseModel):
    content_id: str
    platform: str
    title: str
    content: str
    author: str
    publish_time: datetime
    like_count: int
    comment_count: int
    share_count: int
    image_urls: List[str]
    video_url: Optional[str]
    tags: List[str]
    crawled_at: datetime
```

### 4.3 评论模型
```python
class CommentModel(BaseModel):
    comment_id: str
    content_id: str
    parent_comment_id: Optional[str]
    author: str
    content: str
    like_count: int
    publish_time: datetime
    reply_count: int
    level: int  # 评论层级
    crawled_at: datetime
```

## 5. 技术实现方案

### 5.1 技术栈选型
- **Web框架**: FastAPI + Uvicorn
- **异步处理**: asyncio + aiohttp
- **任务队列**: Celery + Redis / RQ
- **数据库**: MySQL/PostgreSQL + SQLAlchemy
- **缓存**: Redis
- **监控**: Prometheus + Grafana
- **日志**: structlog + ELK Stack
- **文档**: FastAPI自动生成Swagger文档

### 5.2 核心模块实现

#### 5.2.1 爬虫管理器
```python
class CrawlerManager:
    async def create_task(self, task_request: TaskRequest) -> TaskResponse
    async def get_task_status(self, task_id: str) -> TaskStatus
    async def cancel_task(self, task_id: str) -> bool
    async def list_tasks(self, filters: Dict) -> List[TaskStatus]
```

#### 5.2.2 平台适配器
```python
class PlatformAdapter:
    async def login(self, login_params: Dict) -> LoginResult
    async def search(self, search_params: Dict) -> SearchResult
    async def get_detail(self, detail_params: Dict) -> DetailResult
    async def get_creator_data(self, creator_params: Dict) -> CreatorResult
```

#### 5.2.3 数据存储适配器
```python
class StorageAdapter:
    async def save_content(self, content: ContentModel) -> bool
    async def save_comment(self, comment: CommentModel) -> bool
    async def query_data(self, query_params: Dict) -> QueryResult
    async def export_data(self, export_params: Dict) -> ExportResult
```

### 5.3 配置管理
使用Pydantic Settings管理配置，支持环境变量和配置文件：

```python
class Settings(BaseSettings):
    # 应用配置
    app_name: str = "MediaCrawler-ApiServer"
    app_version: str = "1.0.0"
    debug: bool = False
    
    # 数据库配置
    database_url: str
    redis_url: str
    
    # 爬虫配置
    max_concurrent_tasks: int = 10
    task_timeout: int = 3600
    
    # 安全配置
    secret_key: str
    api_key_header: str = "X-API-Key"
    
    class Config:
        env_file = ".env"
```

## 6. 部署方案

### 6.1 容器化部署
使用Docker容器化应用，docker-compose管理服务依赖：

```yaml
version: '3.8'
services:
  api-server:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/mediacrawler
      - REDIS_URL=redis://redis:6379
    depends_on:
      - db
      - redis
      
  db:
    image: postgres:14
    environment:
      POSTGRES_DB: mediacrawler
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
      
  redis:
    image: redis:7-alpine
    
  worker:
    build: .
    command: celery worker -A app.celery --loglevel=info
    depends_on:
      - redis
```

### 6.2 生产环境部署
- **反向代理**: Nginx
- **进程管理**: Gunicorn + Uvicorn Workers
- **监控**: Prometheus + Grafana + Alertmanager
- **日志收集**: Filebeat + Elasticsearch + Kibana
- **负载均衡**: 多实例部署 + 负载均衡器

## 7. 安全考虑

### 7.1 认证授权
- API Key认证
- JWT Token认证
- 请求签名验证

### 7.2 访问控制
- IP白名单
- 请求频率限制
- 用户权限管理

### 7.3 数据安全
- 敏感数据加密存储
- 数据传输HTTPS加密
- 数据备份和恢复策略

## 8. 监控与运维

### 8.1 监控指标
- **系统指标**: CPU、内存、磁盘、网络
- **应用指标**: 请求量、响应时间、错误率
- **业务指标**: 任务成功率、数据采集量、平台可用性

### 8.2 告警机制
- 系统资源告警
- 应用异常告警
- 业务指标异常告警

### 8.3 日志管理
- 结构化日志记录
- 日志等级管理
- 日志检索和分析

## 9. 开发计划

### 9.1 阶段一：基础架构搭建（2周）
- FastAPI应用框架搭建
- 数据库模型设计和实现
- 基础API端点实现
- 配置管理和环境搭建

### 9.2 阶段二：爬虫引擎迁移（3周）
- 爬虫引擎重构为服务化
- 任务队列和调度系统实现
- 平台适配器实现
- 会话管理和登录功能

### 9.3 阶段三：核心功能实现（3周）
- 搜索任务API实现
- 详情获取API实现
- 创作者数据API实现
- 数据查询和导出API实现

### 9.4 阶段四：系统完善（2周）
- 监控和日志系统集成
- 安全机制实现
- 性能优化和测试
- 文档完善

### 9.5 阶段五：部署上线（1周）
- 容器化打包
- 生产环境部署
- 监控告警配置
- 用户培训和文档交付

## 10. 风险评估

### 10.1 技术风险
- 爬虫反爬虫机制适应
- 高并发性能瓶颈
- 第三方平台API变更

### 10.2 业务风险
- 法律合规风险
- 数据质量风险
- 服务可用性风险

### 10.3 风险缓解措施
- 完善的错误处理机制
- 灰度发布和回滚机制
- 详细的测试和监控体系

## 11. 预期收益

### 11.1 技术收益
- 提升系统可维护性和扩展性
- 支持更大规模的并发处理
- 提供标准化的API接口

### 11.2 业务收益
- 降低使用门槛，提升用户体验
- 支持多用户并发使用
- 便于集成到其他系统

### 11.3 运维收益
- 统一的监控和管理界面
- 自动化的运维操作
- 更好的问题定位和解决能力

---

*本文档将随着项目进展持续更新和完善* 