"""
MediaCrawler 适配器测试脚本

测试通过进程方式调用原MediaCrawler项目的功能
"""

import asyncio
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.crawler.adapter import (
    crawler_adapter, 
    CrawlerTask, 
    CrawlerTaskType
)
from app.dataReader.base import PlatformType


async def test_crawler_adapter():
    """测试爬虫适配器"""
    
    print("🚀 开始测试MediaCrawler适配器")
    
    # 创建测试任务
    task = CrawlerTask(
        task_id="test_001",
        platform=PlatformType.XHS,
        task_type=CrawlerTaskType.SEARCH,
        keywords=["美食", "旅行"],
        max_count=5,
        max_comments=10,
        headless=True,
        save_data_option="json"  # 使用json保存，避免数据库依赖
    )
    
    print(f"📋 创建任务: {task.task_id}")
    print(f"   平台: {task.platform.value}")
    print(f"   类型: {task.task_type.value}")
    print(f"   关键词: {task.keywords}")
    print(f"   最大数量: {task.max_count}")
    
    try:
        # 启动任务
        task_id = await crawler_adapter.start_crawler_task(task)
        print(f"✅ 任务启动成功: {task_id}")
        
        # 监控任务状态
        print("\n📊 监控任务状态:")
        while True:
            status = await crawler_adapter.get_task_status(task_id)
            print(f"   状态: {status.get('status')}")
            
            if status.get('progress'):
                progress = status['progress']
                print(f"   进度: {progress.get('stage')} - {progress.get('percentage', 0):.1f}%")
            
            if status.get('done'):
                break
                
            await asyncio.sleep(2)
        
        # 获取最终结果
        result = await crawler_adapter.get_task_result(task_id)
        if result:
            print(f"\n📈 任务结果:")
            print(f"   成功: {result.success}")
            print(f"   消息: {result.message}")
            print(f"   数据数量: {result.data_count}")
            
            if result.errors:
                print(f"   错误: {result.errors}")
        
        # 获取任务事件日志
        events = await crawler_adapter.get_task_events(task_id, limit=10)
        print(f"\n📝 任务事件日志 (最近10条):")
        for event in events[-5:]:  # 显示最后5条
            print(f"   [{event['timestamp']}] {event['event_type']}: {event['message']}")
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()


async def test_multiple_tasks():
    """测试多任务并发"""
    
    print("\n🔥 测试多任务并发")
    
    tasks = [
        CrawlerTask(
            task_id=f"multi_test_{i}",
            platform=PlatformType.XHS,
            task_type=CrawlerTaskType.SEARCH,
            keywords=[f"测试关键词{i}"],
            max_count=3,
            headless=True,
            save_data_option="json"
        )
        for i in range(1, 4)
    ]
    
    # 启动所有任务
    task_ids = []
    for task in tasks:
        try:
            task_id = await crawler_adapter.start_crawler_task(task)
            task_ids.append(task_id)
            print(f"✅ 任务 {task_id} 启动成功")
        except Exception as e:
            print(f"❌ 任务 {task.task_id} 启动失败: {e}")
    
    # 等待所有任务完成
    print(f"\n⏳ 等待 {len(task_ids)} 个任务完成...")
    
    while task_ids:
        for task_id in task_ids.copy():
            status = await crawler_adapter.get_task_status(task_id)
            if status.get('done'):
                result = await crawler_adapter.get_task_result(task_id)
                print(f"✅ 任务 {task_id} 完成: {result.success if result else 'Unknown'}")
                task_ids.remove(task_id)
        
        if task_ids:
            await asyncio.sleep(1)


async def test_task_management():
    """测试任务管理功能"""
    
    print("\n📊 测试任务管理功能")
    
    # 创建一个长期运行的任务
    task = CrawlerTask(
        task_id="management_test",
        platform=PlatformType.XHS,
        task_type=CrawlerTaskType.SEARCH,
        keywords=["长期任务测试"],
        max_count=50,  # 较大的数量，确保任务运行时间足够长
        headless=True,
        save_data_option="json"
    )
    
    try:
        # 启动任务
        task_id = await crawler_adapter.start_crawler_task(task)
        print(f"✅ 启动长期任务: {task_id}")
        
        # 等待一段时间
        await asyncio.sleep(5)
        
        # 检查运行中的任务列表
        running_tasks = await crawler_adapter.list_running_tasks()
        print(f"📋 运行中的任务: {running_tasks}")
        
        # 停止任务
        success = await crawler_adapter.stop_task(task_id)
        print(f"⏹️ 停止任务结果: {success}")
        
        # 再次检查运行中的任务
        running_tasks = await crawler_adapter.list_running_tasks()
        print(f"📋 停止后运行中的任务: {running_tasks}")
        
    except Exception as e:
        print(f"❌ 任务管理测试失败: {e}")


def check_mediacrawler_availability():
    """检查原MediaCrawler项目是否可用"""
    
    print("🔍 检查原MediaCrawler项目...")
    
    mediacrawler_path = os.path.join(
        os.path.dirname(__file__), "..", "MediaCrawler"
    )
    main_py_path = os.path.join(mediacrawler_path, "main.py")
    
    if os.path.exists(main_py_path):
        print(f"✅ 找到原MediaCrawler: {main_py_path}")
        return True
    else:
        print(f"❌ 未找到原MediaCrawler: {main_py_path}")
        print("   请确保原MediaCrawler项目位于正确的路径")
        return False


async def main():
    """主测试函数"""
    
    print("=" * 60)
    print("🧪 MediaCrawler适配器测试")
    print("=" * 60)
    
    # 检查原项目可用性
    if not check_mediacrawler_availability():
        print("\n⚠️ 跳过测试，因为原MediaCrawler项目不可用")
        return
    
    try:
        # 单任务测试
        await test_crawler_adapter()
        
        # 多任务测试
        await test_multiple_tasks()
        
        # 任务管理测试
        await test_task_management()
        
        print("\n🎉 所有测试完成!")
        
    except KeyboardInterrupt:
        print("\n⏹️ 测试被用户中断")
    except Exception as e:
        print(f"\n❌ 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main()) 