"""
MediaCrawler 适配器

通过适配器模式复用原MediaCrawler项目的成熟爬虫功能，
为FastAPI服务提供统一的爬虫接口。
"""

import asyncio
import sys
import os
import subprocess
import tempfile
import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
import logging
from pathlib import Path

from app.dataReader.base import PlatformType
from app.core.logging import logging_manager, TaskEventType, get_app_logger
from app.core.config_manager import get_config_manager, CrawlerConfigRequest, CrawlerConfig
from app.core.login_manager import login_manager, LoginType, LoginStatus
from app.core.config import get_settings
from app.core.cookies_manager import cookies_manager


logger = get_app_logger(__name__)

# 原MediaCrawler项目路径
MEDIACRAWLER_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "MediaCrawler")


class CrawlerTaskType(Enum):
    """爬虫任务类型"""
    SEARCH = "search"
    DETAIL = "detail" 
    CREATOR = "creator"


@dataclass
class CrawlerTask:
    """爬虫任务"""
    task_id: str
    platform: PlatformType
    task_type: CrawlerTaskType
    keywords: Optional[List[str]] = None
    content_ids: Optional[List[str]] = None
    xhs_note_urls: Optional[List[str]] = None
    creator_ids: Optional[List[str]] = None
    max_count: int = 100
    max_comments: int = 50
    start_page: int = 1
    enable_proxy: bool = False
    headless: bool = False  # 修改默认值为False，显示浏览器窗口
    enable_comments: bool = True
    enable_sub_comments: bool = False
    save_data_option: str = "db"  # db, json, csv
    config: Optional[CrawlerConfigRequest] = None  # 自定义配置
    clear_cookies: bool = False  # 是否清除cookies重新登录


@dataclass 
class CrawlerResult:
    """爬虫结果"""
    task_id: str
    success: bool
    message: str
    data_count: int = 0
    error_count: int = 0
    data: Optional[List[Dict]] = None
    errors: Optional[List[str]] = None


