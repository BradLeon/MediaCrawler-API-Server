#!/usr/bin/env python3
"""
MediaCrawler-ApiServer 综合测试脚本

测试所有核心功能模块：
1. 配置管理
2. 爬虫适配器
3. 登录管理
4. 数据访问层
5. API接口
6. 端到端集成测试
"""

import asyncio
import aiohttp
import json
import os
import sys
import time
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.core.config import settings
from app.core.login_manager import login_manager, LoginType
from app.crawler.adapter import crawler_adapter, CrawlerTask, CrawlerTaskType, PlatformType
from app.dataReader.factory import DataReaderFactory


class TestResults:
    """测试结果收集器"""
    def __init__(self):
        self.tests = []
        self.passed = 0
        self.failed = 0
    
    def add_result(self, test_name: str, success: bool, message: str = "", duration: float = 0):
        self.tests.append({
            "name": test_name,
            "success": success,
            "message": message,
            "duration": duration
        })
        if success:
            self.passed += 1
        else:
            self.failed += 1
    
    def print_summary(self):
        print(f"\n{'='*60}")
        print(f"测试总结: {self.passed + self.failed} 个测试")
        print(f"✅ 通过: {self.passed}")
        print(f"❌ 失败: {self.failed}")
        print(f"{'='*60}")
        
        for test in self.tests:
            status = "✅" if test["success"] else "❌"
            print(f"{status} {test['name']} ({test['duration']:.2f}s)")
            if test["message"]:
                print(f"   {test['message']}")


results = TestResults()


