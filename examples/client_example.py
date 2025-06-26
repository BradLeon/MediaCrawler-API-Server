#!/usr/bin/env python3
"""
MediaCrawler API Client 示例

演示如何使用增强的API功能：
1. 日志监控
2. 任务状态和进度查询
3. 自定义配置传递
"""

import asyncio
import aiohttp
import json
import time
from typing import Optional, Dict, Any


class MediaCrawlerClient:
    """MediaCrawler API客户端"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def create_task(self, 
                         platform: str, 
                         task_type: str,
                         keywords: Optional[list] = None,
                         content_ids: Optional[list] = None,
                         creator_ids: Optional[list] = None,
                         max_count: int = 100,
                         max_comments: int = 50,
                         custom_config: Optional[Dict[str, Any]] = None) -> str:
        """创建爬虫任务"""
        
        payload = {
            "platform": platform,
            "task_type": task_type,
            "keywords": keywords,
            "content_ids": content_ids,
            "creator_ids": creator_ids,
            "max_count": max_count,
            "max_comments": max_comments
        }
        
        if custom_config:
            payload["config"] = custom_config
        
        async with self.session.post(
            f"{self.base_url}/api/v1/tasks",
            json=payload
        ) as response:
            result = await response.json()
            if response.status == 200:
                return result["task_id"]
            else:
                raise Exception(f"创建任务失败: {result}")
    
    async def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """获取任务状态（包含详细进度）"""
        async with self.session.get(
            f"{self.base_url}/api/v1/tasks/{task_id}/status"
        ) as response:
            return await response.json()
    
    async def get_task_events(self, task_id: str, limit: int = 50) -> Dict[str, Any]:
        """获取任务事件日志"""
        async with self.session.get(
            f"{self.base_url}/api/v1/tasks/{task_id}/events?limit={limit}"
        ) as response:
            return await response.json()
    
    async def get_task_result(self, task_id: str) -> Dict[str, Any]:
        """获取任务结果"""
        async with self.session.get(
            f"{self.base_url}/api/v1/tasks/{task_id}/result"
        ) as response:
            return await response.json()
    
    async def stop_task(self, task_id: str) -> bool:
        """停止任务"""
        async with self.session.delete(
            f"{self.base_url}/api/v1/tasks/{task_id}"
        ) as response:
            return response.status == 200
    
    async def get_system_stats(self) -> Dict[str, Any]:
        """获取系统统计信息"""
        async with self.session.get(
            f"{self.base_url}/api/v1/system/stats"
        ) as response:
            return await response.json()
    
    async def get_config_options(self) -> Dict[str, Any]:
        """获取支持的配置选项"""
        async with self.session.get(
            f"{self.base_url}/api/v1/system/config/options"
        ) as response:
            return await response.json()
    
    async def wait_for_completion(self, task_id: str, 
                                 progress_callback=None,
                                 event_callback=None,
                                 check_interval: int = 5) -> Dict[str, Any]:
        """等待任务完成，支持进度和事件回调"""
        
        last_event_count = 0
        
        while True:
            # 获取任务状态
            status = await self.get_task_status(task_id)
            
            # 调用进度回调
            if progress_callback and "progress" in status:
                progress_callback(status["progress"])
            
            # 获取新事件
            if event_callback:
                events = await self.get_task_events(task_id, 100)
                new_events = events["events"][last_event_count:]
                if new_events:
                    for event in new_events:
                        event_callback(event)
                    last_event_count = len(events["events"])
            
            # 检查是否完成
            if status["done"]:
                return await self.get_task_result(task_id)
            
            await asyncio.sleep(check_interval)


async def demo_basic_usage():
    """基础使用示例"""
    print("=== 基础使用示例 ===")
    
    async with MediaCrawlerClient() as client:
        # 创建简单的搜索任务
        task_id = await client.create_task(
            platform="xhs",
            task_type="search", 
            keywords=["美食", "旅游"],
            max_count=20
        )
        print(f"创建任务: {task_id}")
        
        # 监控任务进度
        def progress_callback(progress):
            print(f"进度: {progress['current_stage']} - {progress['progress_percent']:.1f}% "
                  f"({progress['items_completed']}/{progress['items_total']})")
        
        def event_callback(event):
            print(f"事件: [{event['event_type']}] {event['message']}")
        
        # 等待完成
        result = await client.wait_for_completion(
            task_id, 
            progress_callback=progress_callback,
            event_callback=event_callback
        )
        
        print(f"任务完成: 成功={result['success']}, 数据量={result['data_count']}")


async def demo_custom_config():
    """自定义配置示例"""
    print("\n=== 自定义配置示例 ===")
    
    async with MediaCrawlerClient() as client:
        # 获取支持的配置选项
        config_options = await client.get_config_options()
        print("支持的配置选项:")
        print(json.dumps(config_options["options"], indent=2, ensure_ascii=False))
        
        # 使用自定义配置创建任务
        custom_config = {
            "headless": False,  # 显示浏览器
            "enable_proxy": True,  # 启用代理
            "max_notes_count": 50,  # 最大内容数量
            "crawler_interval": 2.0,  # 爬取间隔
            "login_type": "cookie",  # 登录方式
            "cookies": "your_cookies_here",  # Cookie
            "browser_type": "chromium",  # 浏览器类型
            "viewport_width": 1280,  # 视口宽度
            "viewport_height": 720,  # 视口高度
            "random_sleep_min": 1.0,  # 随机等待最小时间
            "random_sleep_max": 3.0,  # 随机等待最大时间
            "platform_specific": {  # 平台特定配置
                "specified_notes": ["note1", "note2"],  # 指定笔记ID
                "creator_ids": ["creator1", "creator2"]  # 创作者ID
            }
        }
        
        task_id = await client.create_task(
            platform="xhs",
            task_type="search",
            keywords=["科技"],
            max_count=30,
            custom_config=custom_config
        )
        print(f"创建自定义配置任务: {task_id}")
        
        # 获取任务状态
        status = await client.get_task_status(task_id)
        print(f"任务状态: {status}")


async def demo_monitoring():
    """监控功能示例"""
    print("\n=== 监控功能示例 ===")
    
    async with MediaCrawlerClient() as client:
        # 获取系统统计信息
        stats = await client.get_system_stats()
        print("系统统计信息:")
        print(json.dumps(stats, indent=2, ensure_ascii=False))
        
        # 创建一个任务用于演示
        task_id = await client.create_task(
            platform="douyin",
            task_type="search",
            keywords=["舞蹈"],
            max_count=10
        )
        print(f"创建监控演示任务: {task_id}")
        
        # 监控任务5次
        for i in range(5):
            await asyncio.sleep(2)
            
            # 获取任务状态
            status = await client.get_task_status(task_id)
            print(f"\n第{i+1}次检查 - 状态: {status['status']}")
            
            if "progress" in status:
                progress = status["progress"]
                print(f"  阶段: {progress['current_stage']}")
                print(f"  进度: {progress['progress_percent']:.1f}%")
                print(f"  完成: {progress['items_completed']}/{progress['items_total']}")
                if progress["estimated_remaining_time"]:
                    print(f"  预计剩余: {progress['estimated_remaining_time']}秒")
            
            # 获取最新事件
            events = await client.get_task_events(task_id, 5)
            if events["events"]:
                print("  最新事件:")
                for event in events["events"][-3:]:  # 显示最后3个事件
                    print(f"    [{event['event_type']}] {event['message']}")
            
            if status["done"]:
                print(f"  任务完成: 成功={status.get('success')}")
                break


async def demo_error_handling():
    """错误处理示例"""
    print("\n=== 错误处理示例 ===")
    
    async with MediaCrawlerClient() as client:
        try:
            # 创建一个错误的任务（不支持的平台）
            task_id = await client.create_task(
                platform="invalid_platform",
                task_type="search",
                keywords=["test"]
            )
        except Exception as e:
            print(f"预期错误: {e}")
        
        try:
            # 查询不存在的任务
            status = await client.get_task_status("non_existent_task")
            print(f"不存在任务的状态: {status}")
        except Exception as e:
            print(f"查询不存在任务错误: {e}")


async def main():
    """主函数"""
    print("MediaCrawler API Client 演示")
    print("=" * 50)
    
    try:
        await demo_basic_usage()
        await demo_custom_config() 
        await demo_monitoring()
        await demo_error_handling()
    except Exception as e:
        print(f"演示过程中出错: {e}")
    
    print("\n演示完成!")


if __name__ == "__main__":
    asyncio.run(main()) 