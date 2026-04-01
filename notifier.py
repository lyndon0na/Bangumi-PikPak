"""通知模块

负责发送番剧更新通知到 ntfy.sh。
"""

import logging
from typing import Optional

import requests

from config import Config

logger = logging.getLogger(__name__)


class Notifier:
    """通知发送器"""

    def __init__(self, config: Config):
        self.config = config

    def send(self, title: str, message: str) -> bool:
        """发送通知

        Args:
            title: 通知标题
            message: 通知内容

        Returns:
            发送是否成功
        """
        if not self.config.enable_notifications:
            logger.debug("通知功能未启用，跳过发送")
            return True

        if not self.config.ntfy_url:
            logger.warning("通知 URL 未配置，跳过发送")
            return False

        try:
            clean_title = title.encode("ascii", "ignore").decode("ascii")
            headers = {
                "Title": clean_title,
                "Priority": "default",
                "Tags": "anime,pikpak",
            }

            proxies = None
            if self.config.enable_proxy:
                proxies = {}
                if self.config.http_proxy:
                    proxies["http"] = self.config.http_proxy
                if self.config.https_proxy:
                    proxies["https"] = self.config.https_proxy
                elif self.config.http_proxy:
                    proxies["https"] = self.config.http_proxy

            response = requests.post(
                self.config.ntfy_url,
                data=message.encode("utf-8"),
                headers=headers,
                proxies=proxies,
                timeout=10,
            )

            if response.status_code == 200:
                logger.info(f"通知发送成功: {title}")
                return True
            else:
                logger.warning(f"通知发送失败，状态码: {response.status_code}")
                return False

        except requests.exceptions.Timeout:
            logger.error("通知发送超时")
            return False
        except requests.exceptions.RequestException as e:
            logger.error(f"通知发送失败: {e}")
            return False
        except Exception as e:
            logger.error(f"通知发送时发生未知错误: {e}")
            return False

    async def send_async(self, title: str, message: str) -> bool:
        """异步发送通知

        Args:
            title: 通知标题
            message: 通知内容

        Returns:
            发送是否成功
        """
        import asyncio

        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.send, title, message)

    def send_bangumi_update(self, bangumi_title: str) -> bool:
        """发送番剧更新通知

        Args:
            bangumi_title: 番剧标题

        Returns:
            发送是否成功
        """
        title = "番剧更新"
        message = f"📺 {bangumi_title} 更新啦！快去看看吧！🎉"
        return self.send(title, message)

    def send_task_created(self, task_name: str) -> bool:
        """发送任务创建通知

        Args:
            task_name: 任务名称

        Returns:
            发送是否成功
        """
        title = "PikPak 任务"
        message = f"✅ 成功添加离线任务：{task_name} 🎉"
        return self.send(title, message)

    def send_error(self, error_message: str) -> bool:
        """发送错误通知

        Args:
            error_message: 错误消息

        Returns:
            发送是否成功
        """
        title = "Bangumi-PikPak 错误"
        message = f"❌ 发生错误: {error_message}"
        return self.send(title, message)
