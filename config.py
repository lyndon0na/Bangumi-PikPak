"""配置管理模块

负责加载、验证和管理配置信息。
"""

import json
import os
import re
from dataclasses import dataclass, field
from typing import Optional
from urllib.parse import urlparse

import logging

logger = logging.getLogger(__name__)


@dataclass
class Config:
    """配置类

    使用 dataclass 定义配置结构，支持类型提示和默认值。
    """

    username: str = ""
    password: str = ""
    path: str = ""
    rss: str = ""

    http_proxy: str = ""
    https_proxy: str = ""
    socks_proxy: str = ""
    enable_proxy: bool = False

    ntfy_url: str = ""
    enable_notifications: bool = False

    rss_check_interval: int = 600
    token_refresh_interval: int = 21600
    max_retries: int = 3
    request_timeout: int = 30

    log_level: str = "INFO"
    log_max_bytes: int = 10 * 1024 * 1024
    log_backup_count: int = 5
    log_json_format: bool = False  # 是否使用 JSON 格式日志
    log_sensitive_filter: bool = True  # 是否脱敏敏感信息

    enable_health_check: bool = False  # 是否启用健康检查日志
    health_check_interval: int = 3600  # 健康检查间隔（秒）

    enable_error_alert: bool = False  # 是否启用错误告警
    error_alert_threshold: int = 3  # 连续错误次数阈值

    def validate(self) -> list[str]:
        """验证配置项

        Returns:
            错误消息列表，为空则表示验证通过
        """
        errors = []

        if not self.username:
            errors.append("缺少必填配置项: username")
        elif not self._is_valid_email(self.username):
            errors.append(f"username 格式无效: {self.username}")

        if not self.password:
            errors.append("缺少必填配置项: password")

        if not self.path:
            errors.append("缺少必填配置项: path (PikPak 文件夹 ID)")

        if not self.rss:
            errors.append("缺少必填配置项: rss (Mikan RSS 订阅链接)")
        elif not self._is_valid_url(self.rss):
            errors.append(f"rss URL 格式无效: {self.rss}")

        if self.enable_proxy:
            if self.http_proxy and not self._is_valid_proxy_url(
                self.http_proxy, "http"
            ):
                errors.append(f"http_proxy 格式无效: {self.http_proxy}")
            if self.https_proxy and not self._is_valid_proxy_url(
                self.https_proxy, "http"
            ):
                errors.append(f"https_proxy 格式无效: {self.https_proxy}")
            if self.socks_proxy and not self._is_valid_proxy_url(
                self.socks_proxy, "socks"
            ):
                errors.append(f"socks_proxy 格式无效: {self.socks_proxy}")

        if self.enable_notifications:
            if not self.ntfy_url:
                errors.append("启用了通知但未设置 ntfy_url")
            elif not self._is_valid_url(self.ntfy_url):
                errors.append(f"ntfy_url 格式无效: {self.ntfy_url}")

        if self.rss_check_interval < 60:
            errors.append(
                f"rss_check_interval 不能小于 60 秒: {self.rss_check_interval}"
            )

        if self.token_refresh_interval < 300:
            errors.append(
                f"token_refresh_interval 不能小于 300 秒: {self.token_refresh_interval}"
            )

        if self.max_retries < 0 or self.max_retries > 10:
            errors.append(f"max_retries 应该在 0-10 之间: {self.max_retries}")

        if self.request_timeout < 5 or self.request_timeout > 300:
            errors.append(
                f"request_timeout 应该在 5-300 秒之间: {self.request_timeout}"
            )

        valid_log_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if self.log_level.upper() not in valid_log_levels:
            errors.append(f"log_level 应该是 {valid_log_levels} 之一: {self.log_level}")

        return errors

    @staticmethod
    def _is_valid_email(email: str) -> bool:
        """验证邮箱格式"""
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        return re.match(pattern, email) is not None

    @staticmethod
    def _is_valid_url(url: str) -> bool:
        """验证 URL 格式"""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except Exception:
            return False

    @staticmethod
    def _is_valid_proxy_url(url: str, proxy_type: str) -> bool:
        """验证代理 URL 格式

        Args:
            url: 代理 URL
            proxy_type: 'http' 或 'socks'
        """
        try:
            result = urlparse(url)
            if proxy_type == "http":
                return result.scheme in ["http", "https"] and bool(result.netloc)
            elif proxy_type == "socks":
                return result.scheme in ["socks5", "socks4", "socks"] and bool(
                    result.netloc
                )
            return False
        except Exception:
            return False


def load_config(config_file: str) -> Config:
    """加载配置文件

    Args:
        config_file: 配置文件路径

    Returns:
        Config 对象

    Raises:
        FileNotFoundError: 配置文件不存在
        json.JSONDecodeError: 配置文件格式错误
        ValueError: 配置验证失败
    """
    if not os.path.exists(config_file):
        raise FileNotFoundError(f"配置文件不存在: {config_file}")

    try:
        with open(config_file, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        raise json.JSONDecodeError(f"配置文件格式错误: {e.msg}", e.doc, e.pos)

    config = Config(
        username=data.get("username", ""),
        password=data.get("password", ""),
        path=data.get("path", ""),
        rss=data.get("rss", ""),
        http_proxy=data.get("http_proxy", ""),
        https_proxy=data.get("https_proxy", ""),
        socks_proxy=data.get("socks_proxy", ""),
        enable_proxy=data.get("enable_proxy", False),
        ntfy_url=data.get("ntfy_url", ""),
        enable_notifications=data.get("enable_notifications", False),
        rss_check_interval=data.get("rss_check_interval", 600),
        token_refresh_interval=data.get("token_refresh_interval", 21600),
        max_retries=data.get("max_retries", 3),
        request_timeout=data.get("request_timeout", 30),
        log_level=data.get("log_level", "INFO"),
        log_max_bytes=data.get("log_max_bytes", 10 * 1024 * 1024),
        log_backup_count=data.get("log_backup_count", 5),
        log_json_format=data.get("log_json_format", False),
        log_sensitive_filter=data.get("log_sensitive_filter", True),
        enable_health_check=data.get("enable_health_check", False),
        health_check_interval=data.get("health_check_interval", 3600),
        enable_error_alert=data.get("enable_error_alert", False),
        error_alert_threshold=data.get("error_alert_threshold", 3),
    )

    errors = config.validate()
    if errors:
        error_msg = "\n".join([f"  - {error}" for error in errors])
        raise ValueError(f"配置验证失败:\n{error_msg}")

    logger.info("配置加载成功")
    return config


def save_config(config: Config, config_file: str) -> None:
    """保存配置到文件

    Args:
        config: Config 对象
        config_file: 配置文件路径
    """
    data = {
        "username": config.username,
        "password": config.password,
        "path": config.path,
        "rss": config.rss,
        "http_proxy": config.http_proxy,
        "https_proxy": config.https_proxy,
        "socks_proxy": config.socks_proxy,
        "enable_proxy": config.enable_proxy,
        "ntfy_url": config.ntfy_url,
        "enable_notifications": config.enable_notifications,
        "rss_check_interval": config.rss_check_interval,
        "token_refresh_interval": config.token_refresh_interval,
        "max_retries": config.max_retries,
        "request_timeout": config.request_timeout,
        "log_level": config.log_level,
        "log_max_bytes": config.log_max_bytes,
        "log_backup_count": config.log_backup_count,
    }

    try:
        with open(config_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        logger.info(f"配置已保存到: {config_file}")
    except Exception as e:
        logger.error(f"保存配置失败: {e}")
        raise
