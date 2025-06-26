#!/usr/bin/env python3
"""
简化测试：单个小红书note详情采集
"""

import requests
import time
import json

# API基础URL
BASE_URL = "http://127.0.0.1:8000"

def test_single_note_detail():
    """测试单个小红书内容详情采集"""
    
    print("🚀 开始测试单个小红书内容详情采集...")
    
    # 使用固定的note_id进行测试
    note_id = "68429435000000002102f671"
    #note_url = f"https://www.xiaohongshu.com/explore/{note_id}/"
    note_url = "https://www.xiaohongshu.com/explore/685397b00000000011000bdf?xsec_token=ABxFTdT-8rJ3b6Ix98WtX0stIrLNvshVK420xZU7t57F4=&xsec_source=pc_feed"
    
    print(f"\n📝 测试内容: {note_id}")
    print(f"📋 URL: {note_url}")
    
    # 1. 创建采集任务
    print("\n1️⃣ 创建采集任务...")
    task_data = {
        "platform": "xhs",
        "task_type": "detail",
        "content_ids": [note_url],  # 单个URL
        "max_count": 1,
        "max_comments": 10,
        "headless": True,
        "save_data_option": "db"
    }
    
    print(f"📤 请求数据: {json.dumps(task_data, ensure_ascii=False, indent=2)}")
    
    try:
        response = requests.post(f"{BASE_URL}/api/v1/tasks", json=task_data)
        print(f"📬 HTTP状态码: {response.status_code}")
        
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
    
    # 2. 监控任务进度（简化版）
    print(f"\n2️⃣ 开始监控任务进度 (任务ID: {task_id})...")
    max_wait_time = 300  # 最大等待5分钟
    start_time = time.time()
    check_count = 0
    
    while time.time() - start_time < max_wait_time:
        check_count += 1
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
                
                print(f"   第{check_count}次检查 - 状态: {task_status} | 阶段: {stage} | 进度: {percent:.1f}%")
                
                # 检查是否完成
                if done:
                    print(f"\n✅ 任务完成！最终状态: {task_status}")
                    success = status.get("success")
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
            
        time.sleep(5)  # 每5秒查询一次
    else:
        print(f"\n⏰ 任务超时 (超过{max_wait_time}秒)")
    
    print("\n🎉 测试完成！")

if __name__ == "__main__":
    test_single_note_detail()
