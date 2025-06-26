import asyncio
import aiohttp
import time

API_BASE = "http://localhost:8000/api/v1"

async def test_xhs_client_login():
    """测试小红书客户端登录模式"""
    async with aiohttp.ClientSession() as session:
        # 1. 创建登录会话
        print("\n=== 步骤1: 创建登录会话 ===")
        payload = {
            "task_id": "test_xhs_client_login",
            "platform": "xhs",
            "login_type": "qrcode",
            "timeout": 300
        }
        async with session.post(f"{API_BASE}/login/create-session", json=payload) as resp:
            data = await resp.json()
            print(f"创建会话结果: {data}")
        
        # 2. 启动登录流程（打开浏览器）
        print("\n=== 步骤2: 启动登录流程 ===")
        async with session.post(f"{API_BASE}/login/start/test_xhs_client_login") as resp:
            data = await resp.json()
            print(f"启动登录结果: {data}")
            
            if data.get("status") == "qrcode_generated":
                print("\n浏览器已打开小红书登录页面")
                print("请在浏览器中完成登录（支持扫码、短信等方式）")
                print("系统将自动检测登录成功状态...")
        
        # 3. 监控登录状态
        print("\n=== 步骤3: 监控登录状态 ===")
        max_wait_time = 300  # 5分钟
        start_time = time.time()
        
        while time.time() - start_time < max_wait_time:
            async with session.get(f"{API_BASE}/login/status/test_xhs_client_login") as resp:
                data = await resp.json()
                status = data.get("status")
                message = data.get("message", "")
                
                print(f"登录状态: {status} - {message}")
                
                if status == "success":
                    print("\n🎉 登录成功！")
                    print("Cookies已自动保存，可以开始数据采集任务")
                    break
                elif status in ["failed", "timeout"]:
                    print(f"\n❌ 登录失败: {message}")
                    break
                
                await asyncio.sleep(3)  # 每3秒检查一次
        else:
            print("\n⏰ 等待登录超时")
        
        # 4. 获取登录cookies（如果成功）
        if status == "success":
            print("\n=== 步骤4: 获取登录cookies ===")
            async with session.get(f"{API_BASE}/login/cookies/test_xhs_client_login") as resp:
                cookies_data = await resp.json()
                print(f"Cookies信息: {cookies_data}")

if __name__ == "__main__":
    print("小红书客户端登录测试")
    print("=" * 50)
    asyncio.run(test_xhs_client_login()) 