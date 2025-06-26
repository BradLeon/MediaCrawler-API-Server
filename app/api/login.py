"""
登录API端点

提供爬虫登录相关的API接口：
1. 创建登录会话
2. 获取登录状态（包括二维码）
3. 提交登录输入（手机号、验证码）
4. 登录状态查询
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks, WebSocket
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
import asyncio
import time

from app.core.login_manager import (
    login_manager, LoginType, LoginStatus, LoginRequest, 
    LoginResponse, LoginInput
)
from app.core.logging import get_app_logger
from app.crawler.adapter import crawler_adapter

logger = get_app_logger(__name__)
router = APIRouter(prefix="/api/v1/login", tags=["登录管理"])


class CreateLoginSessionRequest(BaseModel):
    """创建登录会话请求"""
    task_id: str = Field(..., description="任务ID")
    platform: str = Field(..., description="平台名称", examples=["xhs", "douyin", "bilibili"])
    login_type: str = Field(..., description="登录类型", examples=["qrcode", "phone", "cookie"])
    timeout: int = Field(300, description="登录超时时间（秒）")
    cookies: Optional[str] = Field(None, description="Cookie字符串（cookie登录时使用）")


class CreateLoginSessionResponse(BaseModel):
    """创建登录会话响应"""
    success: bool
    message: str
    task_id: str
    session_created: bool = False


class SubmitLoginInputRequest(BaseModel):
    """提交登录输入请求"""
    task_id: str = Field(..., description="任务ID")
    input_type: str = Field(..., description="输入类型", examples=["phone", "verification_code"])
    value: str = Field(..., description="输入值")


class SaveCookiesRequest(BaseModel):
    """保存Cookies请求"""
    task_id: str = Field(..., description="任务ID")
    cookies: str = Field(..., description="登录成功后的Cookies字符串")
    platform: str = Field(..., description="平台名称")


class LoginStatusResponse(BaseModel):
    """登录状态响应"""
    success: bool
    task_id: str
    status: str
    message: str
    data: Optional[Dict[str, Any]] = None
    qrcode_image: Optional[str] = Field(None, description="二维码图片（base64编码）")
    input_required: Optional[Dict[str, str]] = Field(None, description="需要的输入信息")


@router.post("/create-session", response_model=CreateLoginSessionResponse)
async def create_login_session(request: CreateLoginSessionRequest):
    """
    创建登录会话
    
    为指定的爬虫任务创建登录会话，支持三种登录方式：
    - qrcode: 二维码登录
    - phone: 手机号+验证码登录  
    - cookie: Cookie登录
    """
    try:
        # 验证登录类型
        try:
            login_type = LoginType(request.login_type)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"不支持的登录类型: {request.login_type}，支持的类型: qrcode, phone, cookie"
            )
        
        # 检查任务ID是否已存在登录会话
        existing_session = login_manager.get_login_session(request.task_id)
        if existing_session:
            return CreateLoginSessionResponse(
                success=False,
                message=f"任务 {request.task_id} 已存在登录会话",
                task_id=request.task_id,
                session_created=False
            )
        
        # 创建登录会话
        session = login_manager.create_login_session(
            task_id=request.task_id,
            platform=request.platform,
            login_type=login_type,
            timeout=request.timeout
        )
        
        # 如果是Cookie登录，保存Cookie信息
        if login_type == LoginType.COOKIE and request.cookies:
            session.data['cookies'] = request.cookies
        
        logger.info(f"创建登录会话成功: {request.task_id}, 平台: {request.platform}, 类型: {request.login_type}")
        
        return CreateLoginSessionResponse(
            success=True,
            message="登录会话创建成功",
            task_id=request.task_id,
            session_created=True
        )
        
    except Exception as e:
        logger.error(f"创建登录会话失败: {e}")
        raise HTTPException(status_code=500, detail=f"创建登录会话失败: {str(e)}")


@router.post("/start/{task_id}", response_model=LoginStatusResponse)
async def start_login_process(task_id: str, background_tasks: BackgroundTasks):
    """
    启动登录流程
    
    开始执行登录流程，根据登录类型执行不同的操作：
    - 二维码登录：打开登录页面，截取二维码返回给客户端
    - 手机号登录：打开登录页面，等待客户端输入手机号
    - Cookie登录：直接使用Cookie进行登录
    """
    try:
        session = login_manager.get_login_session(task_id)
        if not session:
            raise HTTPException(status_code=404, detail=f"登录会话不存在: {task_id}")
        
        # 启动登录流程 - 使用全局的crawler_adapter
        background_tasks.add_task(_start_login_background, task_id, session.platform)
        
        return LoginStatusResponse(
            success=True,
            task_id=task_id,
            status=session.status.value,
            message="登录流程已启动"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"启动登录流程失败: {e}")
        raise HTTPException(status_code=500, detail=f"启动登录流程失败: {str(e)}")


@router.get("/status/{task_id}", response_model=LoginStatusResponse)
async def get_login_status(task_id: str):
    """
    获取登录状态
    
    查询指定任务的登录状态，包括：
    - 当前登录阶段
    - 二维码图片（如果有）
    - 需要的输入信息（如果有）
    - 错误信息（如果有）
    """
    try:
        response = await login_manager.get_login_status(task_id)
        
        return LoginStatusResponse(
            success=response.status != LoginStatus.FAILED,
            task_id=response.task_id,
            status=response.status.value,
            message=response.message,
            data=response.data,
            qrcode_image=response.qrcode_image,
            input_required=response.input_required
        )
        
    except Exception as e:
        logger.error(f"获取登录状态失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取登录状态失败: {str(e)}")


@router.post("/input/{task_id}", response_model=LoginStatusResponse)
async def submit_login_input(task_id: str, request: SubmitLoginInputRequest):
    """
    提交登录输入
    
    向登录流程提交用户输入，支持：
    - phone: 手机号
    - verification_code: 验证码
    """
    try:
        if request.task_id != task_id:
            raise HTTPException(status_code=400, detail="请求中的task_id与路径参数不匹配")
        
        # 创建登录输入对象
        login_input = LoginInput(
            task_id=task_id,
            input_type=request.input_type,
            value=request.value
        )
        
        # 处理登录输入
        response = await login_manager.handle_login_input(task_id, login_input)
        
        return LoginStatusResponse(
            success=response.status not in [LoginStatus.FAILED, LoginStatus.TIMEOUT],
            task_id=response.task_id,
            status=response.status.value,
            message=response.message,
            data=response.data,
            qrcode_image=response.qrcode_image,
            input_required=response.input_required
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"提交登录输入失败: {e}")
        raise HTTPException(status_code=500, detail=f"提交登录输入失败: {str(e)}")


@router.delete("/session/{task_id}")
async def delete_login_session(task_id: str):
    """
    删除登录会话
    
    清理指定任务的登录会话，释放相关资源
    """
    try:
        session = login_manager.get_login_session(task_id)
        if not session:
            raise HTTPException(status_code=404, detail=f"登录会话不存在: {task_id}")
        
        # 清理资源
        if session.page:
            try:
                await session.page.close()
            except:
                pass
        
        # 移除会话
        await login_manager.remove_login_session(task_id)
        
        logger.info(f"删除登录会话: {task_id}")
        
        return {"success": True, "message": f"登录会话已删除: {task_id}"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除登录会话失败: {e}")
        raise HTTPException(status_code=500, detail=f"删除登录会话失败: {str(e)}")


@router.post("/refresh-qrcode/{task_id}")
async def refresh_qrcode(task_id: str):
    """
    刷新二维码
    
    重新生成二维码，用于二维码过期的情况
    """
    try:
        session = login_manager.get_login_session(task_id)
        if not session:
            raise HTTPException(status_code=404, detail=f"登录会话不存在: {task_id}")
        
        if session.login_type != LoginType.QRCODE:
            raise HTTPException(status_code=400, detail="只有二维码登录支持刷新二维码")
        
        # 这里需要根据具体平台实现刷新逻辑
        # 暂时返回当前状态
        response = await login_manager.get_login_status(task_id)
        
        return LoginStatusResponse(
            success=True,
            task_id=response.task_id,
            status=response.status.value,
            message="二维码刷新请求已提交",
            data=response.data,
            qrcode_image=response.qrcode_image
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"刷新二维码失败: {e}")
        raise HTTPException(status_code=500, detail=f"刷新二维码失败: {str(e)}")


@router.post("/save-cookies")
async def save_login_cookies(request: SaveCookiesRequest):
    """
    保存登录成功的Cookies
    
    客户端在浏览器中完成登录后，调用此接口将cookies传递给服务器，
    服务器会将cookies保存并用于后续的MediaCrawler任务执行。
    """
    try:
        # 验证登录会话是否存在
        session = login_manager.get_login_session(request.task_id)
        if not session:
            raise HTTPException(status_code=404, detail=f"登录会话不存在: {request.task_id}")
        
        # 验证平台是否匹配
        if session.platform != request.platform:
            raise HTTPException(
                status_code=400, 
                detail=f"平台不匹配: 会话平台={session.platform}, 请求平台={request.platform}"
            )
        
        # 保存cookies
        success = await login_manager.save_login_cookies(request.task_id, request.cookies)
        if not success:
            raise HTTPException(status_code=500, detail="保存cookies失败")
        
        # 同步cookies到MediaCrawler配置
        await login_manager.sync_cookies_to_mediacrawler(request.task_id, request.platform)
        
        logger.info(f"Cookies保存成功: {request.task_id}, 平台: {request.platform}")
        
        return {
            "success": True,
            "message": "Cookies保存成功",
            "task_id": request.task_id,
            "platform": request.platform
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"保存cookies失败: {e}")
        raise HTTPException(status_code=500, detail=f"保存cookies失败: {str(e)}")


@router.get("/cookies/{task_id}")
async def get_login_cookies(task_id: str):
    """
    获取已保存的登录Cookies
    
    用于检查指定任务的cookies是否已保存成功
    """
    try:
        session = login_manager.get_login_session(task_id)
        if not session:
            raise HTTPException(status_code=404, detail=f"登录会话不存在: {task_id}")
        
        cookies = await login_manager.get_login_cookies(task_id)
        
        return {
            "task_id": task_id,
            "platform": session.platform,
            "has_cookies": cookies is not None,
            "cookies_length": len(cookies) if cookies else 0,
            "status": session.status.value
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取cookies失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取cookies失败: {str(e)}")


async def _start_login_background(task_id: str, platform: str):
    """后台启动登录流程"""
    try:
        # 使用全局crawler_adapter处理登录
        await login_manager.start_login_process(task_id, crawler_adapter)
    except Exception as e:
        logger.error(f"后台登录流程出错: {e}")
        session = login_manager.get_login_session(task_id)
        if session:
            session.update_status(LoginStatus.FAILED, f"登录流程出错: {str(e)}")


# WebSocket支持（可选）
@router.websocket("/ws/{task_id}")
async def websocket_login_status(websocket: WebSocket, task_id: str):
    """
    WebSocket登录状态推送
    
    为客户端提供实时的登录状态更新
    """
    await websocket.accept()
    
    try:
        while True:
            # 获取当前登录状态
            session = login_manager.get_login_session(task_id)
            if not session:
                await websocket.send_json({
                    "error": "登录会话不存在",
                    "task_id": task_id
                })
                break
            
            # 发送状态更新
            status_data = {
                "task_id": task_id,
                "status": session.status.value,
                "message": f"当前状态: {session.status.value}",
                "timestamp": int(time.time())
            }
            
            # 如果有二维码，添加到数据中
            if session.status == LoginStatus.QRCODE_GENERATED and 'qrcode_image' in session.data:
                status_data['qrcode_image'] = session.data['qrcode_image']
            
            await websocket.send_json(status_data)
            
            # 如果登录完成或失败，结束连接
            if session.status in [LoginStatus.SUCCESS, LoginStatus.FAILED, LoginStatus.TIMEOUT]:
                break
            
            await asyncio.sleep(2)  # 每2秒推送一次状态
            
    except Exception as e:
        logger.error(f"WebSocket连接出错: {e}")
    finally:
        await websocket.close() 