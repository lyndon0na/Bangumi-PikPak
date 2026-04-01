"""Web API 模块

提供Web界面和RESTful API。
"""

import os
import logging
import secrets
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, Request, Form, HTTPException, Depends, status
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from jose import JWTError, jwt
from passlib.context import CryptContext
from jinja2 import Environment, FileSystemLoader

from config import Config
from state_manager import StateManager

logger = logging.getLogger(__name__)

SCRIPT_DIR = Path(__file__).parent.absolute()
TEMPLATES_DIR = SCRIPT_DIR / "templates"
STATIC_DIR = SCRIPT_DIR / "static"

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBasic()

app = FastAPI(title="Bangumi-PikPak Web UI")

if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

template_env = Environment(
    loader=FileSystemLoader(str(TEMPLATES_DIR)), auto_reload=True
)
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))
templates.env = template_env

SECRET_KEY = None
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1440

_downloader_instance = None
_config_instance = None
_state_manager = None


def init_web(config: Config, downloader, state_manager: StateManager):
    """初始化Web服务

    Args:
        config: 配置对象
        downloader: BangumiDownloader实例
        state_manager: 状态管理器
    """
    global _config_instance, _downloader_instance, _state_manager, SECRET_KEY

    _config_instance = config
    _downloader_instance = downloader
    _state_manager = state_manager

    if config.web_secret_key:
        SECRET_KEY = config.web_secret_key
    else:
        SECRET_KEY = secrets.token_urlsafe(32)

    logger.info(f"Web服务初始化完成, 端口: {config.web_port}")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """生成密码哈希"""
    return pwd_context.hash(password)


def create_access_token(data: dict) -> str:
    """创建访问令牌"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> Optional[str]:
    """验证令牌"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            return None
        return username
    except JWTError:
        return None


async def get_current_user(request: Request) -> Optional[str]:
    """获取当前用户"""
    token = request.cookies.get("access_token")
    if not token:
        return None
    return verify_token(token)


