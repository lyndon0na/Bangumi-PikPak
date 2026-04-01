"""PikPak 客户端封装模块

封装 PikPak API 操作，包括登录、文件管理、离线下载等。
"""

import asyncio
import json
import logging
import os
import time
from typing import Optional

import httpx
from pikpakapi import PikPakApi

from config import Config
from utils import async_retry, mask_sensitive_data

logger = logging.getLogger(__name__)


class PikPakClientWrapper:
    """PikPak 客户端封装类"""

    def __init__(self, config: Config):
        self.config = config
        self.client: Optional[PikPakApi] = None
        self.last_refresh_time: float = 0
        self.state_file: str = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "pikpak.json"
        )

    def setup_proxy(self) -> None:
        """设置代理环境变量"""
        if not self.config.enable_proxy:
            logger.info("代理未启用")
            return

        if self.config.http_proxy:
            os.environ["HTTP_PROXY"] = self.config.http_proxy
            os.environ["http_proxy"] = self.config.http_proxy
        if self.config.https_proxy:
            os.environ["HTTPS_PROXY"] = self.config.https_proxy
            os.environ["https_proxy"] = self.config.https_proxy
        if self.config.socks_proxy:
            os.environ["SOCKS_PROXY"] = self.config.socks_proxy
            os.environ["socks_proxy"] = self.config.socks_proxy

        logger.info(
            f"代理已启用 - HTTP: {mask_sensitive_data(self.config.http_proxy or 'N/A')}, "
            f"HTTPS: {mask_sensitive_data(self.config.https_proxy or 'N/A')}"
        )

    def load_state(self) -> Optional[dict]:
        """加载客户端状态

        Returns:
            客户端状态字典，如果不存在则返回 None
        """
        if not os.path.exists(self.state_file):
            return None

        try:
            with open(self.state_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.last_refresh_time = data.get("last_refresh_time", 0)
            logger.debug(f"加载客户端状态，上次刷新时间: {self.last_refresh_time}")
            return data.get("client_token")
        except Exception as e:
            logger.warning(f"加载客户端状态失败: {e}")
            return None

    def save_state(self) -> None:
        """保存客户端状态"""
        if not self.client:
            return

        data = {
            "last_refresh_time": self.last_refresh_time,
            "client_token": self.client.to_dict(),
        }

        try:
            with open(self.state_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            logger.info("客户端状态保存成功")
        except Exception as e:
            logger.error(f"保存客户端状态失败: {e}")

    async def initialize(self) -> None:
        """初始化客户端"""
        self.setup_proxy()

        client_token = self.load_state()

        if client_token and client_token.get("username") == self.config.username:
            try:
                self.client = PikPakApi.from_dict(client_token)
                logger.info("从保存的状态加载客户端成功")
            except Exception as e:
                logger.warning(f"加载客户端状态失败: {e}，将重新登录")
                self.client = PikPakApi(
                    username=self.config.username, password=self.config.password
                )
        else:
            self.client = PikPakApi(
                username=self.config.username, password=self.config.password
            )
            logger.info(
                f"创建新的客户端实例: {mask_sensitive_data(self.config.username)}"
            )

    @async_retry(max_retries=3, initial_delay=1.0)
    async def login(self) -> None:
        """登录 PikPak

        Raises:
            RuntimeError: 客户端未初始化
            Exception: 登录失败
        """
        if not self.client:
            raise RuntimeError("客户端未初始化")

        try:
            await self.client.file_list(parent_id=self.config.path)
            logger.info(f"账号 {mask_sensitive_data(self.config.username)} Token 有效")
        except Exception as e:
            logger.warning(f"Token 验证失败: {e}，将重新登录")
            try:
                await self.client.login()
                logger.info(
                    f"账号 {mask_sensitive_data(self.config.username)} 登录成功"
                )
            except Exception as login_error:
                logger.error(f"登录失败: {login_error}")
                raise

        await self.refresh_token()

    async def refresh_token(self) -> None:
        """刷新访问令牌"""
        current_time = time.time()

        if current_time - self.last_refresh_time < self.config.token_refresh_interval:
            logger.debug("Token 刷新间隔未到，跳过刷新")
            return

        if not self.client:
            return

        try:
            await self.client.refresh_access_token()
            self.last_refresh_time = current_time
            self.save_state()
            logger.info("Token 刷新成功")
        except Exception as e:
            logger.error(f"Token 刷新失败: {e}")
            self.last_refresh_time = 0

    @async_retry(max_retries=3, initial_delay=1.0)
    async def get_or_create_folder(self, folder_name: str) -> str:
        """获取或创建文件夹

        Args:
            folder_name: 文件夹名称

        Returns:
            文件夹 ID

        Raises:
            RuntimeError: 客户端未初始化
        """
        if not self.client:
            raise RuntimeError("客户端未初始化")

        folder_list = await self.client.file_list(parent_id=self.config.path)

        for file in folder_list.get("files", []):
            if file["name"] == folder_name:
                folder_id = file["id"]
                logger.debug(f"文件夹已存在: {folder_name} (ID: {folder_id})")
                return folder_id

        folder_info = await self.client.create_folder(
            name=folder_name, parent_id=self.config.path
        )
        folder_id = folder_info["file"]["id"]
        logger.info(f"创建文件夹: {folder_name} (ID: {folder_id})")
        return folder_id

    @async_retry(max_retries=3, initial_delay=1.0)
    async def offline_download(
        self, file_url: str, folder_id: str, bangumi_title: Optional[str] = None
    ) -> tuple[str, str]:
        """提交离线下载任务

        Args:
            file_url: 文件 URL（种子链接）
            folder_id: 目标文件夹 ID
            bangumi_title: 番剧标题（可选）

        Returns:
            (任务 ID, 任务名称)

        Raises:
            RuntimeError: 客户端未初始化
        """
        if not self.client:
            raise RuntimeError("客户端未初始化")

        result = await self.client.offline_download(
            file_url=file_url, parent_id=folder_id
        )

        task_id = result["task"]["id"]
        task_name = result["task"]["name"]

        logger.info(f"添加离线任务: {task_name} (ID: {task_id})")
        return task_id, task_name

    @async_retry(max_retries=3, initial_delay=1.0)
    async def check_magnet_exists(self, folder_id: str, magnet_link: str) -> bool:
        """检查磁力链接是否已存在

        Args:
            folder_id: 文件夹 ID
            magnet_link: 磁力链接

        Returns:
            是否已存在

        Raises:
            RuntimeError: 客户端未初始化
        """
        if not self.client:
            raise RuntimeError("客户端未初始化")

        file_list = await self.client.file_list(parent_id=folder_id)

        for file in file_list.get("files", []):
            if file.get("params", {}).get("url") == magnet_link:
                logger.debug(f"磁力链接已存在: {magnet_link}")
                return True

        return False

    async def close(self) -> None:
        """关闭客户端（清理资源）"""
        self.save_state()
        logger.info("PikPak 客户端资源已清理")
