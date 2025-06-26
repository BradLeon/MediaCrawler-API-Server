"""
小红书登录适配器

实现小红书平台的具体登录操作，包括：
1. 二维码登录流程
2. 手机号+验证码登录流程
3. Cookie登录
"""

import asyncio
import time
from typing import Optional
from playwright.async_api import Page

from app.core.login_manager import LoginSession, LoginStatus
from app.core.logging import get_app_logger

logger = get_app_logger(__name__)


class XhsLoginAdapter:
    """小红书登录适配器"""
    
    def __init__(self, session: LoginSession):
        self.session = session
        self.page: Page = session.page
    
    async def navigate_to_login_page(self):
        """导航到小红书登录页面"""
        try:
            logger.info("正在打开小红书登录页面...")
            
            # 直接访问小红书首页，通常会自动显示登录界面
            await self.page.goto("https://www.xiaohongshu.com/explore", wait_until="networkidle")
            
            # 等待页面加载
            await self.page.wait_for_timeout(2000)
            
            # 尝试点击登录按钮（如果存在）
            login_button_selectors = [
                "xpath=//*[@id='app']/div[1]/div[2]/div[1]/ul/div[1]/button",  # 原MediaCrawler使用的选择器
                "text=登录",
                "[data-testid='login-button']",
                ".login-btn",
                "a[href*='signin']",
                "button:has-text('登录')"
            ]
            
            login_clicked = False
            for selector in login_button_selectors:
                try:
                    element = await self.page.query_selector(selector)
                    if element and await element.is_visible():
                        await element.click()
                        logger.info(f"成功点击登录按钮: {selector}")
                        login_clicked = True
                        break
                except:
                    continue
            
            if not login_clicked:
                # 如果没有找到登录按钮，直接访问登录页面
                logger.info("未找到登录按钮，直接访问登录页面")
                await self.page.goto("https://www.xiaohongshu.com/signin", wait_until="networkidle")
            
            # 等待登录界面加载
            await self.page.wait_for_timeout(3000)
            
            current_url = self.page.url
            logger.info(f"登录页面已打开: {current_url}")
            
        except Exception as e:
            logger.error(f"导航到小红书登录页面失败: {e}")
            raise
    
    async def capture_qrcode(self) -> Optional[str]:
        """截取二维码"""
        try:
            logger.info("开始截取二维码...")
            
            # 等待页面稳定
            await self.page.wait_for_timeout(3000)
            
            # 小红书二维码可能的选择器（更全面的列表）
            qrcode_selectors = [
                # Canvas元素
                "canvas[data-testid='qrcode-canvas']",
                "canvas.qr-code",
                "canvas",
                # 图片元素
                ".qr-code img",
                ".qrcode-container img",
                ".login-qr-code img",
                ".qr-img",
                "img[alt*='二维码']",
                "img[alt*='qrcode']",
                "img[src*='qr']",
                # 容器元素
                ".qr-code",
                ".qrcode",
                ".qrcode-container",
                ".login-qr-code",
                ".qr-login-code",
                ".scan-code",
                # 通用选择器
                "[data-testid*='qr']",
                "[class*='qr']",
                "[id*='qr']"
            ]
            
            # 先尝试找到二维码容器或元素
            qrcode_element = None
            used_selector = None
            
            # 打印当前页面信息用于调试
            current_url = self.page.url
            page_title = await self.page.title()
            logger.info(f"当前页面URL: {current_url}")
            logger.info(f"当前页面标题: {page_title}")
            
            # 检查页面上所有可能的元素
            all_elements = await self.page.query_selector_all("*")
            logger.info(f"页面总元素数量: {len(all_elements)}")
            
            # 查找包含'qr'或'二维码'的元素
            qr_related_elements = await self.page.query_selector_all("[class*='qr'], [id*='qr'], [data-testid*='qr']")
            logger.info(f"找到包含'qr'的元素数量: {len(qr_related_elements)}")
            
            for element in qr_related_elements[:5]:  # 只检查前5个
                try:
                    tag_name = await element.evaluate("el => el.tagName")
                    class_name = await element.evaluate("el => el.className")
                    logger.info(f"QR相关元素: {tag_name}, class: {class_name}")
                except:
                    pass
            
            # 尝试找到二维码元素
            for selector in qrcode_selectors:
                try:
                    logger.info(f"尝试选择器: {selector}")
                    element = await self.page.query_selector(selector)
                    if element:
                        # 检查元素是否可见
                        is_visible = await element.is_visible()
                        logger.info(f"找到元素 {selector}, 可见性: {is_visible}")
                        
                        if is_visible:
                            qrcode_element = element
                            used_selector = selector
                            logger.info(f"确认使用选择器: {selector}")
                            break
                except Exception as e:
                    logger.debug(f"选择器 {selector} 失败: {e}")
                    continue
            
            if not qrcode_element:
                # 如果没有找到二维码，可能需要切换到二维码登录模式
                logger.info("未找到二维码，尝试切换到二维码登录模式")
                await self._switch_to_qrcode_mode()
                
                # 等待二维码加载
                await self.page.wait_for_timeout(2000)
                
                # 再次尝试找到二维码
                for selector in qrcode_selectors:
                    try:
                        logger.info(f"重新尝试选择器: {selector}")
                        element = await self.page.query_selector(selector)
                        if element and await element.is_visible():
                            qrcode_element = element
                            used_selector = selector
                            logger.info(f"重新找到二维码: {selector}")
                            break
                    except:
                        continue
            
            if qrcode_element:
                # 截取二维码图片
                logger.info(f"开始截图，使用选择器: {used_selector}")
                screenshot_bytes = await qrcode_element.screenshot()
                
                # 转换为base64
                import base64
                qrcode_base64 = base64.b64encode(screenshot_bytes).decode('utf-8')
                
                logger.info(f"成功截取二维码，大小: {len(screenshot_bytes)} bytes")
                return qrcode_base64
            else:
                # 如果还是没找到，尝试截取整个页面的特定区域
                logger.warning("仍未找到二维码元素，尝试截取页面区域")
                
                # 尝试截取页面中心区域（通常二维码在中心）
                viewport_size = self.page.viewport_size
                if viewport_size:
                    center_x = viewport_size['width'] // 2
                    center_y = viewport_size['height'] // 2
                    
                    # 截取中心区域 300x300
                    screenshot_bytes = await self.page.screenshot(
                        clip={
                            'x': center_x - 150,
                            'y': center_y - 150, 
                            'width': 300,
                            'height': 300
                        }
                    )
                    
                    import base64
                    qrcode_base64 = base64.b64encode(screenshot_bytes).decode('utf-8')
                    logger.info("截取页面中心区域作为二维码")
                    return qrcode_base64
                
                logger.error("无法获取二维码")
                return None
                
        except Exception as e:
            logger.error(f"截取二维码失败: {e}")
            return None
    
    async def _switch_to_qrcode_mode(self):
        """切换到二维码登录模式"""
        try:
            logger.info("开始切换到二维码登录模式")
            
            # 等待页面稳定
            await self.page.wait_for_timeout(1000)
            
            # 可能的二维码登录切换按钮（更全面的列表）
            qrcode_switch_selectors = [
                # 文本选择器
                "text=二维码登录",
                "text=扫码登录", 
                "text=扫一扫登录",
                "text=微信登录",
                "text=APP扫码登录",
                # 类名选择器
                ".qr-login-tab",
                ".qrcode-tab",
                ".scan-login",
                ".wechat-login",
                # 属性选择器
                "[data-testid='qrcode-tab']",
                "[data-testid='qr-tab']",
                "[data-testid='scan-tab']",
                # 通用选择器
                ".login-tab:nth-child(1)",
                ".login-tab:first-child",
                ".tab:first-child",
                "[class*='qr']",
                "[class*='scan']"
            ]
            
            # 记录当前页面的所有按钮和标签
            buttons = await self.page.query_selector_all("button, .tab, .login-tab, [role='tab']")
            logger.info(f"页面上找到 {len(buttons)} 个按钮/标签元素")
            
            for i, button in enumerate(buttons[:10]):  # 只检查前10个
                try:
                    text_content = await button.text_content()
                    class_name = await button.evaluate("el => el.className")
                    logger.info(f"按钮 {i}: 文本='{text_content}', class='{class_name}'")
                except:
                    pass
            
            # 尝试点击二维码切换按钮
            for selector in qrcode_switch_selectors:
                try:
                    logger.info(f"尝试切换选择器: {selector}")
                    element = await self.page.query_selector(selector)
                    if element:
                        is_visible = await element.is_visible()
                        logger.info(f"找到切换元素 {selector}, 可见性: {is_visible}")
                        
                        if is_visible:
                            await element.click()
                            logger.info(f"成功点击切换按钮: {selector}")
                            await self.page.wait_for_timeout(1000)
                            return
                except Exception as e:
                    logger.debug(f"切换选择器 {selector} 失败: {e}")
                    continue
            
            logger.info("未找到明确的二维码切换按钮，检查是否已经在二维码模式")
            
            # 检查是否已经有二维码元素存在
            existing_qr = await self.page.query_selector("canvas, .qr-code, .qrcode, [class*='qr']")
            if existing_qr:
                logger.info("页面上已存在二维码相关元素，可能已经在二维码模式")
            else:
                logger.warning("页面上没有找到二维码相关元素")
                        
        except Exception as e:
            logger.error(f"切换到二维码登录模式失败: {e}")
    
    async def switch_to_phone_login(self):
        """切换到手机号登录模式"""
        try:
            # 可能的手机号登录切换按钮
            phone_switch_selectors = [
                "text=手机号登录",
                "text=密码登录",
                ".phone-login-tab",
                "[data-testid='phone-tab']",
                ".login-tab:nth-child(2)"
            ]
            
            for selector in phone_switch_selectors:
                try:
                    element = await self.page.query_selector(selector)
                    if element:
                        await element.click()
                        logger.info(f"切换到手机号登录模式: {selector}")
                        await self.page.wait_for_timeout(1000)
                        return
                except:
                    continue
                    
        except Exception as e:
            logger.error(f"切换到手机号登录模式失败: {e}")
    
    async def fill_phone_number(self, phone: str):
        """填入手机号"""
        try:
            # 手机号输入框的可能选择器
            phone_input_selectors = [
                "input[placeholder*='手机号']",
                "input[placeholder*='手机']",
                "input[type='tel']",
                ".phone-input input",
                "[data-testid='phone-input']",
                "input[name='phone']"
            ]
            
            for selector in phone_input_selectors:
                try:
                    input_element = await self.page.query_selector(selector)
                    if input_element:
                        # 清空输入框
                        await input_element.click()
                        await self.page.keyboard.press("Control+A")
                        await self.page.keyboard.press("Delete")
                        
                        # 输入手机号
                        await input_element.type(phone, delay=100)
                        logger.info(f"成功填入手机号: {selector}")
                        return
                except:
                    continue
            
            raise Exception("未找到手机号输入框")
            
        except Exception as e:
            logger.error(f"填入手机号失败: {e}")
            raise
    
    async def send_verification_code(self):
        """发送验证码"""
        try:
            # 发送验证码按钮的可能选择器
            send_code_selectors = [
                "text=发送验证码",
                "text=获取验证码",
                ".send-code-btn",
                "[data-testid='send-code-btn']",
                "button[type='button']:has-text('验证码')"
            ]
            
            for selector in send_code_selectors:
                try:
                    button = await self.page.query_selector(selector)
                    if button:
                        await button.click()
                        logger.info(f"成功点击发送验证码按钮: {selector}")
                        await self.page.wait_for_timeout(1000)
                        return
                except:
                    continue
            
            raise Exception("未找到发送验证码按钮")
            
        except Exception as e:
            logger.error(f"发送验证码失败: {e}")
            raise
    
    async def fill_verification_code(self, code: str):
        """填入验证码"""
        try:
            # 验证码输入框的可能选择器
            code_input_selectors = [
                "input[placeholder*='验证码']",
                "input[placeholder*='验证']",
                ".verification-code-input input",
                "[data-testid='verification-code-input']",
                "input[name='verificationCode']",
                "input[maxlength='6']"
            ]
            
            for selector in code_input_selectors:
                try:
                    input_element = await self.page.query_selector(selector)
                    if input_element:
                        # 清空输入框
                        await input_element.click()
                        await self.page.keyboard.press("Control+A")
                        await self.page.keyboard.press("Delete")
                        
                        # 输入验证码
                        await input_element.type(code, delay=100)
                        logger.info(f"成功填入验证码: {selector}")
                        return
                except:
                    continue
            
            raise Exception("未找到验证码输入框")
            
        except Exception as e:
            logger.error(f"填入验证码失败: {e}")
            raise
    
    async def submit_login(self):
        """提交登录"""
        try:
            # 登录提交按钮的可能选择器
            login_button_selectors = [
                "text=登录",
                "button[type='submit']",
                ".login-submit-btn",
                "[data-testid='login-submit']",
                "button:has-text('登录')"
            ]
            
            for selector in login_button_selectors:
                try:
                    button = await self.page.query_selector(selector)
                    if button:
                        await button.click()
                        logger.info(f"成功点击登录按钮: {selector}")
                        return
                except:
                    continue
            
            raise Exception("未找到登录按钮")
            
        except Exception as e:
            logger.error(f"提交登录失败: {e}")
            raise
    
    async def wait_for_login_success(self, timeout: int = 30) -> bool:
        """等待登录成功"""
        try:
            start_time = time.time()
            
            while time.time() - start_time < timeout:
                # 检查URL是否变化到已登录状态
                current_url = self.page.url
                if '/explore' in current_url and '/signin' not in current_url:
                    logger.info("检测到URL变化，登录成功")
                    return True
                
                # 检查是否有用户头像或用户名出现
                user_indicators = [
                    ".user-avatar",
                    ".username", 
                    ".user-info",
                    "[data-testid='user-avatar']",
                    ".avatar",
                    ".profile-icon"
                ]
                
                for selector in user_indicators:
                    try:
                        element = await self.page.query_selector(selector)
                        if element and await element.is_visible():
                            logger.info(f"检测到用户元素，登录成功: {selector}")
                            return True
                    except:
                        continue
                
                # 检查登录对话框是否消失
                login_dialog_selectors = [
                    ".login-dialog",
                    ".signin-dialog",
                    ".auth-modal",
                    "[data-testid='login-modal']"
                ]
                
                dialog_exists = False
                for selector in login_dialog_selectors:
                    try:
                        element = await self.page.query_selector(selector)
                        if element and await element.is_visible():
                            dialog_exists = True
                            break
                    except:
                        continue
                
                # 如果原来有登录对话框但现在消失了，可能表示登录成功
                if not dialog_exists and '/signin' not in current_url:
                    # 进一步验证是否真的登录成功
                    await self.page.wait_for_timeout(1000)  # 等待页面稳定
                    if '/explore' in self.page.url or '/user' in self.page.url:
                        logger.info("检测到登录对话框消失且URL正常，登录成功")
                        return True
                
                # 检查是否有错误提示
                error_selectors = [
                    ".error-message",
                    ".login-error",
                    "text=验证码错误",
                    "text=手机号错误",
                    "text=登录失败"
                ]
                
                for selector in error_selectors:
                    try:
                        error_element = await self.page.query_selector(selector)
                        if error_element and await error_element.is_visible():
                            error_text = await error_element.text_content()
                            logger.warning(f"登录错误: {error_text}")
                            return False
                    except:
                        continue
                
                await asyncio.sleep(1)
            
            logger.warning("等待登录成功超时")
            return False
            
        except Exception as e:
            logger.error(f"等待登录成功失败: {e}")
            return False
    
    async def _check_async_condition(self, condition_func) -> bool:
        """检查异步条件（已弃用，保留以防兼容性问题）"""
        return False
    
    async def check_qrcode_status(self) -> str:
        """检查二维码扫描状态"""
        try:
            # 检查是否已扫描
            scanned_indicators = [
                ".qr-scanned",
                "text=已扫描",
                "text=请在手机上确认"
            ]
            
            for selector in scanned_indicators:
                try:
                    element = await self.page.query_selector(selector)
                    if element:
                        return "scanned"
                except:
                    continue
            
            # 检查是否过期
            expired_indicators = [
                ".qr-expired",
                "text=二维码已过期",
                "text=已过期"
            ]
            
            for selector in expired_indicators:
                try:
                    element = await self.page.query_selector(selector)
                    if element:
                        return "expired"
                except:
                    continue
            
            return "waiting"
            
        except Exception as e:
            logger.error(f"检查二维码状态失败: {e}")
            return "error"
    
    async def refresh_qrcode(self) -> Optional[str]:
        """刷新二维码"""
        try:
            # 刷新按钮的可能选择器
            refresh_selectors = [
                ".qr-refresh",
                "text=刷新",
                "[data-testid='refresh-qr']"
            ]
            
            for selector in refresh_selectors:
                try:
                    button = await self.page.query_selector(selector)
                    if button:
                        await button.click()
                        await self.page.wait_for_timeout(1000)
                        return await self.capture_qrcode()
                except:
                    continue
            
            # 如果没有刷新按钮，重新加载页面
            await self.page.reload()
            await self.page.wait_for_timeout(2000)
            return await self.capture_qrcode()
            
        except Exception as e:
            logger.error(f"刷新二维码失败: {e}")
            return None 