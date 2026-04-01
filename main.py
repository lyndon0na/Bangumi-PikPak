"""Bangumi-PikPak 主程序

自动追踪番剧并上传到 PikPak 的工具。
"""

import asyncio
import logging
import os
import signal
import sys
import time
from typing import List

import httpx

from config import Config, load_config, save_config
from pikpak_client import PikPakClientWrapper
from rss_parser import RSSParser, TorrentInfo
from notifier import Notifier
from utils import setup_logging, ensure_directory, async_retry

logger = logging.getLogger(__name__)

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(SCRIPT_DIR, "config.json")


class BangumiDownloader:
    """番剧下载器主类"""

    def __init__(self, config: Config):
        self.config = config
        self.pikpak_client = PikPakClientWrapper(config)
        self.rss_parser = RSSParser(config)
        self.notifier = Notifier(config)
        self.http_client: httpx.AsyncClient = None
        self.torrent_list: List[TorrentInfo] = []

        # 监控和健康检查
        self.error_count: int = 0
        self.last_health_check: float = 0
        self.start_time: float = time.time()

    async def initialize(self) -> None:
        """初始化所有组件"""
        self.http_client = httpx.AsyncClient(timeout=self.config.request_timeout)
        await self.pikpak_client.initialize()
        logger.info("所有组件初始化完成")

    async def login(self) -> None:
        """登录 PikPak"""
        await self.pikpak_client.login()

    @async_retry(max_retries=3, initial_delay=1.0)
    async def download_torrent_file(self, torrent_url: str, save_path: str) -> bool:
        """下载种子文件

        Args:
            torrent_url: 种子 URL
            save_path: 保存路径

        Returns:
            是否成功
        """
        try:
            response = await self.http_client.get(torrent_url)
            response.raise_for_status()

            ensure_directory(os.path.dirname(save_path))

            with open(save_path, "wb") as f:
                f.write(response.content)

            logger.info(f"种子下载成功: {os.path.basename(save_path)}")
            return True

        except Exception as e:
            logger.error(f"种子下载失败: {e}")
            return False

    async def process_torrent(self, torrent_info: TorrentInfo) -> bool:
        """处理单个种子

        Args:
            torrent_info: 种子信息

        Returns:
            是否成功处理
        """
        torrent_name = torrent_info.torrent_url.split("/")[-1]
        folder_path = f"torrent/{torrent_info.bangumi_title}"
        local_path = os.path.join(folder_path, torrent_name)

        if os.path.exists(local_path):
            logger.debug(f"种子已存在，跳过: {torrent_name}")
            return False

        if not await self.download_torrent_file(torrent_info.torrent_url, local_path):
            return False

        try:
            folder_id = await self.pikpak_client.get_or_create_folder(
                torrent_info.bangumi_title
            )

            info_hash = torrent_name.rsplit(".", 1)[0]
            magnet_link = f"magnet:?xt=urn:btih:{info_hash}"

            if await self.pikpak_client.check_magnet_exists(folder_id, magnet_link):
                logger.info(f"磁力链接已存在，跳过: {torrent_name}")
                return False

            task_id, task_name = await self.pikpak_client.offline_download(
                torrent_info.torrent_url, folder_id, torrent_info.bangumi_title
            )

            await self.notifier.send_async(
                "番剧更新", f"📺 {torrent_info.bangumi_title} 更新啦！快去看看吧！🎉"
            )

            return True

        except Exception as e:
            logger.error(f"处理种子失败 {torrent_name}: {e}")
            return False

    async def run_once(self) -> None:
        """执行一次完整流程"""
        await self.pikpak_client.refresh_token()

        self.torrent_list = await self.rss_parser.parse()

        if not self.torrent_list:
            logger.info("RSS 源没有更新")
            return

        need_login = False
        for torrent_info in self.torrent_list:
            torrent_name = torrent_info.torrent_url.split("/")[-1]
            local_path = f"torrent/{torrent_info.bangumi_title}/{torrent_name}"

            if not os.path.exists(local_path):
                need_login = True
                break

        if need_login:
            await self.login()

            processed_count = 0
            for torrent_info in self.torrent_list:
                try:
                    if await self.process_torrent(torrent_info):
                        processed_count += 1
                except Exception as e:
                    logger.error(f"处理种子失败: {e}")
                    await self.notifier.send_async("处理错误", f"❌ 处理种子失败: {e}")
                    continue

            logger.info(f"本次处理完成，成功处理 {processed_count} 个种子")
        else:
            logger.info("所有种子已存在，无需处理")

        # 成功执行后重置错误计数
        self.error_count = 0

    async def health_check(self) -> None:
        """健康检查

        记录运行状态，包括：
        - 运行时长
        - 处理统计
        - 错误计数
        """
        if not self.config.enable_health_check:
            return

        current_time = time.time()

        if current_time - self.last_health_check < self.config.health_check_interval:
            return

        uptime = current_time - self.start_time
        hours = int(uptime // 3600)
        minutes = int((uptime % 3600) // 60)

        logger.info("=" * 60)
        logger.info("健康检查报告")
        logger.info(f"运行时长: {hours}小时{minutes}分钟")
        logger.info(f"错误计数: {self.error_count}")
        logger.info(f"RSS 条目: {len(self.torrent_list)}")
        logger.info("=" * 60)

        self.last_health_check = current_time

    async def check_error_alert(self) -> None:
        """检查错误告警

        如果连续错误次数达到阈值，发送告警通知。
        """
        if not self.config.enable_error_alert:
            return

        if self.error_count >= self.config.error_alert_threshold:
            logger.warning(f"连续错误次数达到阈值: {self.error_count}")

            await self.notifier.send_async(
                "⚠️ Bangumi-PikPak 告警",
                f"连续错误次数: {self.error_count}\n请检查服务状态！",
            )

            # 重置计数，避免重复告警
            self.error_count = 0

    async def cleanup(self) -> None:
        """清理资源"""
        if self.http_client:
            await self.http_client.aclose()
            logger.info("HTTP 客户端已关闭")

        await self.pikpak_client.close()
        logger.info("资源清理完成")


def main():
    """主函数"""
    try:
        config = load_config(CONFIG_FILE)
    except Exception as e:
        print(f"❌ 配置加载失败: {e}", file=sys.stderr)
        sys.exit(1)

    setup_logging(
        log_level=config.log_level,
        max_bytes=config.log_max_bytes,
        backup_count=config.log_backup_count,
        enable_sensitive_filter=config.log_sensitive_filter,
        json_format=config.log_json_format,
    )

    downloader = BangumiDownloader(config)

    def signal_handler(sig, frame):
        logger.info("收到退出信号，正在保存状态...")
        asyncio.run(downloader.cleanup())
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        asyncio.run(downloader.initialize())
    except Exception as e:
        logger.error(f"❌ 初始化失败: {e}")
        sys.exit(1)

    save_config(config, CONFIG_FILE)

    logger.info("=" * 60)
    logger.info("Bangumi-PikPak 启动成功")
    logger.info(f"账号: {config.username}")
    logger.info(f"RSS 检查间隔: {config.rss_check_interval} 秒")
    logger.info(f"通知: {'已启用' if config.enable_notifications else '未启用'}")
    logger.info(f"代理: {'已启用' if config.enable_proxy else '未启用'}")
    logger.info(f"健康检查: {'已启用' if config.enable_health_check else '未启用'}")
    logger.info(f"错误告警: {'已启用' if config.enable_error_alert else '未启用'}")
    logger.info("=" * 60)

    while True:
        try:
            asyncio.run(downloader.run_once())
            asyncio.run(downloader.health_check())
        except Exception as e:
            downloader.error_count += 1
            logger.error(
                f"❌ 运行出错 ({downloader.error_count}次): {e}", exc_info=True
            )
            asyncio.run(downloader.check_error_alert())
            asyncio.run(
                downloader.notifier.send_async(
                    "运行错误", f"❌ 运行出错 ({downloader.error_count}次): {e}"
                )
            )

        time.sleep(config.rss_check_interval)


if __name__ == "__main__":
    main()
