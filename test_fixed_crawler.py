#!/usr/bin/env python3
"""
测试修复后的小红书内容采集功能
"""

import requests
import time
import json

# API基础URL
BASE_URL = "http://127.0.0.1:8000"

def test_note_detail_crawler():
    """测试小红书内容详情采集"""
    
    print("🚀 开始测试小红书内容详情采集...")
    
    # 提示用户输入note_id或完整URL
    print("\n请输入小红书内容信息：")
    print("1. 可以输入note_id（如：67e6c0c30000000009016264）")
    print("2. 也可以输入完整URL（如：https://www.xiaohongshu.com/explore/67e6c0c30000000009016264）")
    
    user_input = input("\n请输入内容ID或URL: ").strip()
    
    if not user_input:
        print("❌ 输入不能为空")
        return
    
    # 判断输入类型并处理
    if "," in user_input:
        # 多个URL，用逗号分隔
        content_urls = [url.strip() for url in user_input.split(",") if url.strip()]
        print(f"\n📝 检测到 {len(content_urls)} 个URL:")
        for i, url in enumerate(content_urls, 1):
            if "/explore/" in url:
                note_id = url.split("/explore/")[-1].split("?")[0]
                print(f"   {i}. {note_id} -> {url[:80]}...")
            else:
                print(f"   {i}. {url[:80]}...")
    elif user_input.startswith("https://"):
        # 单个完整URL
        content_urls = [user_input]
        note_id = user_input.split("/explore/")[-1].split("?")[0] if "/explore/" in user_input else "unknown"
        print(f"\n📝 将要采集的内容: {note_id}")
        print(f"📋 URL: {content_urls[0]}")
    else:
        # note_id，构造基础URL
        note_id = user_input
        content_urls = [f"https://www.xiaohongshu.com/explore/{note_id}"]
        print(f"\n📝 将要采集的内容: {note_id}")
        print(f"📋 URL: {content_urls[0]}")
    
    print(f"\n📊 总计将采集 {len(content_urls)} 个内容")
    
    # 1. 创建采集任务
    print("\n1️⃣ 创建采集任务...")
    task_data = {
        "platform": "xhs",
        "task_type": "detail",
        "content_ids": content_urls,  # 使用完整URL
        "max_count": 1,
        "max_comments": 10,
        "headless": True,
        "save_data_option": "db"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/v1/tasks", json=task_data)
        if response.status_code == 200:
            result = response.json()
            task_id = result.get("task_id")
            print(f"✅ 任务创建成功: {task_id}")
            print(f"📄 服务器响应: {result.get('message', '')}")
        else:
            print(f"❌ 任务创建失败: {response.status_code}")
            print(f"📄 错误信息: {response.text}")
            return
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        return
    
    # 2. 监控任务进度
    print(f"\n2️⃣ 开始监控任务进度 (任务ID: {task_id})...")
    max_wait_time = 300  # 最大等待5分钟
    start_time = time.time()
    last_stage = ""
    
    while time.time() - start_time < max_wait_time:
        try:
            response = requests.get(f"{BASE_URL}/api/v1/tasks/{task_id}/status")
            if response.status_code == 200:
                status = response.json()
                
                # 提取状态信息
                task_status = status.get("status", "unknown")
                done = status.get("done", False)
                progress_info = status.get("progress", {})
                
                # 显示进度信息
                stage = progress_info.get("current_stage", "未知")
                percent = progress_info.get("progress_percent", 0.0)
                items_completed = progress_info.get("items_completed", 0)
                items_total = progress_info.get("items_total", 0)
                
                # 只在状态改变时打印，避免输出太多
                if stage != last_stage or percent % 10 == 0:
                    progress_text = f"   状态: {task_status} | 阶段: {stage} | 进度: {percent:.1f}%"
                    if items_total > 0:
                        progress_text += f" | 项目: {items_completed}/{items_total}"
                    print(progress_text)
                    last_stage = stage
                
                # 检查是否完成
                if done:
                    print(f"\n✅ 任务完成！最终状态: {task_status}")
                    success = status.get("success", False)
                    message = status.get("message", "")
                    data_count = status.get("data_count", 0)
                    
                    print(f"📊 执行结果: {'成功' if success else '失败'}")
                    if message:
                        print(f"📝 消息: {message}")
                    print(f"📈 数据条数: {data_count}")
                    break
                    
            else:
                print(f"⚠️  状态查询失败: {response.status_code}")
                break
                
        except Exception as e:
            print(f"⚠️  查询异常: {e}")
            
        time.sleep(3)  # 每3秒查询一次
    else:
        print(f"\n⏰ 任务超时 (超过{max_wait_time}秒)")
    
    # 3. 获取任务结果
    print(f"\n3️⃣ 获取任务结果...")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/tasks/{task_id}/result")
        if response.status_code == 200:
            result = response.json()
            print(f"📋 任务结果:")
            print(f"   - 成功: {result.get('success', False)}")
            print(f"   - 消息: {result.get('message', '')}")
            print(f"   - 数据条数: {result.get('data_count', 0)}")
            print(f"   - 错误条数: {result.get('error_count', 0)}")
            
            # 显示部分数据
            data = result.get("data", [])
            if data:
                print(f"\n📊 采集到的数据 (前1条):")
                for i, item in enumerate(data[:1]):
                    print(f"   数据 {i+1}:")
                    print(f"     - 标题: {item.get('title', 'N/A')}")
                    print(f"     - 作者: {item.get('author', 'N/A')}")
                    print(f"     - 点赞数: {item.get('liked_count', 'N/A')}")
                    print(f"     - 评论数: {item.get('comments_count', 'N/A')}")
            else:
                print("📊 未获取到具体数据")
        else:
            print(f"❌ 获取结果失败: {response.status_code}")
            print(f"📄 错误信息: {response.text}")
    except Exception as e:
        print(f"❌ 获取结果异常: {e}")
    
    # 4. 查询数据库中的数据
    print(f"\n4️⃣ 查询数据库中的数据...")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/data/xhs/notes", params={"limit": 5})
        if response.status_code == 200:
            db_data = response.json()
            print(f"📊 数据库中的小红书笔记数据:")
            
            notes = db_data.get("data", [])
            if notes:
                print(f"   找到 {len(notes)} 条笔记数据:")
                for note in notes:
                    print(f"     - ID: {note.get('note_id', 'N/A')}")
                    print(f"     - 标题: {note.get('title', 'N/A')[:50]}...")
                    print(f"     - 作者: {note.get('author', 'N/A')}")
                    print(f"     - 发布时间: {note.get('publish_time', 'N/A')}")
                    print("     ---")
            else:
                print("   数据库中暂无数据")
        else:
            print(f"❌ 查询数据库失败: {response.status_code}")
            print(f"📄 错误信息: {response.text}")
    except Exception as e:
        print(f"❌ 查询数据库异常: {e}")
    
    print("\n🎉 测试完成！")

if __name__ == "__main__":
    test_note_detail_crawler() 