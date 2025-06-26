import asyncio
import aiohttp
import time

API_BASE = "http://localhost:8000/api/v1"

KEYWORDS = ["塞那耳机", "缕灵"]
PLATFORM = "xhs"

async def create_login_session(session):
    url = f"{API_BASE}/login/create-session"
    payload = {
        "task_id": "test_xhs_login",
        "platform": PLATFORM,
        "login_type": "qrcode",
        "timeout": 300
    }
    async with session.post(url, json=payload) as resp:
        data = await resp.json()
        print("创建登录会话:", data)
        return data

async def start_login_process(session):
    url = f"{API_BASE}/login/start/test_xhs_login"
    async with session.post(url) as resp:
        data = await resp.json()
        print("启动登录流程:", data)
        return data

async def poll_login_status(session):
    url = f"{API_BASE}/login/status/test_xhs_login"
    for _ in range(60):
        async with session.get(url) as resp:
            data = await resp.json()
            print("登录状态:", data)
            if data.get("status") == "success":
                print("登录成功！")
                return True
            elif data.get("status") == "failed":
                print("登录失败！")
                return False
            elif data.get("status") == "qrcode_generated":
                print("二维码已生成，请用小红书App扫码登录")
                if data.get("qrcode_image"):
                    print("二维码已获取（base64编码）")
        await asyncio.sleep(5)
    print("登录超时")
    return False

async def create_crawl_task(session):
    url = f"{API_BASE}/tasks"
    payload = {
        "platform": PLATFORM,
        "task_type": "search",
        "keywords": KEYWORDS,
        "max_count": 10,
        "headless": True,
        "enable_proxy": False
    }
    async with session.post(url, json=payload) as resp:
        data = await resp.json()
        print("创建采集任务:", data)
        return data.get("task_id")

async def poll_task_status(session, task_id):
    url = f"{API_BASE}/tasks/{task_id}/status"
    for _ in range(60):
        async with session.get(url) as resp:
            data = await resp.json()
            print("任务状态:", data)
            if data.get("done"):
                return data
        await asyncio.sleep(5)
    print("任务超时")
    return None

async def get_task_result(session, task_id):
    url = f"{API_BASE}/tasks/{task_id}/result"
    async with session.get(url) as resp:
        data = await resp.json()
        print("采集结果:", data)
        return data

async def main():
    async with aiohttp.ClientSession() as session:
        # 步骤1：创建登录会话
        create_result = await create_login_session(session)
        if not create_result.get("success"):
            print("创建登录会话失败")
            return
        
        # 步骤2：启动登录流程
        start_result = await start_login_process(session)
        if not start_result.get("success"):
            print("启动登录流程失败")
            return
            
        print("登录流程已启动，等待登录完成...")
        
        # 步骤3：轮询登录状态
        login_ok = await poll_login_status(session)
        if not login_ok:
            print("登录失败，测试终止")
            return

        # 步骤4：提交采集任务
        task_id = await create_crawl_task(session)
        if not task_id:
            print("任务创建失败")
            return

        # 步骤5：轮询任务状态
        status = await poll_task_status(session, task_id)
        if not status:
            print("任务执行超时")
            return

        # 步骤6：获取采集结果
        await get_task_result(session, task_id)

if __name__ == "__main__":
    asyncio.run(main())