class MediaCrawlerAdapter:
    """MediaCrawler 适配器 - 通过进程调用复用原项目功能"""
    
    def __init__(self):
        self.running_tasks: Dict[str, Dict[str, Any]] = {}  # 任务状态信息
        self.task_results: Dict[str, CrawlerResult] = {}
        
    async def start_crawler_task(self, task: CrawlerTask) -> str:
        """启动爬虫任务"""
        
        # 创建任务日志记录器
        platform_str = self._get_platform_string(task.platform)
        task_logger = logging_manager.create_task_logger(task.task_id, platform_str)
        
        try:
            task_logger.log_event(
                TaskEventType.TASK_STARTED,
                f"开始启动爬虫任务: 平台={platform_str}, 类型={task.task_type.value}",
                data={
                    "platform": platform_str,
                    "task_type": task.task_type.value,
                    "keywords": task.keywords,
                    "content_ids": task.content_ids,
                    "xhs_note_urls": task.xhs_note_urls,
                    "creator_ids": task.creator_ids,
                    "max_count": task.max_count,
                    "max_comments": task.max_comments
                }
            )
            
            # 启动异步任务
            async_task = asyncio.create_task(
                self._run_mediacrawler_process(task, task_logger)
            )
            
            self.running_tasks[task.task_id] = {
                "task": async_task,
                "status": "running",
                "done": False,
                "result": None
            }
            
            logger.info(f"爬虫任务 {task.task_id} 已启动")
            return task.task_id
            
        except Exception as e:
            error_msg = f"启动爬虫任务失败: {str(e)}"
            logger.error(error_msg)
            
            task_logger.log_event(
                TaskEventType.TASK_FAILED,
                error_msg,
                error=str(e)
            )
            
            self.task_results[task.task_id] = CrawlerResult(
                task_id=task.task_id,
                success=False,
                message=error_msg
            )
            raise
    
    async def _run_mediacrawler_process(self, task: CrawlerTask, task_logger):
        """运行MediaCrawler进程"""
        result = None
        temp_config_file = None
        try:
            task_logger.log_event(TaskEventType.TASK_PROGRESS, "开始准备MediaCrawler")
            
            # 1. 准备配置（用于日志记录）
            await self._create_temp_config(task)
            
            # 2. 构建执行命令
            cmd = self._build_crawler_command(task)
            
            task_logger.log_event(TaskEventType.TASK_PROGRESS, "开始执行MediaCrawler")
            
            # 3. 执行爬虫进程
            result = await self._execute_crawler_process(cmd, task_logger, task)
            
            # 安全获取消息内容
            message = result.get('message', result.get('error', '无详细信息'))
            task_logger.log_event(
                TaskEventType.TASK_COMPLETED if result["success"] else TaskEventType.TASK_FAILED,
                f"MediaCrawler执行{'成功' if result['success'] else '失败'}: {message}"
            )
            
            # 4. 保存任务结果
            crawler_result = CrawlerResult(
                task_id=task.task_id,
                success=result["success"],
                message=message,
                data_count=result.get("data_count", 0),
                error_count=result.get("error_count", 0),
                data=result.get("data", []),
                errors=result.get("errors", [])
            )
            self.task_results[task.task_id] = crawler_result
            
            # 5. 移除已完成的任务从运行队列
            if task.task_id in self.running_tasks:
                del self.running_tasks[task.task_id]
                
            return result
            
        except Exception as e:
            error_msg = f"执行MediaCrawler时发生错误: {str(e)}"
            logger.error(f"❌ {error_msg}")
            task_logger.log_event(TaskEventType.TASK_FAILED, error_msg)
            
            result = {
                "success": False,
                "message": error_msg,
                "data_count": 0,
                "error_count": 1,
                "data": []
            }
            
            # 保存错误结果
            crawler_result = CrawlerResult(
                task_id=task.task_id,
                success=False,
                message=error_msg,
                data_count=0,
                error_count=1,
                data=[],
                errors=[error_msg]
            )
            self.task_results[task.task_id] = crawler_result
            
            # 移除失败的任务从运行队列
            if task.task_id in self.running_tasks:
                del self.running_tasks[task.task_id]
                
            return result
    
    async def _create_temp_config(self, task: CrawlerTask) -> Optional[str]:
        """
        准备最终的配置参数
        使用基于Pydantic模型的类型安全配置管理
        """
        try:
            config_manager = get_config_manager()
            
            # 🎯 使用新的基于模型的配置管理
            # 构建爬虫配置，传入任务的config作为request_config
            crawler_config: CrawlerConfig = config_manager.build_crawler_config(
                platform=task.platform.value,
                request_config=task.config  # 这是CrawlerConfigRequest类型
            )
            
            # 从其他任务参数创建覆盖配置
            task_overrides = CrawlerConfigRequest(
                enable_proxy=task.enable_proxy,
                headless=task.headless,
                enable_comments=task.enable_comments,
                enable_sub_comments=task.enable_sub_comments,
                max_comments=task.max_comments,
                save_data_option=task.save_data_option
            )
            
            # 重新构建配置，应用任务级覆盖
            final_config: CrawlerConfig = config_manager.build_crawler_config(
                platform=task.platform.value,
                request_config=task_overrides if not task.config else task.config
            )
            
            logger.info(f"🔧 配置构建完成 - 平台: {task.platform.value}")
            logger.info(f"📝 最终配置: headless={final_config.headless}, enable_proxy={final_config.enable_proxy}, timeout={final_config.timeout}")
            
            # 保存类型安全的配置对象
            task._final_config = final_config
            
        except Exception as e:
            logger.error(f"配置构建失败: {e}")
            raise
    
    def _build_crawler_command(self, task: CrawlerTask) -> List[str]:
        """构建MediaCrawler命令行"""
        logger.info(f"🔧 开始构建命令行参数...")
        
        platform_str = self._get_platform_string(task.platform)
        
        # 🍪 Cookies处理逻辑
        # 根据 clear_cookies 决定是否保存登录状态
        save_login_state = not task.clear_cookies

        if task.clear_cookies:
            # 清除cookies，强制重新登录
            cookies_manager.clear_cookies(platform_str)
            logger.info(f"🗑️  已清除cookies，将重新登录: {platform_str}")
        else:
            # 检查是否有缓存的cookies
            cached_cookies = cookies_manager.load_cookies(platform_str, max_age_days=7)
            if cached_cookies:
                logger.info(f"🍪 有缓存的cookies可用: {platform_str}")
            else:
                logger.info(f"📄 未找到有效cookies，将需要重新登录: {platform_str}")

        # 基础命令
        cmd = [
            "python", "main.py",
            "--platform", platform_str,
            "--type", task.task_type.value,
            "--max_count", str(task.max_count),
            "--max_comments", str(task.max_comments),
            "--headless", str(task.headless).lower(),
            "--enable_proxy", str(task.enable_proxy).lower(),
            "--save_data_option", task.save_data_option,
            "--get_comment", str(task.enable_comments).lower(),
            "--get_sub_comment", str(task.enable_sub_comments).lower(),
            "--save_login_state", str(save_login_state).lower()
        ]
        
        # 根据任务类型添加特定参数
        if task.task_type == CrawlerTaskType.SEARCH:
            if task.keywords:
                cmd.extend(["--keywords", ",".join(task.keywords)])
                logger.info(f"🔍 搜索关键词: {','.join(task.keywords)}")
            else:
                logger.warning("⚠️  Search模式需要提供keywords参数")
        
        elif task.task_type == CrawlerTaskType.DETAIL:
            if task.content_ids:
                # 根据平台设置相应的内容参数
                if platform_str == "xhs":
                    # 小红书使用专门的xhs_note_urls参数，包含完整的安全参数
                    if task.xhs_note_urls:
                        # 使用引号包裹URL列表，避免命令行解析问题
                        urls_param = ";".join(task.xhs_note_urls)
                        cmd.extend(["--xhs_note_urls", f'"{urls_param}"'])
                        logger.info(f"🔧 小红书笔记URL列表: {','.join(task.xhs_note_urls)}")
                    else:
                        logger.warning("⚠️  小红书详情模式缺少xhs_note_urls参数，可能导致爬取失败")
                        # 降级处理：使用content_ids构造基础URL（但缺少安全参数）
                        ids_param = ";".join(task.content_ids)
                        cmd.extend(["--xhs_note_urls", f'"{ids_param}"'])
                        logger.info(f"🔧 小红书笔记ID列表(降级): {','.join(task.content_ids)}")
                
                elif platform_str == "dy":
                    cmd.extend(["--dy_ids", ";".join(task.content_ids)])
                    logger.info(f"🔧 抖音视频ID列表: {','.join(task.content_ids)}")
                
                elif platform_str == "ks":
                    cmd.extend(["--ks_ids", ";".join(task.content_ids)])
                    logger.info(f"🔧 快手视频ID列表: {','.join(task.content_ids)}")
                
                elif platform_str == "bili":
                    cmd.extend(["--bili_ids", ";".join(task.content_ids)])
                    logger.info(f"🔧 B站视频BVID列表: {','.join(task.content_ids)}")
                
                elif platform_str == "wb":
                    cmd.extend(["--weibo_ids", ";".join(task.content_ids)])
                    logger.info(f"🔧 微博帖子ID列表: {','.join(task.content_ids)}")
                
                elif platform_str == "zhihu":
                    cmd.extend(["--zhihu_urls", ";".join(task.content_ids)])
                    logger.info(f"🔧 知乎URL列表: {','.join(task.content_ids)}")
            else:
                logger.warning("⚠️  Detail模式需要提供content_ids参数")
        
        elif task.task_type == CrawlerTaskType.CREATOR:
            if task.creator_ids:
                # 根据平台设置相应的创作者参数
                if platform_str == "xhs":
                    cmd.extend(["--xhs_creator_ids", ";".join(task.creator_ids)])
                    logger.info(f"🔧 小红书创作者ID列表: {','.join(task.creator_ids)}")
                
                elif platform_str == "dy":
                    cmd.extend(["--dy_creator_ids", ";".join(task.creator_ids)])
                    logger.info(f"🔧 抖音创作者ID列表: {','.join(task.creator_ids)}")
                
                elif platform_str == "ks":
                    cmd.extend(["--ks_creator_ids", ";".join(task.creator_ids)])
                    logger.info(f"🔧 快手创作者ID列表: {','.join(task.creator_ids)}")
                
                elif platform_str == "bili":
                    cmd.extend(["--bili_creator_ids", ";".join(task.creator_ids)])
                    logger.info(f"🔧 B站创作者ID列表: {','.join(task.creator_ids)}")
                
                elif platform_str == "wb":
                    cmd.extend(["--weibo_creator_ids", ";".join(task.creator_ids)])
                    logger.info(f"🔧 微博创作者ID列表: {','.join(task.creator_ids)}")
                
                elif platform_str == "zhihu":
                    # 知乎和贴吧使用URL格式
                    cmd.extend(["--zhihu_creator_urls", ";".join(task.creator_ids)])
                    logger.info(f"🔧 知乎创作者URL列表: {','.join(task.creator_ids)}")
                
                elif platform_str == "tieba":
                    cmd.extend(["--tieba_creator_urls", ";".join(task.creator_ids)])
                    logger.info(f"🔧 贴吧创作者URL列表: {','.join(task.creator_ids)}")
            else:
                logger.warning("⚠️  Creator模式需要提供creator_ids参数")
        
        logger.info(f"🚀 构建的命令: {' '.join(cmd)}")
        return cmd
    
    async def _execute_crawler_process(self, cmd: List[str], task_logger, task: CrawlerTask) -> Dict[str, Any]:
        """执行爬虫进程并实时监控进度"""
        try:
            # 异步执行子进程
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=MEDIACRAWLER_PATH
            )
            
            # 实时读取输出并解析进度
            stdout_lines = []
            stderr_lines = []
            
            async def read_stdout():
                """读取标准输出并解析进度"""
                async for line in process.stdout:
                    line_text = line.decode('utf-8', errors='ignore').strip()
                    if line_text:
                        stdout_lines.append(line_text)
                        # 解析进度信息
                        await self._parse_progress_from_line(line_text, task_logger)
            
            async def read_stderr():
                """读取错误输出"""
                async for line in process.stderr:
                    line_text = line.decode('utf-8', errors='ignore').strip()
                    if line_text:
                        stderr_lines.append(line_text)
                        # 记录错误日志
                        task_logger.log_event(
                            TaskEventType.CRAWLER_ERROR,
                            f"MediaCrawler stderr: {line_text}"
                        )
            
            # 并发读取stdout和stderr
            await asyncio.gather(read_stdout(), read_stderr())
            
            # 等待进程结束
            returncode = await process.wait()
            
            # 合并输出
            stdout_text = "\n".join(stdout_lines)
            stderr_text = "\n".join(stderr_lines)
            
            # 从输出中解析最终数据数量（MediaCrawler可能输出到stderr）
            combined_output = stdout_text + "\n" + stderr_text
            data_count = self._parse_data_count_from_output(combined_output)
            
            # 🍪 尝试提取并保存新的cookies
            await self._extract_and_save_cookies(task.platform, stdout_text, stderr_text, task.task_id)
            
            # 检查是否成功：优先检查成功标志，其次检查退出码
            success_indicators = [
                "Successfully upserted",  # 数据库插入成功
                "Xhs Crawler finished",   # 爆取器正常结束
                "Stop xiaohongshu crawler successful",  # 爆取器正常停止
                "task_completed",         # 任务完成事件
                "MediaCrawler执行成功",  # 明确的成功消息
            ]
            
            # 检查错误指示器
            error_indicators = [
                "Failed to",
                "Error:",
                "Exception:",
                "Traceback",
                "执行失败"
            ]
            
            has_success_indicator = any(indicator in combined_output for indicator in success_indicators)
            has_error_indicator = any(indicator in combined_output for indicator in error_indicators)
            has_data_operations = "HTTP/2 201 Created" in stderr_text or "HTTP/2 200 OK" in stderr_text
            clean_exit = returncode == 0
            
            # 判断任务是否成功：有成功标志或数据操作成功，且没有严重错误
            is_success = (has_success_indicator or has_data_operations or clean_exit) and not has_error_indicator
            
            if is_success:
                # 更新最终进度状态
                task_logger.update_progress("completed", 100.0, items_completed=data_count)
                task_logger.log_event(
                    TaskEventType.TASK_COMPLETED,
                    f"MediaCrawler执行成功 (数据: {data_count}条, 退出码: {returncode})",
                    data={"final_data_count": data_count, "returncode": returncode}
                )

                # 尝试从数据库获取实际采集的数据
                crawled_data = await self._fetch_crawled_data(task, data_count)

                return {
                    "success": True,
                    "data_count": data_count,
                    "data": crawled_data,  # 添加实际数据
                    "stdout": stdout_text,
                    "stderr": stderr_text,
                    "returncode": returncode,
                    "message": "数据采集成功"
                }
            else:
                # 更新失败状态进度
                task_logger.update_progress("failed", 0.0)
                task_logger.log_event(
                    TaskEventType.TASK_FAILED,
                    f"MediaCrawler执行失败: 退出码={returncode}, 数据量={data_count}",
                    error=stderr_text
                )
                
                return {
                    "success": False,
                    "error": f"进程退出码: {returncode}, 数据量: {data_count}",
                    "stdout": stdout_text,
                    "stderr": stderr_text,
                    "returncode": returncode
                }
                
        except Exception as e:
            task_logger.log_event(
                TaskEventType.CRAWLER_ERROR,
                f"执行MediaCrawler时发生异常: {str(e)}",
                error=str(e)
            )
            
            return {
                "success": False,
                "error": f"执行异常: {str(e)}"
            }
    
    async def _parse_progress_from_line(self, line: str, task_logger) -> None:
        """从输出行中解析实时进度"""
        import re
        
        try:
            # 解析不同类型的进度信息
            
            # 1. 登录相关进度 - 更通用的模式
            login_patterns = [
                (r"开始登录|login.*start|start.*login", "logging_in", 20.0),
                (r"登录成功|login.*success|success.*login", "logged_in", 30.0),
                (r"扫码登录|qr.*login|scan.*code", "qrcode_login", 25.0),
                (r"手机登录|phone.*login|mobile.*login", "phone_login", 25.0),
                (r"cookies.*load|load.*cookies", "loading_cookies", 15.0),
            ]
            
            for pattern, stage, percent in login_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    task_logger.update_progress(stage, percent)
                    return
            
            # 2. 爬虫启动和初始化
            init_patterns = [
                (r"crawler.*start|start.*crawler|开始.*爬|爬.*开始", "starting_crawler", 35.0),
                (r"browser.*start|start.*browser|浏览器.*启动", "browser_starting", 30.0),
                (r"page.*load|load.*page|页面.*加载", "page_loading", 40.0),
            ]
            
            for pattern, stage, percent in init_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    task_logger.update_progress(stage, percent)
                    return
            
            # 3. 爬取进度相关 - 增强模式匹配
            crawl_patterns = [
                (r"开始爬取|start.*crawl|crawl.*start", "crawling", 50.0),
                (r"正在爬取第\s*(\d+)\s*页|crawl.*page\s*(\d+)", "crawling", None),
                (r"已爬取\s*(\d+)\s*/\s*(\d+)|crawled\s*(\d+)\s*/\s*(\d+)", "crawling", None),
                (r"爬取.*?(\d+)\s*条.*?共\s*(\d+)|collected\s*(\d+).*of\s*(\d+)", "crawling", None),
                (r"processing.*(\d+).*of.*(\d+)|处理.*(\d+).*总共.*(\d+)", "processing", None),
            ]
            
            for pattern, stage, percent in crawl_patterns:
                match = re.search(pattern, line, re.IGNORECASE)
                if match:
                    if percent is not None:
                        task_logger.update_progress(stage, percent)
                    else:
                        # 动态计算进度
                        groups = [g for g in match.groups() if g is not None]
                        if len(groups) >= 2:
                            try:
                                completed = int(groups[0])
                                total = int(groups[1])
                                if total > 0:
                                    progress_percent = min(50.0 + (completed / total) * 40.0, 90.0)
                                    task_logger.update_progress(
                                        stage, progress_percent, 
                                        items_total=total, 
                                        items_completed=completed
                                    )
                            except ValueError:
                                pass
                    return
            
            # 4. 数据保存进度 - 包含更多变体
            save_patterns = [
                (r"开始保存|start.*sav|sav.*start", "saving", 90.0),
                (r"保存.*?(\d+)\s*条|sav.*(\d+).*item|(\d+).*saved", "saving", 95.0),
                (r"保存完成|sav.*complete|complete.*sav", "saving_completed", 98.0),
                (r"upsert.*success|successfully.*upsert", "database_saved", 99.0),
                (r"task.*complete|complete.*task|任务.*完成", "completed", 100.0),
            ]
            
            for pattern, stage, percent in save_patterns:
                match = re.search(pattern, line, re.IGNORECASE)
                if match:
                    task_logger.update_progress(stage, percent)
                    if match.groups():
                        try:
                            # 尝试提取数字
                            numbers = [g for g in match.groups() if g and g.isdigit()]
                            if numbers:
                                saved_count = int(numbers[0])
                                task_logger.update_progress(
                                    stage, percent,
                                    items_completed=saved_count
                                )
                        except:
                            pass
                    return
            
            # 5. 通用进度信息 - 捕获其他有用信息
            general_patterns = [
                (r"(\d+)%.*complete|complete.*(\d+)%", "processing", None),
                (r"step\s*(\d+)|阶段\s*(\d+)", "processing", None),
            ]
            
            for pattern, stage, percent in general_patterns:
                match = re.search(pattern, line, re.IGNORECASE)
                if match:
                    if percent is None and match.groups():
                        try:
                            # 从百分比中提取进度
                            percent_match = [g for g in match.groups() if g and g.isdigit()]
                            if percent_match:
                                extracted_percent = float(percent_match[0])
                                if 0 <= extracted_percent <= 100:
                                    task_logger.update_progress(stage, extracted_percent)
                        except:
                            pass
                    return
            
            # 4. 错误信息
            error_patterns = [
                r"错误",
                r"失败",
                r"异常",
                r"Error",
                r"Exception"
            ]
            
            for pattern in error_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    task_logger.log_event(
                        TaskEventType.CRAWLER_ERROR,
                        f"MediaCrawler报告错误: {line}"
                    )
                    return
            
            # 5. 记录重要信息行
            important_patterns = [
                r"开始",
                r"完成",
                r"成功",
                r"关键词",
                r"用户",
                r"内容"
            ]
            
            for pattern in important_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    task_logger.log_event(
                        TaskEventType.TASK_PROGRESS,
                        f"MediaCrawler: {line}"
                    )
                    return
                    
        except Exception as e:
            # 解析失败不影响主流程
            pass
    
    def _parse_data_count_from_output(self, output: str) -> int:
        """从输出中解析数据数量"""
        try:
            import re
            # 查找类似 "共爬取 123 条数据" 的模式
            # 特殊处理：统计Supabase操作成功次数
            supabase_success_count = len(re.findall(r"Successfully upserted.*?note_id", output))
            if supabase_success_count > 0:
                return supabase_success_count

            # 统计HTTP成功响应
            http_success_count = len(re.findall(r"HTTP/2 (200|201)", output))
            if http_success_count > 0:
                # 每个笔记通常有一个查询和一个插入，所以除以2
                return max(1, http_success_count // 2)

            # 原有模式匹配
            patterns = [
                r"共爬取\s*(\d+)\s*条",
                r"获取\s*(\d+)\s*条数据",
                r"crawled\s*(\d+)\s*items",
                r"total[:\s]*(\d+)",
                r"保存.*?(\d+)\s*条",
                r"完成.*?(\d+)\s*个"
            ]

            for pattern in patterns:
                matches = re.findall(pattern, output, re.IGNORECASE)
                if matches:
                    # 返回最大的数字（通常是最终结果）
                    return max(int(match) for match in matches)

            return 0
        except Exception:
            return 0

    async def _fetch_crawled_data(self, task: CrawlerTask, expected_count: int) -> List[Dict]:
        """
        从数据库获取任务采集的数据
        Args:
            task: 爬虫任务
            expected_count: 预期的数据数量
        Returns:
            采集的数据列表
        """
        try:
            from app.dataReader.factory import DataReaderFactory
            from app.dataReader.base import DataSourceType, PlatformType

            # 获取平台字符串并转换为枚举
            platform_str = self._get_platform_string(task.platform)

            # 将字符串转换为枚举类型
            platform_enum = PlatformType.XHS if platform_str == "xhs" else PlatformType.XHS

            # 创建数据读取器（默认使用database）
            reader = await DataReaderFactory.create_data_reader(
                source_type=DataSourceType.DATABASE,  # 使用枚举
                platform=platform_enum  # 使用枚举
            )

            # 根据任务类型获取数据
            data = []

            if task.task_type == CrawlerTaskType.DETAIL:
                # 获取指定的笔记详情
                # 优先使用 content_ids，如果没有则从 xhs_note_urls 提取
                content_ids_to_fetch = task.content_ids if task.content_ids else []

                # 如果是小红书且有 xhs_note_urls，从 URL 中提取 note_id
                if platform_str == "xhs" and task.xhs_note_urls:
                    import re
                    for url in task.xhs_note_urls[:expected_count]:
                        # 从 URL 中提取 note_id: /explore/{note_id}?...
                        match = re.search(r'/explore/([a-f0-9]+)', url)
                        if match:
                            content_ids_to_fetch.append(match.group(1))

                for content_id in content_ids_to_fetch[:expected_count]:
                    try:
                        result = await reader.get_content_by_id(
                            platform=platform_enum,
                            content_id=content_id
                        )
                        if result.success and result.data:
                            data.append(result.data)
                    except Exception as e:
                        logger.warning(f"Failed to fetch content {content_id}: {e}")

            elif task.task_type == CrawlerTaskType.SEARCH and task.keywords:
                # 获取搜索结果 - 获取最近的内容
                try:
                    from app.dataReader.base import QueryFilter, SortOrder

                    filter_obj = QueryFilter(
                        limit=expected_count,
                        sort_field="last_update_time",
                        sort_order=SortOrder.DESC
                    )
                    result = await reader.get_content_list(
                        platform=platform_enum,
                        filters=filter_obj
                    )
                    if result.success and result.data:
                        data.extend(result.data)
                except Exception as e:
                    logger.warning(f"Failed to fetch search results: {e}")

            elif task.task_type == CrawlerTaskType.CREATOR and task.creator_ids:
                # 获取创作者的内容
                for creator_id in task.creator_ids:
                    try:
                        result = await reader.get_creator_content(
                            platform=platform_enum,
                            user_id=creator_id
                        )
                        if result.success and result.data:
                            data.append(result.data)
                    except Exception as e:
                        logger.warning(f"Failed to fetch creator {creator_id} contents: {e}")

            logger.info(f"Successfully fetched {len(data)} items from database")
            return data

        except Exception as e:
            logger.warning(f"Failed to fetch crawled data from database: {e}")
            # 如果数据库读取失败，返回空列表但不影响任务成功状态
            return []
    
    async def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """获取任务状态"""
        base_status = {"task_id": task_id}
        
        if task_id in self.running_tasks:
            task_info = self.running_tasks[task_id]
            task = task_info["task"]
            base_status.update({
                "status": task_info["status"],
                "done": task_info["done"]
            })
        elif task_id in self.task_results:
            result = self.task_results[task_id]
            base_status.update({
                "status": "completed",
                "done": True,
                "success": result.success,
                "message": result.message,
                "data_count": result.data_count,
                "error_count": result.error_count
            })
        else:
            base_status.update({
                "status": "not_found",
                "done": False
            })
        
        # 获取进度信息
        progress = logging_manager.get_task_progress(task_id)
        if progress:
            base_status.update({
                "progress": {
                    "current_stage": progress.current_stage,
                    "progress_percent": progress.progress_percent,
                    "items_total": progress.items_total,
                    "items_completed": progress.items_completed,
                    "items_failed": progress.items_failed,
                    "current_item": progress.current_item,
                    "estimated_remaining_time": progress.estimated_remaining_time,
                    "last_update": progress.last_update
                }
            })
        
        return base_status
    
    async def get_task_result(self, task_id: str) -> Optional[CrawlerResult]:
        """获取任务结果"""
        return self.task_results.get(task_id)
    
    async def stop_task(self, task_id: str) -> bool:
        """停止任务"""
        if task_id in self.running_tasks:
            task_info = self.running_tasks[task_id]
            task = task_info["task"]
            task.cancel()
            
            try:
                await task
            except asyncio.CancelledError:
                pass
            
            self.task_results[task_id] = CrawlerResult(
                task_id=task_id,
                success=False,
                message="任务已被手动停止"
            )
            
            del self.running_tasks[task_id]
            logger.info(f"任务 {task_id} 已停止")
            return True
        
        return False
    
    async def list_running_tasks(self) -> List[str]:
        """列出运行中的任务"""
        return list(self.running_tasks.keys())
    
    async def get_task_events(self, task_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """获取任务事件日志"""
        events = logging_manager.get_task_events(task_id, limit)
        return [
            {
                "task_id": event.task_id,
                "event_type": event.event_type.value,
                "timestamp": event.timestamp,
                "message": event.message,
                "data": event.data,
                "platform": event.platform,
                "progress": event.progress,
                "error": event.error
            }
            for event in events
        ]
    
    async def get_system_stats(self) -> Dict[str, Any]:
        """获取系统统计信息"""
        running_count = len(self.running_tasks)
        completed_count = len(self.task_results)
        
        # 成功/失败统计
        success_count = sum(1 for result in self.task_results.values() if result.success)
        failed_count = completed_count - success_count
        
        # 数据统计
        total_data_count = sum(result.data_count for result in self.task_results.values())
        total_error_count = sum(result.error_count for result in self.task_results.values())
        
        # 从日志管理器获取额外统计
        logging_stats = logging_manager.get_system_stats()
        
        return {
            "tasks": {
                "running": running_count,
                "completed": completed_count,
                "success": success_count,
                "failed": failed_count
            },
            "data": {
                "total_crawled": total_data_count,
                "total_errors": total_error_count
            },
            "system": {
                "uptime": logging_stats.get("uptime", 0),
                "memory_usage": logging_stats.get("memory_usage", 0),
                "active_loggers": logging_stats.get("active_loggers", 0)
            }
        }
    
    async def cleanup_completed_tasks(self) -> Dict[str, Any]:
        """清理已完成的任务"""
        before_count = len(self.task_results)
        
        # 保留最近100个任务结果，删除其余的
        if before_count > 100:
            # 按任务ID排序，保留最新的100个
            sorted_tasks = sorted(self.task_results.items(), key=lambda x: x[0])
            tasks_to_remove = sorted_tasks[:-100]
            
            for task_id, _ in tasks_to_remove:
                del self.task_results[task_id]
                # 清理对应的任务日志
                logging_manager.cleanup_task_logger(task_id)
        
        after_count = len(self.task_results)
        cleaned_count = before_count - after_count
        
        logger.info(f"清理完成：删除了 {cleaned_count} 个已完成的任务")
        
        return {
            "cleaned_tasks": cleaned_count,
            "remaining_tasks": after_count,
            "message": f"已清理 {cleaned_count} 个已完成的任务"
        }
    
    def _get_platform_string(self, platform: PlatformType) -> str:
        """获取平台字符串"""
        platform_mapping = {
            PlatformType.XHS: "xhs",
            PlatformType.DOUYIN: "dy",
            PlatformType.BILIBILI: "bili",
            PlatformType.KUAISHOU: "ks",
            PlatformType.WEIBO: "wb",
            PlatformType.TIEBA: "tieba",
            PlatformType.ZHIHU: "zhihu"
        }
        return platform_mapping.get(platform, str(platform))

    async def _extract_and_save_cookies(self, platform: PlatformType, stdout_text: str, stderr_text: str, task_id: str) -> None:
        """尝试从MediaCrawler的browser_data目录中读取并保存新的cookies"""
        try:
            platform_str = self._get_platform_string(platform)
            
            # MediaCrawler保存cookies的路径
            browser_data_path = Path(MEDIACRAWLER_PATH) / "browser_data"
            cookies_pattern = f"{platform_str}_cookies_*.json"
            
            # 查找最新的cookies文件
            cookies_files = list(browser_data_path.glob(cookies_pattern))
            if cookies_files:
                # 按修改时间排序，取最新的
                latest_cookies_file = max(cookies_files, key=lambda f: f.stat().st_mtime)
                
                with open(latest_cookies_file, 'r', encoding='utf-8') as f:
                    cookies_data = json.load(f)
                
                # 将cookies转换为字符串格式
                if isinstance(cookies_data, list):
                    # 如果是cookies数组，转换为字符串
                    cookie_strings = []
                    for cookie in cookies_data:
                        if isinstance(cookie, dict) and 'name' in cookie and 'value' in cookie:
                            cookie_strings.append(f"{cookie['name']}={cookie['value']}")
                    
                    if cookie_strings:
                        cookies_str = "; ".join(cookie_strings)
                        # 保存到我们的cookies管理器
                        success = cookies_manager.save_cookies(platform_str, cookies_str, task_id)
                        if success:
                            logger.info(f"🍪 成功保存cookies [{platform_str}]: {len(cookie_strings)}个cookie")
                        else:
                            logger.warning(f"⚠️  保存cookies失败 [{platform_str}]")
                    else:
                        logger.warning(f"⚠️  Cookies数据格式异常 [{platform_str}]")
                else:
                    logger.warning(f"⚠️  Cookies数据不是数组格式 [{platform_str}]")
            else:
                logger.info(f"📄 未找到cookies文件 [{platform_str}]: {cookies_pattern}")
                
        except Exception as e:
            logger.error(f"❌ 提取并保存cookies失败 [{platform}]: {e}")


# 全局适配器实例
crawler_adapter = MediaCrawlerAdapter() 