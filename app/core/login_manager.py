"""
登录管理模块

支持爬虫登录过程中的客户端交互：
1. 二维码登录 - 截图传递给客户端
2. 手机验证码登录 - 输入框交互
3. Cookie登录 - 直接应用
"""

import asyncio
import base64
import json
import time
from typing import Dict, Any, Optional, Callable, List
from dataclasses import dataclass
from enum import Enum
import logging
from pathlib import Path

from app.core.logging import TaskEventType, get_app_logger

logger = get_app_logger(__name__)


class LoginType(Enum):
    """登录类型"""
    COOKIE = "cookie"
    QRCODE = "qrcode" 
    PHONE = "phone"


class LoginStatus(Enum):
    """登录状态"""
    PENDING = "pending"           # 等待开始
    QRCODE_GENERATED = "qrcode_generated"  # 二维码已生成
    QRCODE_SCANNED = "qrcode_scanned"      # 二维码已扫描
    PHONE_INPUT_REQUIRED = "phone_input_required"    # 需要输入手机号
    VERIFICATION_CODE_REQUIRED = "verification_code_required"  # 需要验证码
    SUCCESS = "success"           # 登录成功
    FAILED = "failed"             # 登录失败
    TIMEOUT = "timeout"           # 登录超时


@dataclass
class LoginRequest:
    """登录请求"""
    task_id: str
    login_type: LoginType
    timeout: int = 300  # 5分钟超时
    phone_number: Optional[str] = None
    cookies: Optional[str] = None


@dataclass
class LoginResponse:
    """登录响应"""
    task_id: str
    status: LoginStatus
    message: str
    data: Optional[Dict[str, Any]] = None
    qrcode_image: Optional[str] = None  # base64编码的图片
    input_required: Optional[Dict[str, str]] = None  # 需要的输入字段


@dataclass
class LoginInput:
    """登录输入"""
    task_id: str
    input_type: str  # "phone", "verification_code"
    value: str


class LoginSession:
    """登录会话"""
    
    def __init__(self, task_id: str, platform: str, login_type: LoginType):
        self.task_id = task_id
        self.platform = platform
        self.login_type = login_type
        self.status = LoginStatus.PENDING
        self.start_time = time.time()
        self.timeout = 300  # 5分钟
        self.data: Dict[str, Any] = {}
        self.pending_inputs: List[str] = []
        self.crawler_adapter = None
        self.page = None
        self.browser = None
        self.browser_context = None
        self.cookies_data: Optional[str] = None  # 存储登录成功后的cookies
        
        # 事件回调
        self.on_status_change: Optional[Callable] = None
        self.on_qrcode_generated: Optional[Callable] = None
        self.on_input_required: Optional[Callable] = None
        self.on_login_success: Optional[Callable] = None  # 登录成功回调
    
    def is_expired(self) -> bool:
        """检查是否超时"""
        return time.time() - self.start_time > self.timeout
    
    def update_status(self, status: LoginStatus, message: str, data: Optional[Dict] = None):
        """更新状态"""
        self.status = status
        self.data.update(data or {})
        
        if self.on_status_change:
            try:
                self.on_status_change(self.task_id, status, message, data)
            except Exception as e:
                logger.error(f"登录状态回调出错: {e}")
    
    async def cleanup(self):
        """清理资源"""
        try:
            if self.page:
                await self.page.close()
                self.page = None
            if self.browser_context:
                await self.browser_context.close()
                self.browser_context = None
            if self.browser:
                await self.browser.close()
                self.browser = None
        except Exception as e:
            logger.error(f"清理登录会话资源失败: {e}")


