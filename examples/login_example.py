"""
登录交互客户端示例

演示如何使用MediaCrawler API服务的登录功能：
1. 二维码登录流程
2. 手机号+验证码登录流程
3. 实时状态监控

使用方法：
1. 启动API服务器
2. 运行此示例脚本
3. 根据提示选择登录方式
4. 按指示完成登录
"""

import asyncio
import aiohttp
import base64
import json
import time
from typing import Optional
from pathlib import Path
import sys

# API服务器配置
API_BASE_URL = "http://localhost:8000"
LOGIN_API_URL = f"{API_BASE_URL}/api/v1/login"


class LoginClient:
    """登录客户端"""
    
    def __init__(self, api_base_url: str = API_BASE_URL):
        self.api_base_url = api_base_url
        self.login_api_url = f"{api_base_url}/api/v1/login"
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def create_login_session(self, task_id: str, platform: str, login_type: str) -> dict:
        """创建登录会话"""
        data = {
            "task_id": task_id,
            "platform": platform,
            "login_type": login_type,
            "timeout": 300
        }
        
        async with self.session.post(f"{self.login_api_url}/create-session", json=data) as resp:
            if resp.status != 200:
                error_text = await resp.text()
                raise Exception(f"创建登录会话失败: {error_text}")
            
            return await resp.json()
    
    async def start_login_process(self, task_id: str) -> dict:
        """启动登录流程"""
        async with self.session.post(f"{self.login_api_url}/start/{task_id}") as resp:
            if resp.status != 200:
                error_text = await resp.text()
                raise Exception(f"启动登录流程失败: {error_text}")
            
            return await resp.json()
    
    async def get_login_status(self, task_id: str) -> dict:
        """获取登录状态"""
        async with self.session.get(f"{self.login_api_url}/status/{task_id}") as resp:
            if resp.status != 200:
                error_text = await resp.text()
                raise Exception(f"获取登录状态失败: {error_text}")
            
            return await resp.json()
    
    async def submit_login_input(self, task_id: str, input_type: str, value: str) -> dict:
        """提交登录输入"""
        data = {
            "task_id": task_id,
            "input_type": input_type,
            "value": value
        }
        
        async with self.session.post(f"{self.login_api_url}/input/{task_id}", json=data) as resp:
            if resp.status != 200:
                error_text = await resp.text()
                raise Exception(f"提交登录输入失败: {error_text}")
            
            return await resp.json()
    
    async def delete_login_session(self, task_id: str) -> dict:
        """删除登录会话"""
        async with self.session.delete(f"{self.login_api_url}/session/{task_id}") as resp:
            if resp.status != 200:
                error_text = await resp.text()
                raise Exception(f"删除登录会话失败: {error_text}")
            
            return await resp.json()


def save_qrcode_image(base64_data: str, filename: str):
    """保存二维码图片"""
    try:
        image_data = base64.b64decode(base64_data)
        image_path = Path(filename)
        image_path.parent.mkdir(exist_ok=True)
        
        with open(image_path, 'wb') as f:
            f.write(image_data)
        
        print(f"二维码已保存到: {image_path.absolute()}")
        return str(image_path.absolute())
    except Exception as e:
        print(f"保存二维码失败: {e}")
        return None


