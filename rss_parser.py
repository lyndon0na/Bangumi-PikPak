"""RSS 解析模块

负责解析 Mikan Project 的 RSS 订阅，提取番剧信息。
"""

import logging
import urllib.request
from typing import List, Dict, Any
from dataclasses import dataclass

import feedparser
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filepath

from config import Config
from utils import async_retry

logger = logging.getLogger(__name__)

BANGUMI_TITLE_SELECTOR = "bangumi-title"


@dataclass
class TorrentInfo:
    """种子信息数据类"""

    title: str
    link: str
    torrent_url: str
    published_date: str
    bangumi_title: str


class RSSParser:
    """RSS 解析器"""

    def __init__(self, config: Config):
        self.config = config

    def setup_urllib_proxy(self) -> None:
        """为 urllib 设置代理"""
        if not self.config.enable_proxy:
            return

        proxy_dict = {}
        if self.config.http_proxy:
            proxy_dict["http"] = self.config.http_proxy
        if self.config.https_proxy:
            proxy_dict["https"] = self.config.https_proxy
        elif self.config.http_proxy:
            proxy_dict["https"] = self.config.http_proxy

        if proxy_dict:
            proxy_handler = urllib.request.ProxyHandler(proxy_dict)
            opener = urllib.request.build_opener(proxy_handler)
            urllib.request.install_opener(opener)
            logger.debug(f"urllib 代理已设置: {proxy_dict}")

    @async_retry(max_retries=3, initial_delay=1.0)
    async def fetch_bangumi_title(self, mikan_episode_url: str) -> str:
        """获取番剧标题

        Args:
            mikan_episode_url: Mikan 剧集页面 URL

        Returns:
            番剧标题

        Raises:
            ValueError: 无法找到番剧标题
        """
        self.setup_urllib_proxy()

        try:
            with urllib.request.urlopen(
                mikan_episode_url, timeout=self.config.request_timeout
            ) as response:
                soup = BeautifulSoup(response.read(), "html.parser")
                title_element = soup.select_one("p", {"class": BANGUMI_TITLE_SELECTOR})

                if not title_element:
                    raise ValueError(f"无法找到番剧标题: {mikan_episode_url}")

                title = sanitize_filepath(title_element.text.strip())
                logger.debug(f"获取番剧标题: {title} (URL: {mikan_episode_url})")
                return title

        except urllib.error.URLError as e:
            logger.error(f"获取番剧页面失败: {e}")
            raise

    async def parse(self) -> List[TorrentInfo]:
        """解析 RSS

        Returns:
            种子信息列表

        Raises:
            ValueError: RSS 解析失败
        """
        logger.info(f"开始解析 RSS: {self.config.rss}")

        try:
            rss = feedparser.parse(self.config.rss)
        except Exception as e:
            logger.error(f"RSS 解析失败: {e}")
            raise

        if rss.bozo:
            logger.warning(f"RSS 解析可能出现问题: {rss.bozo_exception}")

        entries = rss.get("entries", [])
        if not entries:
            logger.info("RSS 中没有条目")
            return []

        logger.info(f"RSS 包含 {len(entries)} 个条目")

        torrent_list = []

        for entry in entries:
            try:
                title = entry.get("title", "")
                link = entry.get("link", "")
                enclosures = entry.get("enclosures", [])
                published = entry.get("published", "")

                if not enclosures:
                    logger.warning(f"种子信息缺失: {title}")
                    continue

                torrent_url = enclosures[0].get("url", "")
                if not torrent_url:
                    logger.warning(f"种子 URL 缺失: {title}")
                    continue

                try:
                    bangumi_title = await self.fetch_bangumi_title(link)
                except Exception as e:
                    logger.error(f"获取番剧标题失败 {title}: {e}")
                    continue

                published_date = published.split("T")[0] if published else ""

                torrent_info = TorrentInfo(
                    title=title,
                    link=link,
                    torrent_url=torrent_url,
                    published_date=published_date,
                    bangumi_title=bangumi_title,
                )

                torrent_list.append(torrent_info)
                logger.info(f"解析条目: {title} -> {bangumi_title}")

            except Exception as e:
                logger.error(f"解析 RSS 条目失败: {e}")
                continue

        logger.info(f"RSS 解析完成，成功获取 {len(torrent_list)} 个种子信息")
        return torrent_list
