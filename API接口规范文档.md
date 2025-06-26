# MediaCrawler API Server 接口规范文档

## 📋 文档版本

- **版本**: v2.0
- **更新日期**: 2025-06-25
- **状态**: 稳定版本

## 🎯 核心改进

### v2.0 重大更新
1. **统一配置管理**: 所有配置统一收口到 ConfigManager
2. **基于 Pydantic 模型**: 类型安全的配置交互
3. **模块化重构**: dataAccess → dataReader，职责更清晰
4. **配置验证增强**: 完整的参数验证和错误处理

## 🏗️ 系统架构

### 配置管理架构
```
ConfigManager (统一配置入口)
├── AppConfig (应用级配置)
├── CrawlerConfig (爬虫任务配置)
│   ├── CrawlerConfigRequest (API请求)
│   └── 最终合并配置 (内部使用)
└── StorageConfig (数据存储配置)
```

### 数据流架构
```
API Request → 配置验证 → 任务创建 → 爬虫执行 → 数据存储 → 结果返回
     ↓           ↓          ↓          ↓          ↓          ↓
  Pydantic → ConfigManager → Adapter → MediaCrawler → DataWriter → Response
```

## 📡 API 端点规范

### 1. 爬虫任务管理

#### 1.1 创建爬虫任务
**端点**: `POST /api/v1/tasks`

**请求体**:
```json
{
  "platform": "xhs",                    // 必填: 平台名称
  "task_type": "search",                // 必填: 任务类型
  "keywords": ["美食", "旅行"],          // 搜索关键词(search模式必填)
  "content_ids": ["id1", "id2"],        // 内容ID列表(detail模式必填)
  "creator_ids": ["user1", "user2"],    // 创作者ID(creator模式必填)
  "max_count": 100,                     // 最大采集数量
  "max_comments": 50,                   // 最大评论数量
  "start_page": 1,                      // 起始页码
  "enable_proxy": false,                // 是否启用代理
  "headless": true,                     // 是否无头模式
  "enable_comments": true,              // 是否采集评论
  "enable_sub_comments": false,         // 是否采集子评论
  "save_data_option": "db",             // 数据保存方式: db/json/csv
  "clear_cookies": false,               // 是否清除cookies
  "config": {                           // 高级配置(可选)
    "enable_proxy": false,
    "proxy_provider": "kuaidaili",
    "headless": true,
    "user_agent": "custom-agent",
    "window_size": "1920,1080",
    "max_retries": 3,
    "delay_range": [2, 4],
    "timeout": 30
  }
}
```

**配置字段验证规则**:
- `platform`: 枚举值 [xhs, douyin, bilibili, kuaishou, weibo, tieba, zhihu]
- `task_type`: 枚举值 [search, detail, creator]
- `max_count`: 1-1000
- `max_comments`: 0-500
- `window_size`: 格式 "宽度,高度" (如: "1920,1080")
- `max_retries`: 0-10
- `delay_range`: 长度为2的数组，第一个值≤第二个值
- `timeout`: 10-300秒
- `save_data_option`: 枚举值 [db, json, csv]

**响应**:
```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "message": "任务已创建并开始执行"
}
```

#### 1.2 查询任务状态
**端点**: `GET /api/v1/tasks/{task_id}/status`

**响应**:
```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "running",                   // 任务状态
  "done": false,                        // 是否完成
  "success": null,                      // 是否成功(完成后才有值)
  "message": "正在执行数据采集...",       // 状态消息
  "data_count": 45,                     // 已采集数据数量
  "error_count": 2,                     // 错误数量
  "progress": {                         // 进度详情
    "current_stage": "数据采集中",
    "progress_percent": 45.6,
    "items_total": 100,
    "items_completed": 45,
    "items_failed": 2,
    "current_item": "正在处理: 美食推荐",
    "estimated_remaining_time": 120,    // 预估剩余时间(秒)
    "last_update": "2024-01-01T12:34:56Z"
  }
}
```

**状态值说明**:
- `pending`: 任务已创建，等待执行
- `running`: 任务执行中
- `completed`: 任务已完成
- `failed`: 任务执行失败
- `cancelled`: 任务被取消

#### 1.3 获取任务结果
**端点**: `GET /api/v1/tasks/{task_id}/result`

