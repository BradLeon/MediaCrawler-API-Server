#!/usr/bin/env python3
"""
MediaCrawler API Server 启动脚本
解决模块导入问题
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.absolute()
sys.path.insert(0, str(project_root))

if __name__ == "__main__":
    # 导入并运行主应用
    import uvicorn
    
    # 设置环境变量
    os.environ.setdefault("PYTHONPATH", str(project_root))
    
    # 启动服务器
    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="info"
    ) 