# MediaCrawler API Server 部署指南

## 📋 部署概述

本文档详细介绍了 MediaCrawler API Server 的各种部署方式，包括开发环境、生产环境、Docker 容器化部署以及云服务部署等。

## 🛠️ 系统要求

### 最低配置
- **CPU**: 2 核心
- **内存**: 4GB RAM
- **存储**: 20GB 可用空间
- **操作系统**: Ubuntu 20.04+, CentOS 8+, macOS 10.15+, Windows 10+
- **Python**: 3.8+

### 推荐配置
- **CPU**: 4 核心 或更多
- **内存**: 8GB RAM 或更多
- **存储**: 50GB SSD
- **网络**: 稳定的互联网连接

### 软件依赖
- Python 3.8+
- pip
- Git
- Chrome/Chromium 浏览器
- Redis (可选，用于缓存)
- PostgreSQL/MySQL (可选，用于生产环境)

## 🚀 快速部署

### 方式一：本地开发部署

1. **克隆项目**
```bash
git clone https://github.com/your-repo/MediaCrawler-ApiServer.git
cd MediaCrawler-ApiServer
```

2. **创建虚拟环境**
```bash
python -m venv venv

# Linux/macOS
source venv/bin/activate

# Windows
venv\Scripts\activate
```

3. **安装依赖**
```bash
pip install -r requirements.txt
```

4. **配置环境变量**
```bash
cp config.env.example .env
```

编辑 `.env` 文件：
```bash
# 基本配置
APP_NAME=MediaCrawler API Server
APP_VERSION=1.0.0
DEBUG=true
LOG_LEVEL=INFO

# 数据库配置 (可选)
DATABASE_URL=sqlite:///./data/app.db

# Supabase 配置 (可选)
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key

# 爬虫默认配置
DEFAULT_HEADLESS=true
DEFAULT_ENABLE_PROXY=false
DEFAULT_MAX_RETRIES=3
DEFAULT_TIMEOUT=30

# 代理配置 (可选)
DEFAULT_PROXY_PROVIDER=kuaidaili
KUAIDAILI_USERNAME=your_username
KUAIDAILI_PASSWORD=your_password
```

5. **创建数据目录**
```bash
mkdir -p data/xhs/json data/xhs/csv
mkdir -p logs
```

