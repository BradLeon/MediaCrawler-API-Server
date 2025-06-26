# MediaCrawler API Server 安装文档

## 📦 依赖安装总结

### ✅ 安装状态
- **总计安装包数量**: 120个
- **安装状态**: 全部成功 ✅
- **Playwright浏览器**: 已安装 ✅
- **项目模块**: 导入正常 ✅

### 🔧 核心依赖包

#### Web框架和API
- `fastapi>=0.110.2` - 现代化的Web框架
- `uvicorn>=0.29.0` - ASGI服务器
- `pydantic>=2.5.2` - 数据验证
- `pydantic-settings>=2.0.0` - 配置管理

#### 异步HTTP客户端
- `httpx>=0.27.0` - 现代异步HTTP客户端
- `aiohttp>=3.9.0` - 异步HTTP客户端库
- `requests>=2.32.3` - 传统HTTP客户端

#### 浏览器自动化
- `playwright>=1.42.0` - 浏览器自动化框架

#### 数据库和存储
- `asyncpg>=0.29.0` - PostgreSQL异步驱动
- `sqlalchemy>=2.0.0` - SQL ORM框架
- `supabase>=2.15.2` - Supabase客户端
- `aiomysql>=0.2.0` - MySQL异步驱动

#### 缓存和队列
- `redis>=4.6.0` - Redis客户端
- `celery>=5.3.0` - 分布式任务队列

#### 数据处理
- `pandas>=2.2.3` - 数据分析库
- `parsel>=1.9.1` - HTML/XML解析
- `jieba>=0.42.1` - 中文分词

#### 图像处理
- `Pillow>=10.0.0` - 图像处理库
- `opencv-python>=4.8.0` - 计算机视觉库

#### 工具库
- `tenacity>=8.2.2` - 重试机制
- `fake-useragent>=1.4.0` - 用户代理生成
- `python-dotenv>=1.0.1` - 环境变量管理

### 🛠️ 安装命令

```bash
# 1. 安装Python依赖
pip install -r requirements.txt

# 2. 安装Playwright浏览器
playwright install

# 3. 验证安装
python -c "import fastapi, uvicorn, playwright, supabase; print('✅ 安装成功！')"
```

### 📋 Requirements.txt 结构

我们的 `requirements.txt` 按功能分类组织：

```text
# === 核心框架 ===
fastapi>=0.110.2
uvicorn>=0.29.0
pydantic>=2.5.2
pydantic-settings>=2.0.0

# === 异步HTTP客户端 ===
httpx>=0.27.0
aiohttp>=3.9.0
requests>=2.32.3

# === 浏览器自动化 ===
playwright>=1.42.0

# === 数据库和存储 ===
asyncpg>=0.29.0
sqlalchemy>=2.0.0
supabase>=2.15.2
aiomysql>=0.2.0

# ... 更多分类
```

### 🔍 版本兼容性

- **Python**: 3.12+ (推荐)
- **操作系统**: macOS, Linux, Windows
- **数据库**: PostgreSQL 12+, MySQL 8+
- **Redis**: 6.0+

### 🚀 启动验证

安装完成后，可以通过以下方式验证：

```bash
# 测试核心模块导入
python -c "from app.core.config import get_settings; print('✅ 配置模块正常')"

# 测试数据模型
python -c "from app.models.base import Base; print('✅ 数据模型正常')"

# 测试存储适配器
python -c "from app.storage.base import AbstractStorage; print('✅ 存储适配器正常')"
```

### 📝 注意事项

1. **Pydantic版本更新**: 新版本将`BaseSettings`移至`pydantic-settings`包
2. **Playwright浏览器**: 首次安装需要下载浏览器驱动（约200MB）
3. **环境变量**: 生产环境需要配置`.env`文件
4. **数据库连接**: 需要配置Supabase或PostgreSQL连接信息

### 🔧 故障排除

#### 常见问题

**1. Pydantic导入错误**
```bash
# 错误: cannot import name 'BaseSettings' from 'pydantic'
# 解决: 已修复，使用 pydantic-settings 包
```

**2. Playwright浏览器未安装**
```bash
# 错误: Browser not found
# 解决: 运行 playwright install
```

**3. 模块导入失败**
```bash
# 错误: ModuleNotFoundError
# 解决: 确保在虚拟环境中运行，检查PYTHONPATH
```

### 📊 性能指标

- **安装时间**: ~5-10分钟（包含浏览器下载）
- **磁盘占用**: ~1.5GB（包含所有依赖和浏览器）
- **内存需求**: 最低2GB，推荐4GB+
- **启动时间**: ~3-5秒

### 🎯 下一步

安装完成后，您可以：

1. **配置环境变量**: 创建`.env`文件
2. **启动API服务**: `python -m app.main`
3. **运行客户端**: `python examples/unified_client_example.py`
4. **查看API文档**: http://localhost:8000/docs

---

**安装日期**: $(date)
**Python版本**: $(python --version)
**平台**: $(uname -s) 