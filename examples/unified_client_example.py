"""
MediaCrawler 统一客户端示例

集成爬虫任务和登录功能的完整客户端，支持：
1. 平台登录（二维码/手机验证码）
2. 爬虫任务创建和执行
3. 数据获取和监控
4. 完整的用户交互体验

使用方法：
1. 启动API服务器：python -m app.main
2. 运行客户端：python examples/unified_client_example.py
3. 根据提示选择功能并操作
"""

import asyncio
import aiohttp
import base64
import json
import time
import uuid
from typing import Optional, Dict, List, Any
from pathlib import Path
from datetime import datetime


class MediaCrawlerClient:
    """MediaCrawler 统一客户端"""
    
    def __init__(self, api_base_url: str = "http://localhost:8000"):
        self.api_base_url = api_base_url
        self.login_api_url = f"{api_base_url}/api/v1/login"
        self.task_api_url = f"{api_base_url}/api/v1/tasks"
        self.session: Optional[aiohttp.ClientSession] = None
        
        # 会话状态
        self.logged_in_platforms = set()  # 已登录的平台
        self.current_tasks = {}  # 当前运行的任务
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    # === 系统连接和状态 ===
    
    async def check_api_health(self) -> bool:
        """检查API服务健康状态"""
        try:
            async with self.session.get(f"{self.api_base_url}/") as resp:
                if resp.status == 200:
                    service_info = await resp.json()
                    print(f"✅ API服务已连接: {service_info.get('message', 'Unknown')}")
                    print(f"📋 支持平台: {', '.join(service_info.get('supported_platforms', []))}")
                    return True
                else:
                    print(f"❌ API服务响应异常: {resp.status}")
                    return False
        except Exception as e:
            print(f"❌ 无法连接到API服务: {e}")
            print(f"请确保API服务在 {self.api_base_url} 上运行")
            return False
    
    # === 登录功能 ===
    
    async def login_platform(self, platform: str, login_type: str = "qrcode") -> bool:
        """平台登录"""
        if platform in self.logged_in_platforms:
            print(f"✅ 平台 {platform} 已登录")
            return True
        
        task_id = f"login_{platform}_{int(time.time())}"
        
        try:
            print(f"\n🔐 开始 {platform} 平台登录 ({login_type})...")
            
            # 1. 创建登录会话
            print("1️⃣ 创建登录会话...")
            session_data = {
                "task_id": task_id,
                "platform": platform,
                "login_type": login_type,
                "timeout": 300
            }
            
            async with self.session.post(f"{self.login_api_url}/create-session", json=session_data) as resp:
                if resp.status != 200:
                    error_text = await resp.text()
                    print(f"❌ 创建登录会话失败: {error_text}")
                    return False
                
                result = await resp.json()
                if not result.get('success'):
                    print(f"❌ {result.get('message', '未知错误')}")
                    return False
            
            # 2. 启动登录流程
            print("2️⃣ 启动登录流程...")
            async with self.session.post(f"{self.login_api_url}/start/{task_id}") as resp:
                if resp.status != 200:
                    error_text = await resp.text()
                    print(f"❌ 启动登录流程失败: {error_text}")
                    return False
            
            # 3. 根据登录类型处理
            success = False
            if login_type == "qrcode":
                success = await self._handle_qrcode_login(task_id)
            elif login_type == "phone":
                success = await self._handle_phone_login(task_id)
            
            # 4. 清理登录会话
            try:
                await self.session.delete(f"{self.login_api_url}/session/{task_id}")
            except:
                pass
            
            if success:
                self.logged_in_platforms.add(platform)
                print(f"🎉 {platform} 平台登录成功！")
                return True
            else:
                print(f"❌ {platform} 平台登录失败")
                return False
                
        except Exception as e:
            print(f"❌ 登录过程出错: {e}")
            return False
    
    async def _handle_qrcode_login(self, task_id: str) -> bool:
        """处理二维码登录"""
        print("3️⃣ 等待二维码生成...")
        
        # 等待二维码生成
        for attempt in range(30):
            async with self.session.get(f"{self.login_api_url}/status/{task_id}") as resp:
                if resp.status == 200:
                    status_data = await resp.json()
                    status = status_data.get('status', '')
                    
                    if status == 'qrcode_generated':
                        qrcode_image = status_data.get('qrcode_image')
                        if qrcode_image:
                            # 保存二维码
                            qrcode_path = self._save_qrcode_image(qrcode_image, f"logs/{task_id}_qrcode.png")
                            print(f"📱 二维码已生成并保存到: {qrcode_path}")
                            print("请使用手机App扫描二维码完成登录")
                            break
                    elif status in ['failed', 'timeout']:
                        print(f"❌ 二维码生成失败: {status_data.get('message', '')}")
                        return False
            
            await asyncio.sleep(2)
        else:
            print("❌ 等待二维码生成超时")
            return False
        
        # 等待扫码完成
        print("4️⃣ 等待扫码完成...")
        for attempt in range(60):  # 2分钟
            async with self.session.get(f"{self.login_api_url}/status/{task_id}") as resp:
                if resp.status == 200:
                    status_data = await resp.json()
                    status = status_data.get('status', '')
                    
                    if status == 'qrcode_scanned':
                        print("✅ 二维码已扫描，请在手机上确认登录")
                    elif status == 'success':
                        return True
                    elif status in ['failed', 'timeout']:
                        print(f"❌ 登录失败: {status_data.get('message', '')}")
                        return False
            
            await asyncio.sleep(2)
        
        print("❌ 等待登录确认超时")
        return False
    
    async def _handle_phone_login(self, task_id: str) -> bool:
        """处理手机号登录"""
        print("3️⃣ 等待手机号输入提示...")
        
        # 等待手机号输入提示
        for attempt in range(15):
            async with self.session.get(f"{self.login_api_url}/status/{task_id}") as resp:
                if resp.status == 200:
                    status_data = await resp.json()
                    status = status_data.get('status', '')
                    
                    if status == 'phone_input_required':
                        break
                    elif status in ['failed', 'timeout']:
                        print(f"❌ 登录失败: {status_data.get('message', '')}")
                        return False
            
            await asyncio.sleep(2)
        else:
            print("❌ 等待手机号输入提示超时")
            return False
        
        # 输入手机号
        phone_number = input("📱 请输入手机号: ").strip()
        if not phone_number:
            print("❌ 手机号不能为空")
            return False
        
        input_data = {
            "task_id": task_id,
            "input_type": "phone",
            "value": phone_number
        }
        
        async with self.session.post(f"{self.login_api_url}/input/{task_id}", json=input_data) as resp:
            if resp.status != 200:
                print("❌ 提交手机号失败")
                return False
        
        # 等待验证码输入提示
        print("4️⃣ 等待验证码发送...")
        for attempt in range(15):
            async with self.session.get(f"{self.login_api_url}/status/{task_id}") as resp:
                if resp.status == 200:
                    status_data = await resp.json()
                    status = status_data.get('status', '')
                    
                    if status == 'verification_code_required':
                        break
                    elif status in ['failed', 'timeout']:
                        print(f"❌ 登录失败: {status_data.get('message', '')}")
                        return False
            
            await asyncio.sleep(2)
        else:
            print("❌ 等待验证码发送超时")
            return False
        
        # 输入验证码
        verification_code = input("🔢 请输入验证码: ").strip()
        if not verification_code:
            print("❌ 验证码不能为空")
            return False
        
        input_data = {
            "task_id": task_id,
            "input_type": "verification_code",
            "value": verification_code
        }
        
        async with self.session.post(f"{self.login_api_url}/input/{task_id}", json=input_data) as resp:
            if resp.status != 200:
                print("❌ 提交验证码失败")
                return False
        
        # 等待登录完成
        print("5️⃣ 等待登录完成...")
        for attempt in range(30):
            async with self.session.get(f"{self.login_api_url}/status/{task_id}") as resp:
                if resp.status == 200:
                    status_data = await resp.json()
                    status = status_data.get('status', '')
                    
                    if status == 'success':
                        return True
                    elif status in ['failed', 'timeout']:
                        print(f"❌ 登录失败: {status_data.get('message', '')}")
                        return False
            
            await asyncio.sleep(2)
        
        print("❌ 等待登录完成超时")
        return False
    
    def _save_qrcode_image(self, base64_data: str, filename: str) -> str:
        """保存二维码图片"""
        try:
            image_data = base64.b64decode(base64_data)
            image_path = Path(filename)
            image_path.parent.mkdir(exist_ok=True)
            
            with open(image_path, 'wb') as f:
                f.write(image_data)
            
            return str(image_path.absolute())
        except Exception as e:
            print(f"保存二维码失败: {e}")
            return filename
    
    # === 爬虫任务功能 ===
    
    async def create_crawler_task(self, platform: str, task_type: str, **kwargs) -> Optional[str]:
        """创建爬虫任务"""
        
        # 检查是否需要登录
        if platform not in self.logged_in_platforms:
            print(f"⚠️  平台 {platform} 未登录，需要先登录")
            
            # 询问是否现在登录
            login_now = input("是否现在登录? (y/N): ").strip().lower()
            if login_now in ['y', 'yes']:
                # 选择登录方式
                login_types = ["qrcode", "phone"]
                print(f"登录方式: {', '.join(login_types)}")
                login_type = input("请选择登录方式 (默认: qrcode): ").strip().lower()
                if not login_type or login_type not in login_types:
                    login_type = "qrcode"
                
                login_success = await self.login_platform(platform, login_type)
                if not login_success:
                    print("❌ 登录失败，无法创建爬虫任务")
                    return None
            else:
                print("❌ 需要登录后才能创建爬虫任务")
                return None
        
        # 构建任务数据
        task_data = {
            "platform": platform,
            "task_type": task_type,
            **kwargs
        }
        
        try:
            async with self.session.post(f"{self.task_api_url}", json=task_data) as resp:
                if resp.status == 200:
                    result = await resp.json()
                    task_id = result.get('task_id')
                    if task_id:
                        self.current_tasks[task_id] = {
                            'platform': platform,
                            'task_type': task_type,
                            'created_at': datetime.now(),
                            'status': 'running'
                        }
                        print(f"✅ 爬虫任务已创建: {task_id}")
                        return task_id
                    else:
                        print(f"❌ 任务创建失败: {result}")
                        return None
                else:
                    error_text = await resp.text()
                    print(f"❌ 创建任务失败: {error_text}")
                    return None
        
        except Exception as e:
            print(f"❌ 创建任务过程出错: {e}")
            return None
    
    async def get_task_status(self, task_id: str) -> Optional[Dict]:
        """获取任务状态"""
        try:
            async with self.session.get(f"{self.task_api_url}/{task_id}/status") as resp:
                if resp.status == 200:
                    return await resp.json()
                else:
                    print(f"❌ 获取任务状态失败: {resp.status}")
                    return None
        except Exception as e:
            print(f"❌ 获取任务状态出错: {e}")
            return None
    
    async def monitor_task(self, task_id: str, show_progress: bool = True):
        """监控任务执行"""
        print(f"📊 开始监控任务: {task_id}")
        
        while True:
            status_data = await self.get_task_status(task_id)
            if not status_data:
                break
            
            status = status_data.get('status', 'unknown')
            done = status_data.get('done', False)
            
            if show_progress and 'progress' in status_data:
                progress = status_data['progress']
                stage = progress.get('current_stage', 'unknown')
                percent = progress.get('progress_percent', 0)
                completed = progress.get('items_completed', 0)
                total = progress.get('items_total', 0)
                
                print(f"📈 [{percent:.1f}%] {stage} - 已完成: {completed}/{total}")
            else:
                print(f"📊 任务状态: {status}")
            
            if done:
                success = status_data.get('success', False)
                if success:
                    data_count = status_data.get('data_count', 0)
                    print(f"🎉 任务完成！共爬取 {data_count} 条数据")
                else:
                    message = status_data.get('message', '未知错误')
                    print(f"❌ 任务失败: {message}")
                
                # 更新任务状态
                if task_id in self.current_tasks:
                    self.current_tasks[task_id]['status'] = 'completed' if success else 'failed'
                break
            
            await asyncio.sleep(3)
    
    async def get_task_result(self, task_id: str) -> Optional[Dict]:
        """获取任务结果"""
        try:
            async with self.session.get(f"{self.task_api_url}/{task_id}/result") as resp:
                if resp.status == 200:
                    return await resp.json()
                else:
                    print(f"❌ 获取任务结果失败: {resp.status}")
                    return None
        except Exception as e:
            print(f"❌ 获取任务结果出错: {e}")
            return None
    
    async def stop_task(self, task_id: str) -> bool:
        """停止任务"""
        try:
            async with self.session.delete(f"{self.task_api_url}/{task_id}") as resp:
                if resp.status == 200:
                    result = await resp.json()
                    print(f"✅ 任务已停止: {result.get('message', '')}")
                    
                    # 更新任务状态
                    if task_id in self.current_tasks:
                        self.current_tasks[task_id]['status'] = 'stopped'
                    
                    return True
                else:
                    print(f"❌ 停止任务失败: {resp.status}")
                    return False
        except Exception as e:
            print(f"❌ 停止任务出错: {e}")
            return False
    
    async def list_running_tasks(self) -> List[str]:
        """列出运行中的任务"""
        try:
            async with self.session.get(f"{self.task_api_url}") as resp:
                if resp.status == 200:
                    result = await resp.json()
                    return result.get('running_tasks', [])
                else:
                    return []
        except:
            return []
    
    # === 便捷方法 ===
    
    async def quick_search(self, platform: str, keywords: List[str], max_count: int = 100) -> Optional[str]:
        """快速搜索"""
        return await self.create_crawler_task(
            platform=platform,
            task_type="search",
            keywords=keywords,
            max_count=max_count
        )
    
    async def get_content_details(self, platform: str, content_ids: List[str]) -> Optional[str]:
        """获取内容详情"""
        return await self.create_crawler_task(
            platform=platform,
            task_type="detail",
            content_ids=content_ids
        )
    
    async def crawl_creator(self, platform: str, creator_ids: List[str], max_count: int = 100) -> Optional[str]:
        """爬取创作者内容"""
        return await self.create_crawler_task(
            platform=platform,
            task_type="creator",
            creator_ids=creator_ids,
            max_count=max_count
        )
    
    def show_status(self):
        """显示客户端状态"""
        print("\n" + "="*50)
        print("📊 MediaCrawler 客户端状态")
        print("="*50)
        
        print(f"🔐 已登录平台: {', '.join(self.logged_in_platforms) if self.logged_in_platforms else '无'}")
        print(f"📋 当前任务数: {len(self.current_tasks)}")
        
        if self.current_tasks:
            print("\n📋 任务列表:")
            for task_id, task_info in self.current_tasks.items():
                platform = task_info['platform']
                task_type = task_info['task_type']
                status = task_info['status']
                created_at = task_info['created_at'].strftime('%H:%M:%S')
                print(f"   {task_id[:8]}... | {platform} | {task_type} | {status} | {created_at}")
        
        print("="*50)