6. **启动服务**
```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

7. **验证部署**
```bash
curl http://localhost:8000/
curl http://localhost:8000/api/v1/data/health
```

### 方式二：Docker 部署

1. **创建 Dockerfile**
```dockerfile
FROM python:3.9-slim

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    chromium \
    chromium-driver \
    fonts-liberation \
    libappindicator3-1 \
    libasound2 \
    libatk-bridge2.0-0 \
    libnspr4 \
    libnss3 \
    libx11-xcb1 \
    libxcomposite1 \
    libxcursor1 \
    libxdamage1 \
    libxi6 \
    libxrandr2 \
    libxss1 \
    libxtst6 \
    xdg-utils \
    && rm -rf /var/lib/apt/lists/*

# 设置工作目录
WORKDIR /app

# 复制并安装Python依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 创建数据目录
RUN mkdir -p data/xhs/json data/xhs/csv logs

# 设置环境变量
ENV PYTHONPATH=/app
ENV CHROME_BIN=/usr/bin/chromium
ENV CHROME_DRIVER=/usr/bin/chromedriver

# 暴露端口
EXPOSE 8000

# 健康检查
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/v1/data/health || exit 1

# 启动命令
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

2. **创建 docker-compose.yml**
```yaml
version: '3.8'

services:
  mediacrawler-api:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
      - ./config.env:/app/.env
    environment:
      - PYTHONPATH=/app
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/api/v1/data/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 30s

  # 可选：Redis 缓存
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    restart: unless-stopped

  # 可选：PostgreSQL 数据库
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: mediacrawler
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: your_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    restart: unless-stopped

volumes:
  redis_data:
  postgres_data:
```

3. **构建并启动**
```bash
docker-compose up -d --build
```

4. **查看日志**
```bash
docker-compose logs -f mediacrawler-api
```

## 🌐 生产环境部署

### Nginx 反向代理配置

1. **安装 Nginx**
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install nginx

# CentOS/RHEL
sudo yum install nginx
```

2. **创建配置文件** `/etc/nginx/sites-available/mediacrawler-api`
```nginx
upstream mediacrawler_backend {
    server 127.0.0.1:8000;
    # 如果有多个实例，可以添加负载均衡
    # server 127.0.0.1:8001;
    # server 127.0.0.1:8002;
}

server {
    listen 80;
    server_name your-domain.com www.your-domain.com;

    # 重定向到 HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com www.your-domain.com;

    # SSL 证书配置
    ssl_certificate /path/to/your/certificate.crt;
    ssl_certificate_key /path/to/your/private.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;

    # 安全头
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload";

    # 客户端上传限制
    client_max_body_size 100M;

    # 日志配置
    access_log /var/log/nginx/mediacrawler_access.log;
    error_log /var/log/nginx/mediacrawler_error.log;

    # API 代理
    location / {
        proxy_pass http://mediacrawler_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket 支持
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        
        # 超时设置
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # 静态文件缓存
    location ~* \.(jpg|jpeg|png|gif|ico|css|js)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # 健康检查
    location /health {
        access_log off;
        proxy_pass http://mediacrawler_backend/api/v1/data/health;
    }
}
```

3. **启用配置**
```bash
sudo ln -s /etc/nginx/sites-available/mediacrawler-api /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### Systemd 服务配置

1. **创建服务文件** `/etc/systemd/system/mediacrawler-api.service`
```ini
[Unit]
Description=MediaCrawler API Server
After=network.target

[Service]
Type=exec
User=www-data
Group=www-data
WorkingDirectory=/opt/mediacrawler-api
Environment=PATH=/opt/mediacrawler-api/venv/bin
EnvironmentFile=/opt/mediacrawler-api/.env
ExecStart=/opt/mediacrawler-api/venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000 --workers 4
ExecReload=/bin/kill -HUP $MAINPID
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal
SyslogIdentifier=mediacrawler-api

# 安全设置
NoNewPrivileges=yes
PrivateTmp=yes
ProtectSystem=strict
ReadWritePaths=/opt/mediacrawler-api/data /opt/mediacrawler-api/logs
ProtectHome=yes

[Install]
WantedBy=multi-user.target
```

2. **部署应用代码**
```bash
sudo mkdir -p /opt/mediacrawler-api
sudo chown www-data:www-data /opt/mediacrawler-api

# 切换到 www-data 用户
sudo -u www-data -s

# 克隆代码
cd /opt/mediacrawler-api
git clone https://github.com/your-repo/MediaCrawler-ApiServer.git .

# 创建虚拟环境
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 配置环境变量
cp config.env.example .env
# 编辑 .env 文件...

# 创建数据目录
mkdir -p data/xhs/json data/xhs/csv logs
```

3. **启动服务**
```bash
sudo systemctl daemon-reload
sudo systemctl enable mediacrawler-api
sudo systemctl start mediacrawler-api
sudo systemctl status mediacrawler-api
```

### 监控和日志

1. **日志轮转** `/etc/logrotate.d/mediacrawler-api`
```
/opt/mediacrawler-api/logs/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    postrotate
        systemctl reload mediacrawler-api
    endscript
}
```

2. **监控脚本** `monitor.sh`
```bash
#!/bin/bash

# 健康检查
health_check() {
    response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/api/v1/data/health)
    if [ "$response" -eq 200 ]; then
        echo "$(date): Health check passed"
        return 0
    else
        echo "$(date): Health check failed with code $response"
        return 1
    fi
}

# 内存使用检查
memory_check() {
    memory_usage=$(ps -o pid,ppid,user,%mem,%cpu,cmd -C python | grep uvicorn | awk '{sum+=$4} END {print sum}')
    if [ $(echo "$memory_usage > 80" | bc) -eq 1 ]; then
        echo "$(date): High memory usage: $memory_usage%"
        # 发送告警...
    fi
}

# 磁盘空间检查
disk_check() {
    disk_usage=$(df /opt/mediacrawler-api | awk 'NR==2 {print $5}' | sed 's/%//')
    if [ "$disk_usage" -gt 85 ]; then
        echo "$(date): High disk usage: $disk_usage%"
        # 清理旧日志或数据...
    fi
}

# 执行检查
health_check || exit 1
memory_check
disk_check
```

3. **Crontab 定时任务**
```bash
# 编辑定时任务
crontab -e

# 添加监控任务
*/5 * * * * /opt/mediacrawler-api/monitor.sh >> /var/log/mediacrawler-monitor.log 2>&1

