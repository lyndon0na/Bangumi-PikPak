"""状态管理模块

负责持久化存储和查询番剧更新历史。
"""

import json
import os
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)


@dataclass
class UpdateRecord:
    """番剧更新记录"""

    bangumi_title: str
    episode: str
    torrent_url: str
    timestamp: str
    status: str
    file_size: Optional[int] = None


@dataclass
class Stats:
    """统计信息"""

    total_processed: int = 0
    success_count: int = 0
    failed_count: int = 0
    last_check: Optional[str] = None
    start_time: Optional[str] = None


class StateManager:
    """状态管理器"""

    def __init__(self, state_file: str = "state.json"):
        self.state_file = state_file
        self.state: Dict = self._load_state()

    def _load_state(self) -> Dict:
        """加载状态文件"""
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"加载状态文件失败: {e}")

        return {"updates": [], "stats": asdict(Stats())}

    def _save_state(self) -> None:
        """保存状态文件"""
        try:
            with open(self.state_file, "w", encoding="utf-8") as f:
                json.dump(self.state, f, indent=2, ensure_ascii=False)
            logger.debug("状态已保存")
        except Exception as e:
            logger.error(f"保存状态文件失败: {e}")

    def add_update(
        self,
        bangumi_title: str,
        episode: str,
        torrent_url: str,
        status: str,
        file_size: Optional[int] = None,
    ) -> None:
        """添加更新记录

        Args:
            bangumi_title: 番剧标题
            episode: 集数
            torrent_url: 种子URL
            status: 状态 (success/failed)
            file_size: 文件大小(字节)
        """
        record = UpdateRecord(
            bangumi_title=bangumi_title,
            episode=episode,
            torrent_url=torrent_url,
            timestamp=datetime.now().isoformat(),
            status=status,
            file_size=file_size,
        )

        self.state["updates"].append(asdict(record))

        if status == "success":
            self.state["stats"]["success_count"] += 1
        else:
            self.state["stats"]["failed_count"] += 1

        self.state["stats"]["total_processed"] += 1
        self._save_state()

        logger.info(f"添加更新记录: {bangumi_title} - {episode} ({status})")

    def get_updates(
        self,
        limit: Optional[int] = None,
        bangumi_title: Optional[str] = None,
        status: Optional[str] = None,
    ) -> List[Dict]:
        """获取更新记录

        Args:
            limit: 限制返回数量
            bangumi_title: 按番剧标题过滤
            status: 按状态过滤

        Returns:
            更新记录列表
        """
        updates = self.state["updates"]

        if bangumi_title:
            updates = [u for u in updates if u["bangumi_title"] == bangumi_title]

        if status:
            updates = [u for u in updates if u["status"] == status]

        updates = sorted(updates, key=lambda x: x["timestamp"], reverse=True)

        if limit:
            updates = updates[:limit]

        return updates

    def get_stats(self) -> Stats:
        """获取统计信息"""
        return Stats(**self.state["stats"])

    def update_last_check(self) -> None:
        """更新最后检查时间"""
        self.state["stats"]["last_check"] = datetime.now().isoformat()
        self._save_state()

    def set_start_time(self, start_time: float) -> None:
        """设置启动时间"""
        self.state["stats"]["start_time"] = datetime.fromtimestamp(
            start_time
        ).isoformat()
        self._save_state()

    def get_bangumi_list(self) -> List[str]:
        """获取所有番剧标题列表"""
        titles = set()
        for update in self.state["updates"]:
            titles.add(update["bangumi_title"])
        return sorted(list(titles))

    def clear_old_records(self, days: int = 30) -> int:
        """清理旧记录

        Args:
            days: 保留最近多少天的记录

        Returns:
            删除的记录数量
        """
        from datetime import timedelta

        cutoff = datetime.now() - timedelta(days=days)
        cutoff_str = cutoff.isoformat()

        original_count = len(self.state["updates"])
        self.state["updates"] = [
            u for u in self.state["updates"] if u["timestamp"] >= cutoff_str
        ]

        deleted_count = original_count - len(self.state["updates"])

        if deleted_count > 0:
            self._save_state()
            logger.info(f"清理了 {deleted_count} 条旧记录")

        return deleted_count