# === 交互式菜单 ===

async def show_main_menu():
    """显示主菜单"""
    print("\n" + "="*50)
    print("🤖 MediaCrawler 统一客户端")
    print("="*50)
    print("1. 🔐 平台登录")
    print("2. 🕷️  创建爬虫任务")
    print("3. 📊 任务监控")
    print("4. 📋 任务管理")
    print("5. 💡 快捷操作")
    print("6. 📊 查看状态")
    print("0. 🚪 退出")
    print("="*50)

async def handle_login_menu(client: MediaCrawlerClient):
    """处理登录菜单"""
    platforms = ["xhs", "douyin", "bilibili", "kuaishou", "weibo", "tieba", "zhihu"]
    login_types = ["qrcode", "phone"]
    
    print(f"\n📱 支持的平台: {', '.join(platforms)}")
    platform = input("请选择平台: ").strip().lower()
    
    if platform not in platforms:
        print("❌ 不支持的平台")
        return
    
    print(f"\n🔐 登录方式: {', '.join(login_types)}")
    login_type = input("请选择登录方式 (默认: qrcode): ").strip().lower()
    if not login_type or login_type not in login_types:
        login_type = "qrcode"
    
    await client.login_platform(platform, login_type)

async def handle_task_menu(client: MediaCrawlerClient):
    """处理任务创建菜单"""
    platforms = ["xhs", "douyin", "bilibili", "kuaishou", "weibo", "tieba", "zhihu"]
    task_types = ["search", "detail", "creator"]
    
    print(f"\n📱 支持的平台: {', '.join(platforms)}")
    platform = input("请选择平台: ").strip().lower()
    
    if platform not in platforms:
        print("❌ 不支持的平台")
        return
    
    print(f"\n📋 任务类型: {', '.join(task_types)}")
    task_type = input("请选择任务类型: ").strip().lower()
    
    if task_type not in task_types:
        print("❌ 不支持的任务类型")
        return
    
    # 根据任务类型收集参数
    kwargs = {}
    
    if task_type == "search":
        keywords_str = input("请输入搜索关键词 (用逗号分隔): ").strip()
        if keywords_str:
            kwargs['keywords'] = [k.strip() for k in keywords_str.split(',')]
        else:
            print("❌ 搜索任务需要关键词")
            return
    
    elif task_type == "detail":
        content_ids_str = input("请输入内容ID (用逗号分隔): ").strip()
        if content_ids_str:
            kwargs['content_ids'] = [id.strip() for id in content_ids_str.split(',')]
        else:
            print("❌ 详情任务需要内容ID")
            return
    
    elif task_type == "creator":
        creator_ids_str = input("请输入创作者ID (用逗号分隔): ").strip()
        if creator_ids_str:
            kwargs['creator_ids'] = [id.strip() for id in creator_ids_str.split(',')]
        else:
            print("❌ 创作者任务需要创作者ID")
            return
    
    # 可选参数
    max_count_str = input("最大爬取数量 (默认: 100): ").strip()
    if max_count_str and max_count_str.isdigit():
        kwargs['max_count'] = int(max_count_str)
    
    # 创建任务
    task_id = await client.create_crawler_task(platform, task_type, **kwargs)
    
    if task_id:
        # 询问是否监控任务
        monitor = input("是否监控任务执行? (Y/n): ").strip().lower()
        if monitor != 'n':
            await client.monitor_task(task_id)

