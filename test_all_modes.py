#!/usr/bin/env python3
"""
测试所有爬取模式的命令行参数传递功能
包括：search、detail、creator三种模式
"""

import requests
import time
import json

# API基础URL
BASE_URL = "http://127.0.0.1:8000"

def test_search_mode():
    """测试搜索模式"""
    print("🔍 测试搜索模式...")
    
    task_data = {
        "platform": "xhs",
        "task_type": "search",
        "keywords": ["护肤", "美妆"],
        "max_count": 5,
        "max_comments": 10,
        "headless": True,
        "save_data_option": "db"
    }
    
    print(f"📤 搜索请求: {json.dumps(task_data, ensure_ascii=False, indent=2)}")
    
    try:
        response = requests.post(f"{BASE_URL}/api/v1/tasks", json=task_data)
        if response.status_code == 200:
            result = response.json()
            task_id = result.get("task_id")
            print(f"✅ 搜索任务创建成功: {task_id}")
            return task_id
        else:
            print(f"❌ 搜索任务创建失败: {response.status_code}")
            print(f"📄 错误信息: {response.text}")
            return None
    except Exception as e:
        print(f"❌ 搜索请求失败: {e}")
        return None

def test_detail_mode():
    """测试详情模式"""
    print("\n📋 测试详情模式...")
    
    # 使用单个小红书笔记URL测试
    note_url = "https://www.xiaohongshu.com/explore/683a4230000000002100ee92?xsec_token=AB8AXJiSMVTsbKWfkYat5O7htmY9B8azBnBaieK48jYv0=&xsec_source=pc_feed"
    
    task_data = {
        "platform": "xhs",
        "task_type": "detail",
        "content_ids": [note_url],
        "max_count": 1,
        "max_comments": 5,
        "headless": True,
        "save_data_option": "db"
    }
    
    print(f"📤 详情请求: {json.dumps(task_data, ensure_ascii=False, indent=2)}")
    
    try:
        response = requests.post(f"{BASE_URL}/api/v1/tasks", json=task_data)
        if response.status_code == 200:
            result = response.json()
            task_id = result.get("task_id")
            print(f"✅ 详情任务创建成功: {task_id}")
            return task_id
        else:
            print(f"❌ 详情任务创建失败: {response.status_code}")
            print(f"📄 错误信息: {response.text}")
            return None
    except Exception as e:
        print(f"❌ 详情请求失败: {e}")
        return None

def test_creator_mode():
    """测试创作者模式"""
    print("\n👤 测试创作者模式...")
    
    # 使用小红书创作者ID测试
    creator_id = "595989005e87e7786f165159"  # 花西子官方账号
    
    task_data = {
        "platform": "xhs",
        "task_type": "creator",
        "creator_ids": [creator_id],
        "max_count": 5,
        "max_comments": 10,
        "headless": True,
        "save_data_option": "db"
    }
    
    print(f"📤 创作者请求: {json.dumps(task_data, ensure_ascii=False, indent=2)}")
    
    try:
        response = requests.post(f"{BASE_URL}/api/v1/tasks", json=task_data)
        if response.status_code == 200:
            result = response.json()
            task_id = result.get("task_id")
            print(f"✅ 创作者任务创建成功: {task_id}")
            return task_id
        else:
            print(f"❌ 创作者任务创建失败: {response.status_code}")
            print(f"📄 错误信息: {response.text}")
            return None
    except Exception as e:
        print(f"❌ 创作者请求失败: {e}")
        return None

def monitor_task(task_id, task_name):
    """监控任务进度"""
    if not task_id:
        return
        
    print(f"\n⏱️  监控{task_name}任务进度 (任务ID: {task_id})...")
    max_wait_time = 120  # 1分钟超时
    start_time = time.time()
    last_stage = ""
    
    while time.time() - start_time < max_wait_time:
        try:
            response = requests.get(f"{BASE_URL}/api/v1/tasks/{task_id}/status")
            if response.status_code == 200:
                status = response.json()
                
                task_status = status.get("status", "unknown")
                done = status.get("done", False)
                progress_info = status.get("progress", {})
                
                stage = progress_info.get("current_stage", "未知")
                percent = progress_info.get("progress_percent", 0.0)
                
                if stage != last_stage:
                    print(f"   {task_name}: {task_status} | {stage} | {percent:.1f}%")
                    last_stage = stage
                
                if done:
                    success = status.get("success", False)
                    message = status.get("message", "")
                    data_count = status.get("data_count", 0)
                    
                    print(f"✅ {task_name}任务完成！")
                    print(f"   结果: {'成功' if success else '失败'}")
                    print(f"   消息: {message}")
                    print(f"   数据条数: {data_count}")
                    break
                    
            else:
                print(f"⚠️  {task_name}状态查询失败: {response.status_code}")
                break
                
        except Exception as e:
            print(f"⚠️  {task_name}查询异常: {e}")
            
        time.sleep(5)  # 每5秒查询一次
    else:
        print(f"⏰ {task_name}任务超时")

def main():
    """主测试函数"""
    print("🚀 开始测试所有爬取模式的命令行参数传递功能")
    print("=" * 60)
    
    # 选择测试模式
    print("\n请选择要测试的模式：")
    print("1. 搜索模式 (search)")
    print("2. 详情模式 (detail)")
    print("3. 创作者模式 (creator)")
    print("4. 全部测试")
    
    choice = input("\n请输入选择 (1-4): ").strip()
    
    task_ids = []
    
    if choice == "1":
        task_id = test_search_mode()
        if task_id:
            task_ids.append((task_id, "搜索"))
    elif choice == "2":
        task_id = test_detail_mode()
        if task_id:
            task_ids.append((task_id, "详情"))
    elif choice == "3":
        task_id = test_creator_mode()
        if task_id:
            task_ids.append((task_id, "创作者"))
    elif choice == "4":
        # 测试所有模式
        search_id = test_search_mode()
        detail_id = test_detail_mode()
        creator_id = test_creator_mode()
        
        if search_id:
            task_ids.append((search_id, "搜索"))
        if detail_id:
            task_ids.append((detail_id, "详情"))
        if creator_id:
            task_ids.append((creator_id, "创作者"))
    else:
        print("❌ 无效选择")
        return
    
    # 监控所有任务
    for task_id, task_name in task_ids:
        monitor_task(task_id, task_name)
    
    print("\n🎉 测试完成！")

if __name__ == "__main__":
    main() 