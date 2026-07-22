"""FastAPI 应用入口"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.database import init_db
from app.routers import sync, accounts, articles, opportunities, campus, reading, alerts
from app.services.scheduler import start_scheduler

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


async def _run_sync():
    """在 scheduler 上下文中运行同步"""
    from app.database import SessionLocal
    from app.routers.sync import sync_articles
    db = SessionLocal()
    try:
        await sync_articles(db=db)
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时
    logger.info("Initializing database...")
    init_db()
    logger.info("Database initialized")

    logger.info("Starting scheduler...")
    start_scheduler(_run_sync)
    logger.info("Scheduler started")

    yield

    # 关闭时
    from app.services.scheduler import scheduler
    scheduler.shutdown()
    logger.info("Scheduler shut down")


app = FastAPI(
    title="公众号信息助手",
    description="微信公众号文章聚合、AI 机会识别、飞书通知",
    version="0.1.0",
    lifespan=lifespan,
)

# 允许本地前端跨域访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 本地使用，允许所有来源
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(sync.router)
app.include_router(accounts.router)
app.include_router(articles.router)
app.include_router(opportunities.router)
app.include_router(campus.router)
app.include_router(alerts.router)
app.include_router(reading.router)  # 包含页面和 API


@app.get("/api")
async def api_root():
    return {
        "name": "公众号信息助手",
        "version": "0.1.0",
        "docs": "/docs",
    }