async def handle_monitor_menu(client: MediaCrawlerClient):
    """处理任务监控菜单"""
    running_tasks = await client.list_running_tasks()
    
    if not running_tasks:
        print("📋 当前没有运行中的任务")
        return
    
    print(f"\n📋 运行中的任务:")
    for i, task_id in enumerate(running_tasks, 1):
        task_info = client.current_tasks.get(task_id, {})
        platform = task_info.get('platform', 'unknown')
        task_type = task_info.get('task_type', 'unknown')
        print(f"{i}. {task_id[:12]}... | {platform} | {task_type}")
    
    try:
        choice = int(input("请选择要监控的任务 (输入序号): ").strip())
        if 1 <= choice <= len(running_tasks):
            task_id = running_tasks[choice - 1]
            await client.monitor_task(task_id)
        else:
            print("❌ 无效的选择")
    except ValueError:
        print("❌ 请输入有效的数字")

async def handle_management_menu(client: MediaCrawlerClient):
    """处理任务管理菜单"""
    print("\n📋 任务管理:")
    print("1. 📊 查看任务状态")
    print("2. 📄 获取任务结果")
    print("3. 🛑 停止任务")
    print("4. 📋 列出所有任务")
    
    choice = input("请选择操作: ").strip()
    
    if choice == "1":
        task_id = input("请输入任务ID: ").strip()
        if task_id:
            status = await client.get_task_status(task_id)
            if status:
                print(f"📊 任务状态: {json.dumps(status, indent=2, ensure_ascii=False)}")
    
    elif choice == "2":
        task_id = input("请输入任务ID: ").strip()
        if task_id:
            result = await client.get_task_result(task_id)
            if result:
                print(f"📄 任务结果: {json.dumps(result, indent=2, ensure_ascii=False)}")
    
    elif choice == "3":
        task_id = input("请输入任务ID: ").strip()
        if task_id:
            await client.stop_task(task_id)
    
    elif choice == "4":
        running_tasks = await client.list_running_tasks()
        if running_tasks:
            print(f"📋 运行中的任务: {running_tasks}")
        else:
            print("📋 当前没有运行中的任务")