**响应**:
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
      "title": "美食分享：探店记录",
      "desc": "今天去了一家很棒的餐厅...",
      "author": {
        "user_id": "user123",
        "nickname": "美食达人",
        "avatar": "https://avatar.url"
      },
      "publish_time": "2024-01-01 12:00:00",
      "liked_count": 1234,
      "comments_count": 56,
      "shared_count": 12,
      "note_url": "https://www.xiaohongshu.com/explore/67e6c0c30000000009016264",
      "images": [
        "https://image1.url",
        "https://image2.url"
      ],
      "tags": ["美食", "探店", "推荐"],
      "location": "北京市朝阳区",
      "comments": [
        {
          "comment_id": "comment123",
          "content": "看起来很好吃！",
          "author": "用户A",
          "publish_time": "2024-01-01 12:30:00",
          "liked_count": 12
        }
      ]
    }
  ],
  "errors": [
    "部分内容获取失败: 网络超时",
    "评论采集异常: 权限不足"
  ]
}
```

#### 1.4 停止任务
**端点**: `DELETE /api/v1/tasks/{task_id}`

**响应**:
```json
{
  "message": "任务已停止",
  "task_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

#### 1.5 列出运行中的任务
**端点**: `GET /api/v1/tasks`

**响应**:
```json
{
  "running_tasks": [
    {
      "task_id": "task1",
      "platform": "xhs",
      "task_type": "search",
      "status": "running",
      "created_at": "2024-01-01T12:00:00Z",
      "progress_percent": 45.6
    }
  ],
  "count": 1
}
```

### 2. 数据查询接口

#### 2.1 获取内容列表
**端点**: `GET /api/v1/data/content/{platform}`

**查询参数**:
- `source_type`: 数据源类型 (json/csv/supabase)，默认 json
- `limit`: 返回数量限制，默认 20，最大 100
- `offset`: 偏移量，默认 0
- `task_id`: 按任务ID过滤
- `user_id`: 按用户ID过滤
- `keyword`: 关键词搜索

**响应**:
```json
{
  "data": [
    {
      "note_id": "67e6c0c30000000009016264",
      "title": "美食分享",
      "author": "美食达人",
      "publish_time": "2024-01-01 12:00:00",
      "liked_count": 1234,
      "comments_count": 56
    }
  ],
  "total": 500,
  "limit": 20,
  "offset": 0,
  "platform": "xhs",
  "source_type": "json",
  "message": "数据获取成功"
}
```

#### 2.2 获取内容详情
**端点**: `GET /api/v1/data/content/{platform}/{content_id}`

**查询参数**:
- `source_type`: 数据源类型，默认 json

#### 2.3 搜索内容
**端点**: `GET /api/v1/data/search/{platform}`

**查询参数**:
- `keyword`: 搜索关键词 (必填)
- `source_type`: 数据源类型，默认 json
- `limit`: 返回数量限制，默认 20
- `offset`: 偏移量，默认 0

#### 2.4 获取用户内容
**端点**: `GET /api/v1/data/user/{platform}/{user_id}/content`

#### 2.5 获取任务结果
**端点**: `GET /api/v1/data/task/{task_id}/results`

**查询参数**:
- `source_type`: 数据源类型，默认 json
- `platform`: 平台名称，默认 xhs

#### 2.6 获取平台统计
**端点**: `GET /api/v1/data/stats/{platform}`

**响应**:
```json
{
  "stats": {
    "total_content": 10000,
    "total_comments": 50000,
    "total_users": 1000,
    "latest_update": "2024-01-01T12:00:00Z",
    "data_size_mb": 256.7
  },
  "platform": "xhs",
  "source_type": "json"
}
```

### 3. 登录管理接口

#### 3.1 创建登录会话
**端点**: `POST /api/v1/login/create-session`

**请求体**:
```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "platform": "xhs",
  "login_type": "qrcode",              // qrcode/phone/cookie
  "timeout": 300,                      // 登录超时时间(秒)
  "cookies": "optional-cookie-string"  // cookie登录时使用
}
```

#### 3.2 获取登录状态
**端点**: `GET /api/v1/login/status/{task_id}`

**响应**:
```json
{
  "success": true,
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "qrcode_generated",        // 登录状态
  "message": "二维码已生成，请扫码登录",
  "data": {
    "login_url": "https://login.url",
    "expires_at": "2024-01-01T12:05:00Z"
  },
  "qrcode_image": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgA...",
  "input_required": {
    "type": "phone",
    "prompt": "请输入手机号码"
  }
}
```

**登录状态值**:
- `created`: 会话已创建
- `qrcode_generated`: 二维码已生成
- `waiting_scan`: 等待扫码
- `scan_confirmed`: 扫码确认
- `input_required`: 需要输入信息
- `success`: 登录成功
- `failed`: 登录失败
- `timeout`: 登录超时

#### 3.3 提交登录输入
**端点**: `POST /api/v1/login/input/{task_id}`

**请求体**:
```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "input_type": "phone",               // phone/verification_code
  "value": "13800138000"
}
```

#### 3.4 保存登录Cookies
**端点**: `POST /api/v1/login/save-cookies`

**请求体**:
```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "cookies": "session_id=abc123; user_token=xyz789",
  "platform": "xhs"
}
```

#### 3.5 刷新二维码
**端点**: `POST /api/v1/login/refresh-qrcode/{task_id}`

#### 3.6 删除登录会话
**端点**: `DELETE /api/v1/login/session/{task_id}`

### 4. 系统管理接口

#### 4.1 健康检查
**端点**: `GET /api/v1/data/health`

**响应**:
```json
{
  "status": "healthy",
  "data_sources": {
    "json_reader": true,
    "csv_reader": true,
    "supabase_reader": false
  },
  "app_version": "1.0.0",
  "supported_platforms": 7
}
```

#### 4.2 获取支持的平台
**端点**: `GET /api/v1/data/platforms`

**响应**:
```json
{
  "platforms": [
    {
      "key": "xhs",
      "name": "小红书",
      "delay_range": [2, 4],
      "max_comments": 100,
      "timeout": 45
    }
  ],
  "total": 7
}
```

#### 4.3 获取数据源类型
**端点**: `GET /api/v1/data/sources`

**响应**:
```json
{
  "sources": [
    {
      "type": "json",
      "name": "JSON",
      "healthy": true,
      "description": "JSON 数据存储"
    }
  ],
  "total": 3
}
```

#### 4.4 获取配置选项
**端点**: `GET /api/v1/system/config/options`

**响应**:
```json
{
  "message": "支持的配置选项",
  "options": {
    "crawler_config_request": {
      "model": "CrawlerConfigRequest",
      "fields": {
        "enable_proxy": {
          "type": "boolean",
          "required": false,
          "description": "是否启用代理"
        }
      },
      "description": "API请求中可传递的爬虫配置参数"
    },
    "crawler_config": {
      "model": "CrawlerConfig",
      "fields": {...},
      "description": "最终生效的完整爬虫配置"
    },
    "storage_config": {
      "model": "StorageConfig", 
      "fields": {...},
      "description": "数据存储配置"
    },
    "supported_platforms": [...]
  }
}
```

#### 4.5 系统统计
**端点**: `GET /api/v1/system/stats`

**响应**:
```json
{
  "total_tasks": 1500,
  "completed_tasks": 1450,
  "failed_tasks": 30,
  "running_tasks": 20,
  "success_rate": 96.7,
  "avg_task_duration": 45.6,
  "total_data_collected": 150000,
  "system_uptime": 86400,
  "last_restart": "2024-01-01T00:00:00Z"
}
```

#### 4.6 清理已完成任务
**端点**: `POST /api/v1/maintenance/cleanup`

### 5. Cookies管理接口

#### 5.1 获取Cookies状态
**端点**: `GET /api/v1/cookies/{platform}/status`

#### 5.2 列出所有Cookies
**端点**: `GET /api/v1/cookies`

#### 5.3 清除平台Cookies
**端点**: `DELETE /api/v1/cookies/{platform}`

#### 5.4 清除所有Cookies
**端点**: `DELETE /api/v1/cookies`

#### 5.5 手动保存Cookies
**端点**: `POST /api/v1/cookies`

## 🔒 错误处理

### 标准错误响应格式
```json
{
  "detail": "错误描述信息",
  "error_code": "VALIDATION_ERROR",
  "timestamp": "2024-01-01T12:00:00Z",
  "path": "/api/v1/tasks",
  "method": "POST"
}
```

### 常见错误码
- `400`: 请求参数错误
- `401`: 未授权访问
- `404`: 资源不存在
- `422`: 数据验证失败
- `429`: 请求频率限制
- `500`: 服务器内部错误
- `503`: 服务不可用

### 配置验证错误示例
```json
{
  "detail": [
    {
      "loc": ["config", "delay_range"],
      "msg": "delay_range第一个值应该小于或等于第二个值",
      "type": "value_error"
    },
    {
      "loc": ["config", "window_size"],
      "msg": "String should match pattern '^\\d+,\\d+$'",
      "type": "string_pattern_mismatch"
    }
  ]
}
```

## 📊 性能指标

### 接口性能基准
- 任务创建: < 200ms
- 状态查询: < 100ms
- 数据查询: < 500ms
- 登录状态: < 150ms

### 并发限制
- 同时运行任务数: 10个
- API 请求频率: 100次/分钟
- 数据查询限制: 1000条/次

## 📝 更新日志

### v2.0.0 (2025-06-25)
- ✨ 全新的基于 Pydantic 模型的配置管理
- 🔧 统一配置收口到 ConfigManager
- 🛡️ 增强的类型安全和参数验证
- 📁 模块重构：dataAccess → dataReader
- 🚀 性能优化和错误处理改进

### v1.0.0 (2024-12-01)
- 🎉 初始版本发布
- 📡 基础 API 接口实现
- 🔄 多平台爬虫支持
- 💾 多种数据存储方式

---

**文档维护**: 请在代码变更时同步更新此文档 