async def qrcode_login_demo(client: LoginClient, task_id: str, platform: str):
    """二维码登录演示"""
    print(f"\n=== 二维码登录演示 ===")
    print(f"任务ID: {task_id}")
    print(f"平台: {platform}")
    
    try:
        # 1. 创建登录会话
        print("\n1. 创建登录会话...")
        session_resp = await client.create_login_session(task_id, platform, "qrcode")
        print(f"会话创建结果: {session_resp}")
        
        # 2. 启动登录流程
        print("\n2. 启动登录流程...")
        start_resp = await client.start_login_process(task_id)
        print(f"启动结果: {start_resp}")
        
        # 3. 轮询获取二维码
        print("\n3. 等待二维码生成...")
        qrcode_received = False
        attempts = 0
        max_attempts = 30
        
        while not qrcode_received and attempts < max_attempts:
            status_resp = await client.get_login_status(task_id)
            status = status_resp.get('status', '')
            
            print(f"当前状态: {status} - {status_resp.get('message', '')}")
            
            if status == 'qrcode_generated':
                qrcode_image = status_resp.get('qrcode_image')
                if qrcode_image:
                    print("\n✅ 二维码已生成！")
                    
                    # 保存二维码图片
                    qrcode_path = save_qrcode_image(qrcode_image, f"logs/{task_id}_qrcode.png")
                    if qrcode_path:
                        print(f"请打开图片文件查看二维码: {qrcode_path}")
                        print("请使用手机App扫描二维码完成登录")
                    
                    qrcode_received = True
                    break
            elif status in ['failed', 'timeout']:
                print(f"❌ 登录失败: {status_resp.get('message', '')}")
                return False
            
            attempts += 1
            await asyncio.sleep(2)
        
        if not qrcode_received:
            print("❌ 等待二维码超时")
            return False
        
        # 4. 等待扫码完成
        print("\n4. 等待扫码完成...")
        login_completed = False
        scan_attempts = 0
        max_scan_attempts = 60  # 2分钟
        
        while not login_completed and scan_attempts < max_scan_attempts:
            status_resp = await client.get_login_status(task_id)
            status = status_resp.get('status', '')
            
            print(f"扫码状态: {status} - {status_resp.get('message', '')}")
            
            if status == 'qrcode_scanned':
                print("✅ 二维码已扫描，请在手机上确认登录")
            elif status == 'success':
                print("🎉 登录成功！")
                login_completed = True
                break
            elif status in ['failed', 'timeout']:
                print(f"❌ 登录失败: {status_resp.get('message', '')}")
                return False
            
            scan_attempts += 1
            await asyncio.sleep(2)
        
        if not login_completed:
            print("❌ 等待登录确认超时")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ 二维码登录过程出错: {e}")
        return False


async def phone_login_demo(client: LoginClient, task_id: str, platform: str):
    """手机号+验证码登录演示"""
    print(f"\n=== 手机号登录演示 ===")
    print(f"任务ID: {task_id}")
    print(f"平台: {platform}")
    
    try:
        # 1. 创建登录会话
        print("\n1. 创建登录会话...")
        session_resp = await client.create_login_session(task_id, platform, "phone")
        print(f"会话创建结果: {session_resp}")
        
        # 2. 启动登录流程
        print("\n2. 启动登录流程...")
        start_resp = await client.start_login_process(task_id)
        print(f"启动结果: {start_resp}")
        
        # 3. 等待输入手机号提示
        print("\n3. 等待手机号输入提示...")
        phone_prompt_received = False
        attempts = 0
        max_attempts = 15
        
        while not phone_prompt_received and attempts < max_attempts:
            status_resp = await client.get_login_status(task_id)
            status = status_resp.get('status', '')
            
            print(f"当前状态: {status} - {status_resp.get('message', '')}")
            
            if status == 'phone_input_required':
                input_required = status_resp.get('input_required', {})
                print(f"\n✅ 请输入{input_required.get('placeholder', '手机号')}")
                phone_prompt_received = True
                break
            elif status in ['failed', 'timeout']:
                print(f"❌ 登录失败: {status_resp.get('message', '')}")
                return False
            
            attempts += 1
            await asyncio.sleep(2)
        
        if not phone_prompt_received:
            print("❌ 等待手机号输入提示超时")
            return False
        
        # 4. 输入手机号
        phone_number = input("\n请输入手机号: ").strip()
        if not phone_number:
            print("❌ 手机号不能为空")
            return False
        
        print(f"提交手机号: {phone_number}")
        phone_resp = await client.submit_login_input(task_id, "phone", phone_number)
        print(f"手机号提交结果: {phone_resp}")
        
        # 5. 等待验证码提示
        print("\n5. 等待验证码提示...")
        code_prompt_received = False
        attempts = 0
        max_attempts = 15
        
        while not code_prompt_received and attempts < max_attempts:
            status_resp = await client.get_login_status(task_id)
            status = status_resp.get('status', '')
            
            print(f"当前状态: {status} - {status_resp.get('message', '')}")
            
            if status == 'verification_code_required':
                input_required = status_resp.get('input_required', {})
                print(f"\n✅ 请输入{input_required.get('placeholder', '验证码')}")
                code_prompt_received = True
                break
            elif status in ['failed', 'timeout']:
                print(f"❌ 登录失败: {status_resp.get('message', '')}")
                return False
            
            attempts += 1
            await asyncio.sleep(2)
        
        if not code_prompt_received:
            print("❌ 等待验证码输入提示超时")
            return False
        
        # 6. 输入验证码
        verification_code = input("\n请输入验证码: ").strip()
        if not verification_code:
            print("❌ 验证码不能为空")
            return False
        
        print(f"提交验证码: {verification_code}")
        code_resp = await client.submit_login_input(task_id, "verification_code", verification_code)
        print(f"验证码提交结果: {code_resp}")
        
        # 7. 等待登录完成
        print("\n7. 等待登录完成...")
        login_completed = False
        attempts = 0
        max_attempts = 30
        
        while not login_completed and attempts < max_attempts:
            status_resp = await client.get_login_status(task_id)
            status = status_resp.get('status', '')
            
            print(f"登录状态: {status} - {status_resp.get('message', '')}")
            
            if status == 'success':
                print("🎉 登录成功！")
                login_completed = True
                break
            elif status in ['failed', 'timeout']:
                print(f"❌ 登录失败: {status_resp.get('message', '')}")
                return False
            
            attempts += 1
            await asyncio.sleep(2)
        
        if not login_completed:
            print("❌ 等待登录完成超时")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ 手机号登录过程出错: {e}")
        return False