async def handle_quick_menu(client: MediaCrawlerClient):
    """处理快捷操作菜单"""
    print("\n💡 快捷操作:")
    print("1. 🔍 小红书快速搜索")
    print("2. 🎬 抖音快速搜索")
    print("3. 📺 B站快速搜索")
    
    choice = input("请选择操作: ").strip()
    
    if choice in ["1", "2", "3"]:
        platform_map = {"1": "xhs", "2": "douyin", "3": "bilibili"}
        platform = platform_map[choice]
        
        keywords_str = input("请输入搜索关键词 (用逗号分隔): ").strip()
        if not keywords_str:
            print("❌ 关键词不能为空")
            return
        
        keywords = [k.strip() for k in keywords_str.split(',')]
        max_count_str = input("最大爬取数量 (默认: 50): ").strip()
        max_count = int(max_count_str) if max_count_str.isdigit() else 50
        
        task_id = await client.quick_search(platform, keywords, max_count)
        if task_id:
            await client.monitor_task(task_id)

async def main():
    """主函数"""
    print("🚀 启动 MediaCrawler 统一客户端...")
    
    # 确保日志目录存在
    Path("logs").mkdir(exist_ok=True)
    
    try:
        async with MediaCrawlerClient() as client:
            # 检查API服务
            if not await client.check_api_health():
                return
            
            # 主循环
            while True:
                await show_main_menu()
                choice = input("请选择操作: ").strip()
                
                if choice == "0":
                    print("👋 感谢使用 MediaCrawler 客户端！")
                    break
                
                elif choice == "1":
                    await handle_login_menu(client)
                
                elif choice == "2":
                    await handle_task_menu(client)
                
                elif choice == "3":
                    await handle_monitor_menu(client)
                
                elif choice == "4":
                    await handle_management_menu(client)
                
                elif choice == "5":
                    await handle_quick_menu(client)
                
                elif choice == "6":
                    client.show_status()
                
                else:
                    print("❌ 无效的选择，请重新输入")
                
                # 等待用户确认继续
                input("\n按回车键继续...")
    
    except KeyboardInterrupt:
        print("\n\n👋 用户中断程序")
    except Exception as e:
        print(f"\n❌ 程序执行出错: {e}")


if __name__ == "__main__":
    asyncio.run(main()) 