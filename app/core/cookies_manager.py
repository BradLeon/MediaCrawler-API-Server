"""
简单的Cookies管理器
负责保存、加载和清理本地cookies缓存
"""

import json
import os
import time
from pathlib import Path
from typing import Optional, Dict
import logging

logger = logging.getLogger(__name__)


class CookiesManager:
    """Cookies缓存管理器"""
    
    def __init__(self, cache_dir: str = "logs/cookies"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
    def get_cookies_file_path(self, platform: str) -> Path:
        """获取指定平台的cookies文件路径"""
        return self.cache_dir / f"{platform}_cookies.json"
        
    def save_cookies(self, platform: str, cookies: str, task_id: Optional[str] = None) -> bool:
        """保存cookies到本地文件"""
        try:
            cookies_file = self.get_cookies_file_path(platform)
            
            cookies_data = {
                "platform": platform,
                "cookies": cookies,
                "task_id": task_id,
                "saved_time": int(time.time()),
                "saved_date": time.strftime("%Y-%m-%d %H:%M:%S")
            }
            
            with open(cookies_file, 'w', encoding='utf-8') as f:
                json.dump(cookies_data, f, ensure_ascii=False, indent=2)
                
            logger.info(f"✅ Cookies已保存: {platform} -> {cookies_file}")
            return True
            
        except Exception as e:
            logger.error(f"❌ 保存cookies失败 [{platform}]: {e}")
            return False
    
    def load_cookies(self, platform: str, max_age_days: int = 7) -> Optional[str]:
        """加载本地cookies（如果未过期）"""
        try:
            cookies_file = self.get_cookies_file_path(platform)
            
            if not cookies_file.exists():
                logger.info(f"📄 Cookies文件不存在: {platform}")
                return None
                
            with open(cookies_file, 'r', encoding='utf-8') as f:
                cookies_data = json.load(f)
            
            # 检查cookies是否过期
            saved_time = cookies_data.get("saved_time", 0)
            current_time = int(time.time())
            age_days = (current_time - saved_time) / (24 * 3600)
            
            if age_days > max_age_days:
                logger.info(f"⏰ Cookies已过期 [{platform}]: {age_days:.1f}天 > {max_age_days}天")
                return None
            
            cookies = cookies_data.get("cookies")
            if cookies:
                logger.info(f"✅ 加载到有效cookies [{platform}]: 保存于{cookies_data.get('saved_date')}")
                return cookies
            else:
                logger.warning(f"⚠️  Cookies数据为空 [{platform}]")
                return None
                
        except Exception as e:
            logger.error(f"❌ 加载cookies失败 [{platform}]: {e}")
            return None
    
    def clear_cookies(self, platform: Optional[str] = None) -> bool:
        """清除cookies缓存"""
        try:
            if platform:
                # 清除指定平台的cookies
                cookies_file = self.get_cookies_file_path(platform)
                if cookies_file.exists():
                    cookies_file.unlink()
                    logger.info(f"🗑️  已清除cookies: {platform}")
                else:
                    logger.info(f"📄 Cookies文件不存在: {platform}")
            else:
                # 清除所有cookies
                cleared_count = 0
                for cookies_file in self.cache_dir.glob("*_cookies.json"):
                    cookies_file.unlink()
                    cleared_count += 1
                logger.info(f"🗑️  已清除所有cookies: {cleared_count}个文件")
                
            return True
            
        except Exception as e:
            logger.error(f"❌ 清除cookies失败 [{platform or 'all'}]: {e}")
            return False
    
    def list_cached_cookies(self) -> Dict[str, Dict]:
        """列出所有缓存的cookies信息"""
        cookies_info = {}
        
        try:
            for cookies_file in self.cache_dir.glob("*_cookies.json"):
                platform = cookies_file.stem.replace("_cookies", "")
                
                try:
                    with open(cookies_file, 'r', encoding='utf-8') as f:
                        cookies_data = json.load(f)
                    
                    # 计算年龄
                    saved_time = cookies_data.get("saved_time", 0)
                    current_time = int(time.time())
                    age_days = (current_time - saved_time) / (24 * 3600)
                    
                    cookies_info[platform] = {
                        "saved_date": cookies_data.get("saved_date"),
                        "age_days": round(age_days, 1),
                        "task_id": cookies_data.get("task_id"),
                        "has_cookies": bool(cookies_data.get("cookies")),
                        "file_path": str(cookies_file)
                    }
                    
                except Exception as e:
                    logger.error(f"❌ 读取cookies信息失败 [{platform}]: {e}")
                    
        except Exception as e:
            logger.error(f"❌ 列出cookies失败: {e}")
            
        return cookies_info
    
    def get_cookies_status(self, platform: str, max_age_days: int = 7) -> Dict:
        """获取指定平台的cookies状态"""
        cookies_file = self.get_cookies_file_path(platform)
        
        status = {
            "platform": platform,
            "has_cache": False,
            "is_valid": False,
            "age_days": 0,
            "saved_date": None,
            "file_path": str(cookies_file)
        }
        
        if not cookies_file.exists():
            return status
            
        try:
            with open(cookies_file, 'r', encoding='utf-8') as f:
                cookies_data = json.load(f)
            
            status["has_cache"] = True
            status["saved_date"] = cookies_data.get("saved_date")
            
            # 检查是否过期
            saved_time = cookies_data.get("saved_time", 0)
            current_time = int(time.time())
            age_days = (current_time - saved_time) / (24 * 3600)
            status["age_days"] = round(age_days, 1)
            
            # cookies有效且未过期
            if cookies_data.get("cookies") and age_days <= max_age_days:
                status["is_valid"] = True
                
        except Exception as e:
            logger.error(f"❌ 获取cookies状态失败 [{platform}]: {e}")
            
        return status


# 全局cookies管理器实例
cookies_manager = CookiesManager() 