async def require_auth(request: Request):
    """要求认证"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_302_FOUND, headers={"Location": "/login"}
        )
    return user


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """根路径重定向到仪表盘"""
    return RedirectResponse(url="/dashboard")


@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """登录页面"""
    return templates.TemplateResponse("login.html", {"request": request})


@app.post("/login")
async def login(request: Request, password: str = Form(...)):
    """处理登录"""
    if not _config_instance:
        raise HTTPException(status_code=500, detail="服务未初始化")

    if password != _config_instance.web_password:
        return templates.TemplateResponse(
            "login.html", {"request": request, "error": "密码错误"}
        )

    access_token = create_access_token(data={"sub": "admin"})

    response = RedirectResponse(url="/dashboard", status_code=303)
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )

    return response


@app.get("/logout")
async def logout():
    """登出"""
    response = RedirectResponse(url="/login")
    response.delete_cookie("access_token")
    return response


@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request, user: str = Depends(require_auth)):
    """仪表盘页面"""
    if not _downloader_instance or not _state_manager:
        raise HTTPException(status_code=500, detail="服务未初始化")

    stats = _state_manager.get_stats()
    recent_updates = _state_manager.get_updates(limit=10)
    bangumi_list = _state_manager.get_bangumi_list()

    uptime = datetime.now() - datetime.fromtimestamp(_downloader_instance.start_time)

    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "stats": stats,
            "recent_updates": recent_updates,
            "bangumi_list": bangumi_list,
            "uptime": str(uptime).split(".")[0],
            "error_count": _downloader_instance.error_count,
            "config": _config_instance,
        },
    )


@app.get("/logs", response_class=HTMLResponse)
async def logs_page(request: Request, user: str = Depends(require_auth)):
    """日志页面"""
    return templates.TemplateResponse("logs.html", {"request": request})


@app.get("/config", response_class=HTMLResponse)
async def config_page(request: Request, user: str = Depends(require_auth)):
    """配置页面"""
    if not _config_instance:
        raise HTTPException(status_code=500, detail="服务未初始化")

    return templates.TemplateResponse(
        "config.html", {"request": request, "config": _config_instance}
    )


@app.get("/api/status")
async def api_status(user: str = Depends(require_auth)):
    """获取状态API"""
    if not _downloader_instance or not _state_manager:
        raise HTTPException(status_code=500, detail="服务未初始化")

    stats = _state_manager.get_stats()
    uptime = datetime.now() - datetime.fromtimestamp(_downloader_instance.start_time)

    return {
        "running": True,
        "uptime_seconds": int(uptime.total_seconds()),
        "uptime_human": str(uptime).split(".")[0],
        "error_count": _downloader_instance.error_count,
        "total_processed": stats.total_processed,
        "success_count": stats.success_count,
        "failed_count": stats.failed_count,
        "last_check": stats.last_check,
        "start_time": stats.start_time,
    }


@app.get("/api/updates")
async def api_updates(
    limit: Optional[int] = None,
    bangumi_title: Optional[str] = None,
    status: Optional[str] = None,
    user: str = Depends(require_auth),
):
    """获取更新记录API"""
    if not _state_manager:
        raise HTTPException(status_code=500, detail="服务未初始化")

    updates = _state_manager.get_updates(
        limit=limit, bangumi_title=bangumi_title, status=status
    )

    return {"updates": updates}


@app.get("/api/bangumi")
async def api_bangumi(user: str = Depends(require_auth)):
    """获取番剧列表API"""
    if not _state_manager:
        raise HTTPException(status_code=500, detail="服务未初始化")

    return {"bangumi_list": _state_manager.get_bangumi_list()}


@app.get("/api/logs")
async def api_logs(
    lines: int = 100, level: Optional[str] = None, user: str = Depends(require_auth)
):
    """获取日志API"""
    log_file = SCRIPT_DIR / "rss-pikpak.log"

    if not log_file.exists():
        return {"logs": [], "message": "日志文件不存在"}

    try:
        with open(log_file, "r", encoding="utf-8") as f:
            all_lines = f.readlines()[-lines:]

        if level:
            all_lines = [l for l in all_lines if level.upper() in l]

        return {"logs": [l.strip() for l in all_lines]}
    except Exception as e:
        logger.error(f"读取日志失败: {e}")
        raise HTTPException(status_code=500, detail="读取日志失败")


@app.get("/api/config")
async def api_get_config(user: str = Depends(require_auth)):
    """获取配置API(脱敏)"""
    if not _config_instance:
        raise HTTPException(status_code=500, detail="服务未初始化")

    config_dict = {
        "username": _config_instance.username,
        "password": "***",
        "path": _config_instance.path,
        "rss": "***" if _config_instance.rss else "",
        "http_proxy": _config_instance.http_proxy,
        "https_proxy": _config_instance.https_proxy,
        "socks_proxy": _config_instance.socks_proxy,
        "enable_proxy": _config_instance.enable_proxy,
        "ntfy_url": "***" if _config_instance.ntfy_url else "",
        "enable_notifications": _config_instance.enable_notifications,
        "rss_check_interval": _config_instance.rss_check_interval,
        "token_refresh_interval": _config_instance.token_refresh_interval,
        "max_retries": _config_instance.max_retries,
        "request_timeout": _config_instance.request_timeout,
        "log_level": _config_instance.log_level,
        "web_enabled": _config_instance.web_enabled,
        "web_host": _config_instance.web_host,
        "web_port": _config_instance.web_port,
        "enable_health_check": _config_instance.enable_health_check,
        "health_check_interval": _config_instance.health_check_interval,
        "enable_error_alert": _config_instance.enable_error_alert,
        "error_alert_threshold": _config_instance.error_alert_threshold,
    }

    return config_dict


@app.post("/api/config")
async def api_update_config(request: Request, user: str = Depends(require_auth)):
    """更新配置API"""
    if not _config_instance:
        raise HTTPException(status_code=500, detail="服务未初始化")

    try:
        data = await request.json()

        for key, value in data.items():
            if hasattr(_config_instance, key):
                if key in ["password", "rss", "ntfy_url", "web_password"]:
                    if value and value != "***":
                        setattr(_config_instance, key, value)
                elif key not in ["username", "path"]:
                    setattr(_config_instance, key, value)

        from config import save_config

        config_file = SCRIPT_DIR / "config.json"
        save_config(_config_instance, str(config_file))

        return {"success": True, "message": "配置已更新,部分配置需要重启服务生效"}

    except Exception as e:
        logger.error(f"更新配置失败: {e}")
        raise HTTPException(status_code=500, detail=f"更新配置失败: {e}")


@app.post("/api/service/restart")
async def api_restart_service(user: str = Depends(require_auth)):
    """重启服务API (用户级 systemd)"""
    import subprocess

    try:
        result = subprocess.run(
            ["systemctl", "--user", "restart", "bangumi-pikpak"],
            check=True,
            capture_output=True,
            text=True,
        )
        return {"success": True, "message": "服务重启命令已发送"}
    except subprocess.CalledProcessError as e:
        logger.error(f"重启服务失败: {e.stderr if e.stderr else str(e)}")
        raise HTTPException(
            status_code=500, detail=f"重启服务失败: {e.stderr if e.stderr else str(e)}"
        )
    except Exception as e:
        logger.error(f"重启服务失败: {e}")
        raise HTTPException(status_code=500, detail=f"重启服务失败: {e}")


@app.get("/api/service/status")
async def api_service_status(user: str = Depends(require_auth)):
    """获取服务状态API (用户级 systemd)"""
    import subprocess

    try:
        result = subprocess.run(
            ["systemctl", "--user", "is-active", "bangumi-pikpak"],
            capture_output=True,
            text=True,
        )

        return {
            "active": result.stdout.strip() == "active",
            "status": result.stdout.strip(),
            "level": "user",
        }
    except Exception as e:
        logger.error(f"获取服务状态失败: {e}")
        return {"active": False, "status": "unknown", "level": "user", "error": str(e)}


@app.post("/api/service/stop")
async def api_stop_service(user: str = Depends(require_auth)):
    """停止服务API (用户级 systemd)"""
    import subprocess

    try:
        result = subprocess.run(
            ["systemctl", "--user", "stop", "bangumi-pikpak"],
            check=True,
            capture_output=True,
            text=True,
        )
        return {"success": True, "message": "服务已停止"}
    except subprocess.CalledProcessError as e:
        logger.error(f"停止服务失败: {e.stderr if e.stderr else str(e)}")
        raise HTTPException(
            status_code=500, detail=f"停止服务失败: {e.stderr if e.stderr else str(e)}"
        )
    except Exception as e:
        logger.error(f"停止服务失败: {e}")
        raise HTTPException(status_code=500, detail=f"停止服务失败: {e}")


@app.post("/api/service/start")
async def api_start_service(user: str = Depends(require_auth)):
    """启动服务API (用户级 systemd)"""
    import subprocess

    try:
        result = subprocess.run(
            ["systemctl", "--user", "start", "bangumi-pikpak"],
            check=True,
            capture_output=True,
            text=True,
        )
        return {"success": True, "message": "服务已启动"}
    except subprocess.CalledProcessError as e:
        logger.error(f"启动服务失败: {e.stderr if e.stderr else str(e)}")
        raise HTTPException(
            status_code=500, detail=f"启动服务失败: {e.stderr if e.stderr else str(e)}"
        )
    except Exception as e:
        logger.error(f"启动服务失败: {e}")
        raise HTTPException(status_code=500, detail=f"启动服务失败: {e}")


@app.on_event("startup")
async def startup_event():
    """启动事件"""
    logger.info("Web API服务启动")


@app.on_event("shutdown")
async def shutdown_event():
    """关闭事件"""
    logger.info("Web API服务关闭")
