#!/usr/bin/env python3
"""
数据访问层测试

测试数据读取器的功能和兼容性。
"""

import pytest
import asyncio
import tempfile
import json
import csv
import os
from typing import Dict, Any, List
from datetime import datetime

from app.dataReader.factory import DataReaderFactory
from app.dataReader.base import DataSourceType, QueryFilter, PlatformType
from app.dataReader.csv_reader import CsvDataReader
from app.dataReader.json_reader import JsonDataReader


async def test_config_validation():
    """测试配置验证"""
    print("🔧 测试配置验证...")
    
    print(f"主数据源: {settings.primary_data_source}")
    print(f"备用数据源: {settings.fallback_data_source}")
    print(f"自动降级: {settings.auto_fallback_enabled}")
    
    # 测试各种数据源配置
    data_sources = ["supabase", "mysql", "csv", "json"]
    for source in data_sources:
        try:
            config = settings.get_data_source_config(source)
            print(f"✅ {source} 配置有效: {list(config.keys())}")
        except Exception as e:
            print(f"❌ {source} 配置错误: {e}")


async def test_csv_data_access():
    """测试CSV数据访问"""
    print("\n📄 测试CSV数据访问...")
    
    # 创建测试数据目录
    csv_path = Path(settings.csv_data_path)
    csv_path.mkdir(parents=True, exist_ok=True)
    
    csv_accessor = CsvDataAccessor(settings.get_data_source_config("csv"))
    
    try:
        # 测试初始化
        await csv_accessor.initialize()
        print("✅ CSV访问器初始化成功")
        
        # 测试健康检查
        health = await csv_accessor.health_check()
        print(f"CSV健康状态: {health}")
        
        # 测试平台列表
        result = await csv_accessor.get_platform_list()
        print(f"平台列表查询: success={result.success}, count={len(result.data or [])}")
        
        # 测试内容查询
        query = DataQuery(
            platform="xhs",
            limit=5
        )
        result = await csv_accessor.query_content(query)
        print(f"内容查询: success={result.success}, count={len(result.data or [])}")
        
    except Exception as e:
        print(f"❌ CSV测试失败: {e}")
    finally:
        await csv_accessor.close()


async def test_json_data_access():
    """测试JSON数据访问"""
    print("\n📋 测试JSON数据访问...")
    
    # 创建测试数据目录
    json_path = Path(settings.json_data_path)
    json_path.mkdir(parents=True, exist_ok=True)
    
    json_accessor = JsonDataAccessor(settings.get_data_source_config("json"))
    
    try:
        # 测试初始化
        await json_accessor.initialize()
        print("✅ JSON访问器初始化成功")
        
        # 测试健康检查
        health = await json_accessor.health_check()
        print(f"JSON健康状态: {health}")
        
        # 测试平台列表
        result = await json_accessor.get_platform_list()
        print(f"平台列表查询: success={result.success}, count={len(result.data or [])}")
        
        # 测试搜索功能
        result = await json_accessor.search_content("测试", platform="douyin")
        print(f"搜索测试: success={result.success}, count={len(result.data or [])}")
        
    except Exception as e:
        print(f"❌ JSON测试失败: {e}")
    finally:
        await json_accessor.close()


async def test_data_access_manager():
    """测试数据访问管理器"""
    print("\n🎯 测试数据访问管理器...")
    
    try:
        # 初始化管理器
        await data_access_manager.initialize()
        print("✅ 数据访问管理器初始化成功")
        
        # 测试主数据源
        primary = await data_access_manager.get_primary_access()
        if primary:
            print(f"✅ 主数据源可用: {type(primary).__name__}")
            
            # 测试主数据源查询
            result = await primary.get_platform_list()
            print(f"主数据源查询: success={result.success}")
        else:
            print("❌ 主数据源不可用")
        
        # 测试降级机制
        fallback = await data_access_manager.get_access_with_fallback()
        if fallback:
            print(f"✅ 降级数据源可用: {type(fallback).__name__}")
            
            # 测试降级数据源查询
            result = await fallback.get_platform_list()
            print(f"降级数据源查询: success={result.success}")
        else:
            print("❌ 降级数据源不可用")
        
        # 测试健康检查
        health = await data_access_manager.health_check()
        print(f"管理器健康状态: {health}")
        
        # 测试统计信息
        stats = await data_access_manager.get_statistics()
        print(f"统计信息: {stats}")
        
    except Exception as e:
        print(f"❌ 管理器测试失败: {e}")