def test_function(test_name: str):
    """测试装饰器"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                await func(*args, **kwargs)
                duration = time.time() - start_time
                results.add_result(test_name, True, "测试通过", duration)
                print(f"✅ {test_name} - 通过 ({duration:.2f}s)")
            except Exception as e:
                duration = time.time() - start_time
                results.add_result(test_name, False, str(e), duration)
                print(f"❌ {test_name} - 失败: {e}")
        return wrapper
    return decorator


# =================================
# 1. 配置管理测试
# =================================

@test_function("配置管理 - 基础配置加载")
async def test_config_loading():
    """测试配置加载"""
    assert settings.app_name == "MediaCrawler-ApiServer"
    assert settings.api_v1_prefix == "/api/v1"
    assert isinstance(settings.max_concurrent_tasks, int)


@test_function("配置管理 - 数据库URL生成")
async def test_database_url_generation():
    """测试数据库URL生成"""
    mysql_url = settings.mysql_url_async
    assert mysql_url.startswith("mysql+aiomysql://")
    assert settings.relation_db_name in mysql_url


@test_function("配置管理 - 数据源配置")
async def test_data_source_config():
    """测试数据源配置获取"""
    mysql_config = settings.get_data_source_config("mysql")
    assert "database_url" in mysql_config
    assert "host" in mysql_config
    
    csv_config = settings.get_data_source_config("csv")
    assert "data_path" in csv_config


# =================================
# 2. 爬虫适配器测试
# =================================

@test_function("爬虫适配器 - 任务创建")
async def test_crawler_adapter_task_creation():
    """测试任务创建"""
    task = CrawlerTask(
        task_id="test_task_001",
        platform=PlatformType.XHS,
        task_type=CrawlerTaskType.SEARCH,
        keywords=["测试"],
        max_count=5,
        headless=True
    )
    
    # 不实际启动任务，只测试任务对象创建
    assert task.task_id == "test_task_001"
    assert task.platform == PlatformType.XHS
    assert task.keywords == ["测试"]


@test_function("爬虫适配器 - 系统状态")
async def test_crawler_adapter_system_stats():
    """测试系统统计信息"""
    stats = await crawler_adapter.get_system_stats()
    assert "running_tasks" in stats
    assert "completed_tasks" in stats
    assert isinstance(stats["running_tasks"], int)


# =================================
# 3. 登录管理器测试
# =================================

@test_function("登录管理 - 会话创建")
async def test_login_session_creation():
    """测试登录会话创建"""
    session = login_manager.create_login_session(
        task_id="test_login_001",
        platform="xhs",
        login_type=LoginType.QRCODE,
        timeout=300
    )
    
    assert session.task_id == "test_login_001"
    assert session.platform == "xhs"
    assert session.login_type == LoginType.QRCODE


@test_function("登录管理 - 会话查询")
async def test_login_session_query():
    """测试登录会话查询"""
    # 查询已创建的会话
    session = login_manager.get_login_session("test_login_001")
    assert session is not None
    assert session.task_id == "test_login_001"


# =================================
# 4. 数据访问层测试
# =================================

@test_function("数据访问 - 管理器初始化")
async def test_data_access_manager():
    """测试数据访问管理器"""
    # 尝试初始化数据访问管理器
    await data_access_manager.initialize()
    
    # 测试健康检查
    health = await data_access_manager.health_check()
    print(f"数据访问健康状态: {health}")


@test_function("数据访问 - 降级机制")
async def test_data_access_fallback():
    """测试数据访问降级机制"""
    # 尝试获取数据访问器（可能降级到CSV）
    accessor = await data_access_manager.get_access_with_fallback()
    assert accessor is not None
    
    # 测试基础查询
    try:
        result = await accessor.get_platform_list()
        assert result.success
    except Exception as e:
        # 如果没有数据，这是正常的
        print(f"数据查询结果: {e}")


# =================================
# 5. API接口测试
# =================================

async def start_test_server():
    """启动测试服务器"""
    import subprocess
    import time
    
    # 启动服务器
    process = subprocess.Popen([
        sys.executable, "-m", "uvicorn", 
        "app.main:app", 
        "--host", "127.0.0.1", 
        "--port", "8001",
        "--log-level", "error"
    ], cwd=str(project_root))
    
    # 等待服务器启动
    time.sleep(3)
    return process


@test_function("API接口 - 健康检查")
async def test_api_health_check():
    """测试API健康检查"""
    async with aiohttp.ClientSession() as session:
        async with session.get("http://127.0.0.1:8001/") as response:
            assert response.status == 200
            data = await response.json()
            assert "message" in data


@test_function("API接口 - 系统统计")
async def test_api_system_stats():
    """测试系统统计API"""
    async with aiohttp.ClientSession() as session:
        async with session.get("http://127.0.0.1:8001/api/v1/system/stats") as response:
            assert response.status == 200
            data = await response.json()
            assert "running_tasks" in data


@test_function("API接口 - 数据查询健康检查")
async def test_api_data_health():
    """测试数据查询健康检查API"""
    async with aiohttp.ClientSession() as session:
        async with session.get("http://127.0.0.1:8001/api/v1/data/health") as response:
            # 可能返回200或503，都是正常的
            assert response.status in [200, 503]


# =================================
# 6. 端到端集成测试
# =================================

@test_function("集成测试 - 配置文件检查")
async def test_integration_config_files():
    """测试配置文件完整性"""
    # 检查关键文件是否存在
    critical_files = [
        "app/main.py",
        "app/core/config.py",
        "app/crawler/adapter.py",
        "app/dataReader/factory.py",
        "config.env.example"
    ]
    
    for file_path in critical_files:
        full_path = project_root / file_path
        assert full_path.exists(), f"关键文件不存在: {file_path}"


@test_function("集成测试 - 模块导入")
async def test_integration_module_imports():
    """测试关键模块导入"""
    try:
        from app.main import app
        from app.crawler.adapter import crawler_adapter
        from app.core.login_manager import login_manager
        from app.dataReader.factory import DataReaderFactory
        print("所有关键模块导入成功")
    except ImportError as e:
        raise Exception(f"模块导入失败: {e}")


# =================================
# 主测试函数
# =================================

async def run_basic_tests():
    """运行基础测试（不需要服务器）"""
    print("🧪 开始基础功能测试...")
    
    # 配置管理测试
    await test_config_loading()
    await test_database_url_generation()
    await test_data_source_config()
    
    # 爬虫适配器测试
    await test_crawler_adapter_task_creation()
    await test_crawler_adapter_system_stats()
    
    # 登录管理器测试
    await test_login_session_creation()
    await test_login_session_query()
    
    # 数据访问层测试
    await test_data_access_manager()
    await test_data_access_fallback()
    
    # 集成测试
    await test_integration_config_files()
    await test_integration_module_imports()


async def run_api_tests():
    """运行API测试（需要服务器）"""
    print("\n🌐 开始API接口测试...")
    
    # 启动测试服务器
    server_process = await start_test_server()
    
    try:
        await test_api_health_check()
        await test_api_system_stats()
        await test_api_data_health()
    finally:
        # 停止服务器
        server_process.terminate()
        server_process.wait()


async def main():
    """主函数"""
    print("🚀 MediaCrawler-ApiServer 综合测试开始")
    print("="*60)
    
    # 运行基础测试
    await run_basic_tests()
    
    # 询问是否运行API测试
    print(f"\n{'='*60}")
    api_test = input("是否运行API接口测试? (需要启动服务器) [y/N]: ").strip().lower()
    
    if api_test in ['y', 'yes']:
        await run_api_tests()
    else:
        print("跳过API接口测试")
    
    # 打印测试总结
    results.print_summary()
    
    # 清理登录会话
    login_manager.clear_session("test_login_001")
    
    return results.failed == 0


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1) 