# 每日数据备份
0 2 * * * /opt/mediacrawler-api/backup.sh >> /var/log/mediacrawler-backup.log 2>&1
```

## ☁️ 云服务部署

### AWS ECS 部署

1. **创建 ECS 任务定义**
```json
{
  "family": "mediacrawler-api",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "1024",
  "memory": "2048",
  "executionRoleArn": "arn:aws:iam::YOUR_ACCOUNT:role/ecsTaskExecutionRole",
  "containerDefinitions": [
    {
      "name": "mediacrawler-api",
      "image": "your-account.dkr.ecr.region.amazonaws.com/mediacrawler-api:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "DATABASE_URL",
          "value": "postgresql://user:pass@rds-endpoint:5432/db"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/mediacrawler-api",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      },
      "healthCheck": {
        "command": [
          "CMD-SHELL",
          "curl -f http://localhost:8000/api/v1/data/health || exit 1"
        ],
        "interval": 30,
        "timeout": 5,
        "retries": 3,
        "startPeriod": 60
      }
    }
  ]
}
```

2. **创建 ECS 服务**
```bash
aws ecs create-service \
  --cluster your-cluster \
  --service-name mediacrawler-api \
  --task-definition mediacrawler-api:1 \
  --desired-count 2 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-12345],securityGroups=[sg-12345],assignPublicIp=ENABLED}" \
  --load-balancers "targetGroupArn=arn:aws:elasticloadbalancing:...,containerName=mediacrawler-api,containerPort=8000"
```

### Google Cloud Run 部署

1. **构建镜像并推送到 GCR**
```bash
# 构建镜像
docker build -t gcr.io/YOUR_PROJECT_ID/mediacrawler-api .

# 推送到 Google Container Registry
docker push gcr.io/YOUR_PROJECT_ID/mediacrawler-api
```

2. **部署到 Cloud Run**
```bash
gcloud run deploy mediacrawler-api \
  --image gcr.io/YOUR_PROJECT_ID/mediacrawler-api \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 2 \
  --min-instances 1 \
  --max-instances 10 \
  --set-env-vars DATABASE_URL="postgresql://...",SUPABASE_URL="..."
```

### Azure Container Instances 部署

```bash
az container create \
  --resource-group myResourceGroup \
  --name mediacrawler-api \
  --image your-registry.azurecr.io/mediacrawler-api:latest \
  --cpu 2 \
  --memory 4 \
  --port 8000 \
  --environment-variables DATABASE_URL="postgresql://..." \
  --restart-policy Always
```

## 🔧 配置优化

### 生产环境配置调优

1. **Uvicorn 配置**
```bash
# 启动命令优化
uvicorn app.main:app \
  --host 0.0.0.0 \
  --port 8000 \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --access-log \
  --log-level info \
  --no-server-header
```

2. **环境变量优化**
```bash
# 生产环境配置
DEBUG=false
LOG_LEVEL=WARNING
DEFAULT_HEADLESS=true
DEFAULT_ENABLE_PROXY=true
DEFAULT_MAX_RETRIES=3
DEFAULT_TIMEOUT=45

# 数据库连接池
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=10

# 缓存配置
REDIS_URL=redis://localhost:6379/0
CACHE_TTL=3600
```

### 性能优化

1. **数据库优化**
```sql
-- 创建索引
CREATE INDEX idx_content_platform_created ON contents(platform, created_at);
CREATE INDEX idx_content_task_id ON contents(task_id);
CREATE INDEX idx_comments_content_id ON comments(content_id);

-- 分区表（大数据量时）
CREATE TABLE contents_2024 PARTITION OF contents
FOR VALUES FROM ('2024-01-01') TO ('2025-01-01');
```

2. **缓存策略**
```python
# Redis 缓存配置
CACHE_CONFIG = {
    'task_results': 3600,      # 任务结果缓存1小时
    'platform_stats': 1800,   # 平台统计缓存30分钟
    'content_list': 600,       # 内容列表缓存10分钟
}
```

## 🔐 安全配置

### SSL/TLS 配置

1. **Let's Encrypt 证书**
```bash
# 安装 Certbot
sudo apt install certbot python3-certbot-nginx

# 获取证书
sudo certbot --nginx -d your-domain.com