async def test_query_functionality():
    """测试查询功能"""
    print("\n🔍 测试查询功能...")
    
    try:
        accessor = await data_access_manager.get_access_with_fallback()
        if not accessor:
            print("❌ 无可用数据访问器")
            return
        
        # 测试基础查询
        query1 = DataQuery(platform="xhs", limit=10)
        result1 = await accessor.query_content(query1)
        print(f"基础查询: success={result1.success}, count={len(result1.data or [])}")
        
        # 测试带过滤器的查询
        filter_obj = QueryFilter(
            user_id="test_user",
            start_date="2024-01-01",
            end_date="2024-12-31"
        )
        query2 = DataQuery(platform="douyin", limit=5, filters=filter_obj)
        result2 = await accessor.query_content(query2)
        print(f"过滤查询: success={result2.success}, count={len(result2.data or [])}")
        
        # 测试评论查询
        result3 = await accessor.query_comments("test_content_id", platform="xhs")
        print(f"评论查询: success={result3.success}, count={len(result3.data or [])}")
        
        # 测试用户内容查询
        result4 = await accessor.get_user_content("test_user_id", platform="bilibili")
        print(f"用户内容查询: success={result4.success}, count={len(result4.data or [])}")
        
    except Exception as e:
        print(f"❌ 查询功能测试失败: {e}")


async def test_error_handling():
    """测试错误处理"""
    print("\n🚨 测试错误处理...")
    
    try:
        # 测试无效平台
        invalid_query = DataQuery(platform="invalid_platform", limit=10)
        accessor = await data_access_manager.get_access_with_fallback()
        
        if accessor:
            result = await accessor.query_content(invalid_query)
            print(f"无效平台查询: success={result.success}, message='{result.message}'")
        
        # 测试无效配置
        try:
            settings.get_data_source_config("invalid_source")
        except ValueError as e:
            print(f"✅ 无效配置正确抛出异常: {e}")
        
        print("✅ 错误处理测试通过")
        
    except Exception as e:
        print(f"❌ 错误处理测试失败: {e}")


async def create_sample_data():
    """创建示例数据用于测试"""
    print("\n📝 创建示例数据...")
    
    import json
    import csv
    from datetime import datetime
    
    # 示例数据
    sample_xhs_data = [
        {
            "note_id": "test_note_001",
            "title": "测试小红书笔记1",
            "desc": "这是一个测试笔记",
            "user_id": "test_user_001",
            "nickname": "测试用户1",
            "liked_count": "100",
            "collected_count": "50",
            "time": int(datetime.now().timestamp() * 1000)
        },
        {
            "note_id": "test_note_002", 
            "title": "测试小红书笔记2",
            "desc": "这是另一个测试笔记",
            "user_id": "test_user_002",
            "nickname": "测试用户2",
            "liked_count": "200",
            "collected_count": "80",
            "time": int(datetime.now().timestamp() * 1000)
        }
    ]
    
    # 创建CSV示例数据
    csv_path = Path(settings.csv_data_path)
    csv_path.mkdir(parents=True, exist_ok=True)
    
    csv_file = csv_path / "xhs_note.csv"
    with open(csv_file, 'w', newline='', encoding='utf-8') as f:
        if sample_xhs_data:
            writer = csv.DictWriter(f, fieldnames=sample_xhs_data[0].keys())
            writer.writeheader()
            writer.writerows(sample_xhs_data)
    
    print(f"✅ 创建CSV示例数据: {csv_file}")
    
    # 创建JSON示例数据
    json_path = Path(settings.json_data_path)
    json_path.mkdir(parents=True, exist_ok=True)
    
    json_file = json_path / "xhs_note.json"
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(sample_xhs_data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 创建JSON示例数据: {json_file}")


async def main():
    """主函数"""
    print("🚀 数据访问层专项测试开始")
    print("="*50)
    
    # 创建示例数据
    await create_sample_data()
    
    # 配置验证
    await test_config_validation()
    
    # CSV数据访问测试
    await test_csv_data_access()
    
    # JSON数据访问测试
    await test_json_data_access()
    
    # 数据访问管理器测试
    await test_data_access_manager()
    
    # 查询功能测试
    await test_query_functionality()
    
    # 错误处理测试
    await test_error_handling()
    
    print("\n✅ 数据访问层测试完成!")


if __name__ == "__main__":
    asyncio.run(main()) 