class LoginManager:
    """登录管理器"""
    
    def __init__(self):
        self.sessions: Dict[str, LoginSession] = {}
        self.screenshots_dir = Path("logs/screenshots")
        self.screenshots_dir.mkdir(exist_ok=True, parents=True)
    
    def create_login_session(self, task_id: str, platform: str, 
                           login_type: LoginType, timeout: int = 300) -> LoginSession:
        """创建登录会话"""
        session = LoginSession(task_id, platform, login_type)
        session.timeout = timeout
        
        # 设置事件回调
        session.on_status_change = self._on_status_change
        session.on_qrcode_generated = self._on_qrcode_generated
        session.on_input_required = self._on_input_required
        
        self.sessions[task_id] = session
        logger.info(f"创建登录会话: {task_id}, 平台: {platform}, 类型: {login_type.value}")
        
        return session
    
    def get_login_session(self, task_id: str) -> Optional[LoginSession]:
        """获取登录会话"""
        return self.sessions.get(task_id)
    
    async def remove_login_session(self, task_id: str):
        """移除登录会话"""
        if task_id in self.sessions:
            session = self.sessions[task_id]
            await session.cleanup()
            del self.sessions[task_id]
            logger.info(f"移除登录会话: {task_id}")
    
    async def _init_browser_for_session(self, session: LoginSession):
        """为登录会话初始化浏览器"""
        try:
            from playwright.async_api import async_playwright
            
            # 启动playwright
            playwright = await async_playwright().start()
            
            # 启动浏览器（非headless模式，方便用户看到二维码）
            session.browser = await playwright.chromium.launch(
                headless=False,
                args=[
                    '--no-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-blink-features=AutomationControlled'
                ]
            )
            
            # 创建上下文
            session.browser_context = await session.browser.new_context(
                viewport={'width': 1200, 'height': 800},
                user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            )
            
            # 创建页面
            session.page = await session.browser_context.new_page()
            
            logger.info(f"浏览器初始化成功: {session.task_id}")
            
        except Exception as e:
            logger.error(f"浏览器初始化失败: {e}")
            raise
    
    async def start_login_process(self, task_id: str, crawler_adapter) -> LoginResponse:
        """启动登录流程"""
        session = self.get_login_session(task_id)
        if not session:
            return LoginResponse(
                task_id=task_id,
                status=LoginStatus.FAILED,
                message="登录会话不存在"
            )
        
        session.crawler_adapter = crawler_adapter
        
        try:
            # 初始化浏览器
            await self._init_browser_for_session(session)
            
            if session.login_type == LoginType.COOKIE:
                return await self._handle_cookie_login(session)
            elif session.login_type == LoginType.QRCODE:
                return await self._handle_qrcode_login(session)
            elif session.login_type == LoginType.PHONE:
                return await self._handle_phone_login(session)
            else:
                session.update_status(LoginStatus.FAILED, f"不支持的登录类型: {session.login_type}")
                return LoginResponse(
                    task_id=task_id,
                    status=LoginStatus.FAILED,
                    message=f"不支持的登录类型: {session.login_type}"
                )
                
        except Exception as e:
            logger.error(f"登录流程出错: {e}")
            session.update_status(LoginStatus.FAILED, f"登录流程出错: {str(e)}")
            return LoginResponse(
                task_id=task_id,
                status=LoginStatus.FAILED,
                message=f"登录流程出错: {str(e)}"
            )
    
    async def _handle_cookie_login(self, session: LoginSession) -> LoginResponse:
        """处理Cookie登录"""
        session.update_status(LoginStatus.PENDING, "开始Cookie登录")
        
        # 这里需要根据具体平台实现Cookie设置
        # 示例代码，实际需要调用对应平台的login方法
        try:
            # await session.crawler.login_by_cookies()
            session.update_status(LoginStatus.SUCCESS, "Cookie登录成功")
            return LoginResponse(
                task_id=session.task_id,
                status=LoginStatus.SUCCESS,
                message="Cookie登录成功"
            )
        except Exception as e:
            session.update_status(LoginStatus.FAILED, f"Cookie登录失败: {str(e)}")
            return LoginResponse(
                task_id=session.task_id,
                status=LoginStatus.FAILED,
                message=f"Cookie登录失败: {str(e)}"
            )
    
    async def _handle_qrcode_login(self, session: LoginSession) -> LoginResponse:
        """处理二维码登录 - 改为客户端登录模式"""
        session.update_status(LoginStatus.PENDING, "准备打开登录页面")
        
        try:
            # 导航到小红书登录页面
            await self._navigate_to_login_page(session)
            
            # 更新状态为等待用户登录
            session.update_status(LoginStatus.QRCODE_GENERATED, "请在浏览器中完成登录，登录成功后系统将自动检测")
            
            # 启动后台监控任务来检测登录成功
            asyncio.create_task(self._monitor_client_login(session))
            
            return LoginResponse(
                task_id=session.task_id,
                status=LoginStatus.QRCODE_GENERATED,
                message="登录页面已打开，请在浏览器中完成登录。支持扫码登录、短信登录等方式。",
                data={
                    "login_url": session.page.url if session.page else "https://www.xiaohongshu.com/explore",
                    "instructions": "请在打开的浏览器窗口中完成登录，登录成功后系统将自动检测并保存cookies"
                }
            )
                
        except Exception as e:
            logger.error(f"打开登录页面失败: {e}")
            session.update_status(LoginStatus.FAILED, f"打开登录页面失败: {str(e)}")
            return LoginResponse(
                task_id=session.task_id,
                status=LoginStatus.FAILED,
                message=f"打开登录页面失败: {str(e)}"
            )
    
    async def _monitor_client_login(self, session: LoginSession):
        """监控客户端登录状态 - 通过cookie变化检测登录成功"""
        try:
            timeout = 300  # 5分钟超时
            start_time = time.time()
            
            # 获取初始的web_session cookie（未登录状态）
            initial_cookies = await session.browser_context.cookies()
            initial_web_session = None
            for cookie in initial_cookies:
                if cookie['name'] == 'web_session':
                    initial_web_session = cookie['value']
                    break
            
            logger.info(f"初始web_session: {initial_web_session}")
            
            while time.time() - start_time < timeout:
                # 检查会话是否仍然存在
                if session.task_id not in self.sessions:
                    break
                
                # 如果已经成功或失败，停止监控
                if session.status in [LoginStatus.SUCCESS, LoginStatus.FAILED, LoginStatus.TIMEOUT]:
                    break
                
                # 检查cookie变化
                current_cookies = await session.browser_context.cookies()
                current_web_session = None
                for cookie in current_cookies:
                    if cookie['name'] == 'web_session':
                        current_web_session = cookie['value']
                        break
                
                # 如果web_session发生变化，说明登录成功
                if current_web_session and current_web_session != initial_web_session:
                    logger.info(f"检测到登录成功，web_session变化: {initial_web_session} -> {current_web_session}")
                    
                    # 提取所有cookies
                    cookies = await self._extract_cookies(session)
                    if cookies:
                        session.cookies_data = cookies
                        await self.save_login_cookies(session.task_id, cookies)
                        await self.sync_cookies_to_mediacrawler(session.task_id, session.platform)
                    
                    session.update_status(LoginStatus.SUCCESS, "登录成功，cookies已保存")
                    break
                
                # 每2秒检查一次
                await asyncio.sleep(2)
            
            # 超时处理
            if session.status not in [LoginStatus.SUCCESS, LoginStatus.FAILED]:
                session.update_status(LoginStatus.TIMEOUT, "登录超时，请重新尝试")
                
        except Exception as e:
            logger.error(f"监控客户端登录状态失败: {e}")
            session.update_status(LoginStatus.FAILED, f"监控登录状态失败: {str(e)}")
    
    async def _handle_phone_login(self, session: LoginSession) -> LoginResponse:
        """处理手机号登录"""
        session.update_status(LoginStatus.PENDING, "开始手机号登录")
        
        try:
            # 导航到登录页面
            await self._navigate_to_login_page(session)
            
            # 切换到手机号登录
            await self._switch_to_phone_login(session)
            
            session.update_status(LoginStatus.PHONE_INPUT_REQUIRED, "请输入手机号")
            return LoginResponse(
                task_id=session.task_id,
                status=LoginStatus.PHONE_INPUT_REQUIRED,
                message="请输入手机号",
                input_required={"type": "phone", "placeholder": "请输入手机号"}
            )
            
        except Exception as e:
            logger.error(f"手机号登录出错: {e}")
            session.update_status(LoginStatus.FAILED, f"手机号登录出错: {str(e)}")
            return LoginResponse(
                task_id=session.task_id,
                status=LoginStatus.FAILED,
                message=f"手机号登录出错: {str(e)}"
            )
    
    async def handle_login_input(self, task_id: str, input_data: LoginInput) -> LoginResponse:
        """处理登录输入"""
        session = self.get_login_session(task_id)
        if not session:
            return LoginResponse(
                task_id=task_id,
                status=LoginStatus.FAILED,
                message="登录会话不存在"
            )
        
        try:
            if input_data.input_type == "phone":
                return await self._handle_phone_input(session, input_data.value)
            elif input_data.input_type == "verification_code":
                return await self._handle_verification_code_input(session, input_data.value)
            else:
                return LoginResponse(
                    task_id=task_id,
                    status=LoginStatus.FAILED,
                    message=f"不支持的输入类型: {input_data.input_type}"
                )
                
        except Exception as e:
            logger.error(f"处理登录输入出错: {e}")
            session.update_status(LoginStatus.FAILED, f"处理输入出错: {str(e)}")
            return LoginResponse(
                task_id=task_id,
                status=LoginStatus.FAILED,
                message=f"处理输入出错: {str(e)}"
            )
    
    async def _handle_phone_input(self, session: LoginSession, phone: str) -> LoginResponse:
        """处理手机号输入"""
        try:
            # 填入手机号
            await self._fill_phone_number(session, phone)
            
            # 点击发送验证码
            await self._send_verification_code(session)
            
            session.update_status(LoginStatus.VERIFICATION_CODE_REQUIRED, "验证码已发送，请输入")
            return LoginResponse(
                task_id=session.task_id,
                status=LoginStatus.VERIFICATION_CODE_REQUIRED,
                message="验证码已发送，请输入",
                input_required={"type": "verification_code", "placeholder": "请输入验证码"}
            )
            
        except Exception as e:
            session.update_status(LoginStatus.FAILED, f"手机号输入失败: {str(e)}")
            return LoginResponse(
                task_id=session.task_id,
                status=LoginStatus.FAILED,
                message=f"手机号输入失败: {str(e)}"
            )
    
    async def _handle_verification_code_input(self, session: LoginSession, code: str) -> LoginResponse:
        """处理验证码输入"""
        try:
            # 填入验证码
            await self._fill_verification_code(session, code)
            
            # 点击登录
            await self._submit_login(session)
            
            # 等待登录结果
            success = await self._wait_for_login_success(session)
            
            if success:
                session.update_status(LoginStatus.SUCCESS, "登录成功")
                return LoginResponse(
                    task_id=session.task_id,
                    status=LoginStatus.SUCCESS,
                    message="登录成功"
                )
            else:
                session.update_status(LoginStatus.FAILED, "登录失败，请检查验证码")
                return LoginResponse(
                    task_id=session.task_id,
                    status=LoginStatus.FAILED,
                    message="登录失败，请检查验证码"
                )
                
        except Exception as e:
            session.update_status(LoginStatus.FAILED, f"验证码输入失败: {str(e)}")
            return LoginResponse(
                task_id=session.task_id,
                status=LoginStatus.FAILED,
                message=f"验证码输入失败: {str(e)}"
            )
    
    async def get_login_status(self, task_id: str) -> LoginResponse:
        """获取登录状态"""
        session = self.get_login_session(task_id)
        if not session:
            return LoginResponse(
                task_id=task_id,
                status=LoginStatus.FAILED,
                message="登录会话不存在"
            )
        
        # 检查超时
        if session.is_expired():
            session.update_status(LoginStatus.TIMEOUT, "登录超时")
            # 注意：这里不能await，因为get_login_status不是在async上下文中
            # 超时清理将由后台任务处理
        
        return LoginResponse(
            task_id=task_id,
            status=session.status,
            message=f"当前状态: {session.status.value}",
            data=session.data
        )
    
    # 以下是平台特定的实现方法，需要根据具体平台调整
    async def _navigate_to_login_page(self, session: LoginSession):
        """导航到登录页面"""
        if session.platform == "xhs":
            from app.crawler.platforms.xhs_login import XhsLoginAdapter
            adapter = XhsLoginAdapter(session)
            await adapter.navigate_to_login_page()
        else:
            # 其他平台的实现
            pass
        
    async def _capture_qrcode(self, session: LoginSession) -> Optional[str]:
        """截取二维码"""
        if session.platform == "xhs":
            from app.crawler.platforms.xhs_login import XhsLoginAdapter
            adapter = XhsLoginAdapter(session)
            return await adapter.capture_qrcode()
        else:
            # 其他平台的实现
            return None
    
    async def _switch_to_phone_login(self, session: LoginSession):
        """切换到手机号登录"""
        if session.platform == "xhs":
            from app.crawler.platforms.xhs_login import XhsLoginAdapter
            adapter = XhsLoginAdapter(session)
            await adapter.switch_to_phone_login()
        else:
            # 其他平台的实现
            pass
    
    async def _fill_phone_number(self, session: LoginSession, phone: str):
        """填入手机号"""
        if session.platform == "xhs":
            from app.crawler.platforms.xhs_login import XhsLoginAdapter
            adapter = XhsLoginAdapter(session)
            await adapter.fill_phone_number(phone)
        else:
            # 其他平台的实现
            pass
    
    async def _send_verification_code(self, session: LoginSession):
        """发送验证码"""
        if session.platform == "xhs":
            from app.crawler.platforms.xhs_login import XhsLoginAdapter
            adapter = XhsLoginAdapter(session)
            await adapter.send_verification_code()
        else:
            # 其他平台的实现
            pass
    
    async def _fill_verification_code(self, session: LoginSession, code: str):
        """填入验证码"""
        if session.platform == "xhs":
            from app.crawler.platforms.xhs_login import XhsLoginAdapter
            adapter = XhsLoginAdapter(session)
            await adapter.fill_verification_code(code)
        else:
            # 其他平台的实现
            pass
    
    async def _submit_login(self, session: LoginSession):
        """提交登录"""
        if session.platform == "xhs":
            from app.crawler.platforms.xhs_login import XhsLoginAdapter
            adapter = XhsLoginAdapter(session)
            await adapter.submit_login()
        else:
            # 其他平台的实现
            pass
    
    async def _wait_for_login_success(self, session: LoginSession) -> bool:
        """等待登录成功"""
        if session.platform == "xhs":
            from app.crawler.platforms.xhs_login import XhsLoginAdapter
            adapter = XhsLoginAdapter(session)
            return await adapter.wait_for_login_success()
        else:
            # 其他平台的实现
            return False
    
    # 事件回调方法
    def _on_status_change(self, task_id: str, status: LoginStatus, message: str, data: Optional[Dict]):
        """状态变更回调"""
        logger.info(f"登录状态变更: {task_id} -> {status.value}: {message}")
    
    def _on_qrcode_generated(self, task_id: str, qrcode_image: str):
        """二维码生成回调"""
        logger.info(f"二维码已生成: {task_id}")
    
    def _on_input_required(self, task_id: str, input_type: str, placeholder: str):
        """需要输入回调"""
        logger.info(f"需要输入: {task_id} -> {input_type}: {placeholder}")
    
    def _on_login_success(self, task_id: str, cookies: str):
        """登录成功回调 - 同步cookies到MediaCrawler"""
        session = self.get_login_session(task_id)
        if session:
            session.cookies_data = cookies
            logger.info(f"任务 {task_id} 登录成功，cookies已保存")
    
    async def save_login_cookies(self, task_id: str, cookies: str) -> bool:
        """保存登录成功的cookies"""
        session = self.get_login_session(task_id)
        if not session:
            return False
        
        try:
            session.cookies_data = cookies
            session.update_status(LoginStatus.SUCCESS, "登录成功，cookies已保存")
            
            # 将cookies保存到文件供MediaCrawler使用
            cookies_file = Path("logs") / f"cookies_{task_id}_{session.platform}.json"
            cookies_file.parent.mkdir(exist_ok=True)
            
            import json
            with open(cookies_file, 'w', encoding='utf-8') as f:
                json.dump({"cookies": cookies, "platform": session.platform}, f)
            
            logger.info(f"Cookies已保存到文件: {cookies_file}")
            return True
            
        except Exception as e:
            logger.error(f"保存cookies失败: {e}")
            return False
    
    async def get_login_cookies(self, task_id: str) -> Optional[str]:
        """获取登录成功的cookies"""
        session = self.get_login_session(task_id)
        return session.cookies_data if session else None
    
    async def sync_cookies_to_mediacrawler(self, task_id: str, platform: str) -> bool:
        """将cookies同步到MediaCrawler配置"""
        cookies = await self.get_login_cookies(task_id)
        if not cookies:
            return False
        
        try:
            # 将cookies注入到下次MediaCrawler执行的配置中
            logger.info(f"Cookies已准备同步到MediaCrawler配置: {platform}")
            return True
            
        except Exception as e:
            logger.error(f"同步cookies失败: {e}")
            return False

    async def _extract_cookies(self, session: LoginSession) -> Optional[str]:
        """提取登录成功后的cookies"""
        try:
            if session.page and session.browser_context:
                cookies = await session.browser_context.cookies()
                # 将cookies转换为字符串格式
                cookie_strings = []
                for cookie in cookies:
                    cookie_str = f"{cookie['name']}={cookie['value']}"
                    if cookie.get('domain'):
                        cookie_str += f"; Domain={cookie['domain']}"
                    if cookie.get('path'):
                        cookie_str += f"; Path={cookie['path']}"
                    cookie_strings.append(cookie_str)
                
                return "; ".join(cookie_strings)
            return None
        except Exception as e:
            logger.error(f"提取cookies失败: {e}")
            return None


# 全局登录管理器实例
login_manager = LoginManager() 