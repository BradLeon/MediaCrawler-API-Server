#!/usr/bin/env python3
"""
MediaCrawler API Server 启动脚本

直接复用原MediaCrawler功能，提供FastAPI服务
"""

import uvicorn
import sys
import os

# 添加当前目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

if __name__ == "__main__":
    # 启动FastAPI服务
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # 开发模式下启用热重载
        log_level="info"
    ) 