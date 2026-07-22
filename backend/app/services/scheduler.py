"""APScheduler 定时任务管理"""

import logging
from datetime import datetime, timedelta
from typing import Callable, Awaitable

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from app.config import settings

logger = logging.getLogger(__name__)

# 全局调度器实例
scheduler = AsyncIOScheduler()

# 各类型的上次同步时间
_last_sync: dict[str, datetime] = {}


def get_sync_interval(account_type: str) -> int:
    """获取指定类型的同步间隔（分钟）"""
    mapping = {
        "opportunity": settings.sync_interval_opportunity,
        "campus": settings.sync_interval_campus,
        "news": settings.sync_interval_news,
        "interest": settings.sync_interval_interest,
    }
    return mapping.get(account_type, settings.sync_interval_minutes)


def should_sync(account_type: str) -> bool:
    """判断某类型是否到了该同步的时间"""
    interval = get_sync_interval(account_type)
    last = _last_sync.get(account_type)
    if last is None:
        return True
    return datetime.now() - last > timedelta(minutes=interval)


def mark_synced(account_type: str):
    """记录同步时间"""
    _last_sync[account_type] = datetime.now()


def start_scheduler(sync_func: Callable[[], Awaitable[None]]):
    """启动定时任务

    Args:
        sync_func: 同步+AI 处理的核心函数（async）
    """
    # 使用最短的间隔作为调度器 tick 间隔
    all_intervals = [
        settings.sync_interval_minutes,
        settings.sync_interval_opportunity,
        settings.sync_interval_campus,
        settings.sync_interval_news,
        settings.sync_interval_interest,
    ]
    min_interval = max(min(all_intervals), 30)  # 最少 30 分钟

    async def _sync_wrapper():
        try:
            await sync_func()
        except Exception as e:
            logger.error(f"Sync job failed: {e}")

    scheduler.add_job(
        _sync_wrapper,
        trigger=IntervalTrigger(minutes=min_interval),
        id="article_sync",
        name="公众号文章同步+AI处理",
        replace_existing=True,
    )

    # 启动时立即跑一次
    scheduler.add_job(
        _sync_wrapper,
        trigger=None,  # 立即执行
        id="article_sync_startup",
        name="启动时立即同步",
    )

    scheduler.start()
    logger.info(f"Scheduler started, check interval: {min_interval}min")