# 自动续期
sudo crontab -e
0 12 * * * /usr/bin/certbot renew --quiet
```

### 防火墙配置

```bash
# UFW 配置
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw --force enable

# 限制 API 访问频率
sudo ufw limit 80/tcp
sudo ufw limit 443/tcp
```

### API 安全

1. **速率限制**
```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@limiter.limit("100/minute")
@app.post("/api/v1/tasks")
async def create_task(request: Request, ...):
    ...
```

2. **CORS 配置**
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-frontend.com"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)
```

## 🔄 备份和恢复

### 数据备份脚本

```bash
#!/bin/bash
# backup.sh

BACKUP_DIR="/opt/backups/mediacrawler"
DATE=$(date +%Y%m%d_%H%M%S)
APP_DIR="/opt/mediacrawler-api"

# 创建备份目录
mkdir -p $BACKUP_DIR

# 备份数据文件
tar -czf $BACKUP_DIR/data_$DATE.tar.gz -C $APP_DIR data/

# 备份数据库 (如果使用 PostgreSQL)
pg_dump mediacrawler > $BACKUP_DIR/database_$DATE.sql

# 压缩数据库备份
gzip $BACKUP_DIR/database_$DATE.sql

# 清理旧备份 (保留30天)
find $BACKUP_DIR -name "*.tar.gz" -mtime +30 -delete
find $BACKUP_DIR -name "*.sql.gz" -mtime +30 -delete

echo "Backup completed: $DATE"
```

### 恢复脚本

```bash
#!/bin/bash
# restore.sh

BACKUP_FILE=$1
if [ -z "$BACKUP_FILE" ]; then
    echo "Usage: $0 <backup_file>"
    exit 1
fi

APP_DIR="/opt/mediacrawler-api"

# 停止服务
sudo systemctl stop mediacrawler-api

# 恢复数据文件
tar -xzf $BACKUP_FILE -C $APP_DIR

# 恢复数据库 (如果有)
if [ -f "$2" ]; then
    gunzip -c $2 | psql mediacrawler
fi

# 重启服务
sudo systemctl start mediacrawler-api

echo "Restore completed"
```

## 📊 监控和告警

### Prometheus 监控

1. **安装 Prometheus 客户端**
```bash
pip install prometheus-client
```

2. **添加监控指标**
```python
from prometheus_client import Counter, Histogram, Gauge, generate_latest

# 定义指标
task_counter = Counter('mediacrawler_tasks_total', 'Total tasks', ['platform', 'status'])
request_duration = Histogram('mediacrawler_request_duration_seconds', 'Request duration')
active_tasks = Gauge('mediacrawler_active_tasks', 'Active tasks')

@app.get("/metrics")
async def metrics():
    return Response(generate_latest(), media_type="text/plain")
```

### Grafana 仪表板

```json
{
  "dashboard": {
    "title": "MediaCrawler API Server",
    "panels": [
      {
        "title": "Request Rate",
        "targets": [
          {
            "expr": "rate(mediacrawler_requests_total[5m])"
          }
        ]
      },
      {
        "title": "Active Tasks",
        "targets": [
          {
            "expr": "mediacrawler_active_tasks"
          }
        ]
      }
    ]
  }
}
```

## 🔍 故障排除

### 常见问题

1. **端口占用**
```bash
# 查找占用端口的进程
lsof -i :8000
netstat -tulpn | grep 8000

# 杀死进程
kill -9 <PID>
```

2. **内存不足**
```bash
# 检查内存使用
free -h
ps aux --sort=-%mem | head

# 增加交换空间
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

3. **浏览器驱动问题**
```bash
# 检查 Chrome 版本
google-chrome --version
chromium --version

# 更新驱动
sudo apt update
sudo apt install chromium chromium-driver
```

4. **权限问题**
```bash
# 检查文件权限
ls -la /opt/mediacrawler-api/

# 修复权限
sudo chown -R www-data:www-data /opt/mediacrawler-api/
sudo chmod -R 755 /opt/mediacrawler-api/
```

### 日志分析

```bash
# 查看应用日志
journalctl -u mediacrawler-api -f

# 查看错误日志
tail -f /opt/mediacrawler-api/logs/errors.log

# 分析访问日志
tail -f /var/log/nginx/mediacrawler_access.log | grep -E "50[0-9]|40[0-9]"
```

---

**注意**: 请根据实际环境调整配置参数，确保安全性和性能满足需求。 