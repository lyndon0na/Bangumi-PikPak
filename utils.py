"""工具函数模块

提供重试机制、日志配置等通用功能。
"""

import asyncio
import functools
import logging
import sys
import time
from logging.handlers import RotatingFileHandler
from typing import Callable, Optional, Type, Tuple

logger = logging.getLogger(__name__)


def async_retry(
    max_retries: int = 3,
    initial_delay: float = 1.0,
    exponential_base: float = 2.0,
    exceptions: Tuple[Type[Exception], ...] = (Exception,),
    on_retry: Optional[Callable] = None,
):
    """异步函数重试装饰器

    Args:
        max_retries: 最大重试次数
        initial_delay: 初始延迟时间（秒）
        exponential_base: 指数退避基数
        exceptions: 需要重试的异常类型
        on_retry: 重试时的回调函数

    Returns:
        装饰器函数

    Example:
        @async_retry(max_retries=3, initial_delay=1.0)
        async def fetch_data():
            async with httpx.AsyncClient() as client:
                response = await client.get('https://api.example.com/data')
                return response.json()
    """

    def decorator(func: Callable):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            last_exception = None

            for attempt in range(max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e

                    if attempt == max_retries:
                        logger.error(
                            f"{func.__name__} 失败，已达到最大重试次数 ({max_retries}): {e}"
                        )
                        raise

                    delay = initial_delay * (exponential_base**attempt)
                    logger.warning(
                        f"{func.__name__} 失败 (尝试 {attempt + 1}/{max_retries + 1}): {e}, "
                        f"{delay:.1f} 秒后重试..."
                    )

                    if on_retry:
                        await on_retry(attempt, e) if asyncio.iscoroutinefunction(
                            on_retry
                        ) else on_retry(attempt, e)

                    await asyncio.sleep(delay)

            raise last_exception

        return wrapper

    return decorator


def sync_retry(
    max_retries: int = 3,
    initial_delay: float = 1.0,
    exponential_base: float = 2.0,
    exceptions: Tuple[Type[Exception], ...] = (Exception,),
    on_retry: Optional[Callable] = None,
):
    """同步函数重试装饰器

    Args:
        max_retries: 最大重试次数
        initial_delay: 初始延迟时间（秒）
        exponential_base: 指数退避基数
        exceptions: 需要重试的异常类型
        on_retry: 重试时的回调函数

    Returns:
        装饰器函数
    """

    def decorator(func: Callable):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None

            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e

                    if attempt == max_retries:
                        logger.error(
                            f"{func.__name__} 失败，已达到最大重试次数 ({max_retries}): {e}"
                        )
                        raise

                    delay = initial_delay * (exponential_base**attempt)
                    logger.warning(
                        f"{func.__name__} 失败 (尝试 {attempt + 1}/{max_retries + 1}): {e}, "
                        f"{delay:.1f} 秒后重试..."
                    )

                    if on_retry:
                        on_retry(attempt, e)

                    time.sleep(delay)

            raise last_exception

        return wrapper

    return decorator


class SensitiveDataFilter(logging.Filter):
    """敏感数据过滤器

    自动脱敏日志中的敏感信息，如密码、token 等。
    """

    SENSITIVE_KEYWORDS = [
        "password",
        "token",
        "secret",
        "key",
        "credential",
        "auth",
    ]

    def filter(self, record: logging.LogRecord) -> bool:
        """过滤日志记录

        Args:
            record: 日志记录

        Returns:
            是否保留该记录（总是返回 True，但会修改消息）
        """
        # 脱敏处理
        msg = str(record.msg)

        for keyword in self.SENSITIVE_KEYWORDS:
            # 匹配模式：keyword=value 或 keyword: value
            patterns = [
                f"{keyword}=([^\\s,;]+)",
                f"{keyword}: ([^\\s,;]+)",
                f"{keyword}\\s*=\\s*([^\\s,;]+)",
                f"{keyword}\\s*:\\s*([^\\s,;]+)",
            ]

            for pattern in patterns:
                import re

                msg = re.sub(
                    pattern,
                    f"{keyword}={mask_sensitive_data('PLACEHOLDER')}",
                    msg,
                    flags=re.IGNORECASE,
                )

        record.msg = msg
        return True


class JSONFormatter(logging.Formatter):
    """JSON 格式日志格式器

    输出结构化的 JSON 日志，便于日志分析工具处理。
    """

    def format(self, record: logging.LogRecord) -> str:
        """格式化日志记录为 JSON

        Args:
            record: 日志记录

        Returns:
            JSON 格式的日志字符串
        """
        import json
        from datetime import datetime

        log_obj = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # 添加异常信息
        if record.exc_info:
            log_obj["exception"] = self.formatException(record.exc_info)

        # 添加额外字段
        if hasattr(record, "bangumi_title"):
            log_obj["bangumi_title"] = record.bangumi_title

        return json.dumps(log_obj, ensure_ascii=False)


def setup_logging(
    log_file: str = "rss-pikpak.log",
    log_level: str = "INFO",
    max_bytes: int = 10 * 1024 * 1024,
    backup_count: int = 5,
    enable_sensitive_filter: bool = True,
    json_format: bool = False,
) -> logging.Logger:
    """配置日志系统

    Args:
        log_file: 日志文件路径
        log_level: 日志级别 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        max_bytes: 单个日志文件最大大小
        backup_count: 保留的日志文件数量
        enable_sensitive_filter: 是否启用敏感信息脱敏
        json_format: 是否使用 JSON 格式日志

    Returns:
        配置好的 Logger 对象
    """
    try:
        level = getattr(logging, log_level.upper(), logging.INFO)

        logger = logging.getLogger()
        logger.setLevel(level)

        if logger.handlers:
            logger.handlers.clear()

        # 选择格式器
        if json_format:
            formatter = JSONFormatter()
        else:
            formatter = logging.Formatter(
                fmt="%(asctime)s [%(levelname)s] %(name)s:%(lineno)d - %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )

        # 文件处理器
        file_handler = RotatingFileHandler(
            filename=log_file,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding="utf-8",
        )
        file_handler.setFormatter(formatter)

        # 启用敏感信息过滤器
        if enable_sensitive_filter:
            file_handler.addFilter(SensitiveDataFilter())

        logger.addHandler(file_handler)

        # 控制台处理器（不脱敏，便于调试）
        console_formatter = logging.Formatter(
            fmt="%(asctime)s [%(levelname)s] %(name)s:%(lineno)d - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)

        logger.info(f"日志系统初始化成功 (级别: {log_level}, JSON: {json_format})")
        return logger

    except Exception as e:
        print(f"日志系统初始化失败: {e}", file=sys.stderr)
        sys.exit(1)


def mask_sensitive_data(data: str, show_length: int = 3) -> str:
    """脱敏敏感数据

    Args:
        data: 需要脱敏的数据
        show_length: 显示的字符数量

    Returns:
        脱敏后的数据

    Example:
        mask_sensitive_data("password123") -> "pas********"
    """
    if not data or len(data) <= show_length:
        return "*" * len(data) if data else ""

    return data[:show_length] + "*" * (len(data) - show_length)


def sanitize_filename(filename: str) -> str:
    """清理文件名，移除非法字符

    Args:
        filename: 原始文件名

    Returns:
        清理后的文件名
    """
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, "_")
    return filename.strip()


def ensure_directory(path: str) -> None:
    """确保目录存在，不存在则创建

    Args:
        path: 目录路径
    """
    import os

    os.makedirs(path, exist_ok=True)