async def main():
    """主函数"""
    print("MediaCrawler 登录交互演示")
    print("=" * 50)
    
    # 选择平台
    platforms = ["xhs", "douyin", "bilibili", "kuaishou", "weibo", "tieba", "zhihu"]
    print(f"支持的平台: {', '.join(platforms)}")
    platform = input("请选择平台 (默认: xhs): ").strip().lower()
    if not platform:
        platform = "xhs"
    
    if platform not in platforms:
        print(f"❌ 不支持的平台: {platform}")
        return
    
    # 选择登录方式
    login_types = ["qrcode", "phone"]
    print(f"支持的登录方式: {', '.join(login_types)}")
    login_type = input("请选择登录方式 (qrcode/phone, 默认: qrcode): ").strip().lower()
    if not login_type:
        login_type = "qrcode"
    
    if login_type not in login_types:
        print(f"❌ 不支持的登录方式: {login_type}")
        return
    
    # 生成任务ID
    task_id = f"login_demo_{platform}_{int(time.time())}"
    
    try:
        async with LoginClient() as client:
            # 检查API服务是否可用
            try:
                async with client.session.get(f"{API_BASE_URL}/") as resp:
                    if resp.status != 200:
                        print(f"❌ API服务不可用，请检查服务是否启动: {API_BASE_URL}")
                        return
                    service_info = await resp.json()
                    print(f"✅ API服务已连接: {service_info.get('message', 'Unknown')}")
            except Exception as e:
                print(f"❌ 无法连接到API服务: {e}")
                print(f"请确保API服务在 {API_BASE_URL} 上运行")
                return
            
            # 执行登录流程
            success = False
            if login_type == "qrcode":
                success = await qrcode_login_demo(client, task_id, platform)
            elif login_type == "phone":
                success = await phone_login_demo(client, task_id, platform)
            
            # 清理登录会话
            try:
                print(f"\n清理登录会话 {task_id}...")
                cleanup_resp = await client.delete_login_session(task_id)
                print(f"清理结果: {cleanup_resp}")
            except Exception as e:
                print(f"清理会话失败: {e}")
            
            if success:
                print(f"\n🎉 {platform} 平台登录演示完成！")
                print("现在可以使用该平台进行数据爬取任务了")
            else:
                print(f"\n❌ {platform} 平台登录演示失败")
    
    except KeyboardInterrupt:
        print("\n\n用户中断程序")
    except Exception as e:
        print(f"\n❌ 程序执行出错: {e}")


if __name__ == "__main__":
    # 确保日志目录存在
    Path("logs").mkdir(exist_ok=True)
    
    # 运行演示
    asyncio.run(main()) 