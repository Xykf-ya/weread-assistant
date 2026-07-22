"""Pydantic 请求/响应模型"""

from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, Field


# === 公众号 ===

class AccountCreate(BaseModel):
    werss_mp_id: str
    mp_name: str
    cover_url: Optional[str] = None
    account_type: str = "opportunity"  # opportunity / campus / news / interest
    tags: Optional[str] = "[]"  # JSON 数组字符串


class AccountUpdate(BaseModel):
    mp_name: Optional[str] = None
    cover_url: Optional[str] = None
    account_type: Optional[str] = None
    tags: Optional[str] = None
    is_active: Optional[bool] = None


class AccountOut(BaseModel):
    id: int
    werss_mp_id: str
    mp_name: str
    cover_url: Optional[str]
    account_type: str
    tags: Optional[str]
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


# === 文章 ===

class ArticleOut(BaseModel):
    id: int
    werss_article_id: str
    werss_mp_id: str
    title: str
    author: Optional[str]
    summary: Optional[str]
    cover_url: Optional[str]
    original_url: str
    published_at: datetime
    fetched_at: datetime
    ai_processed: bool

    model_config = {"from_attributes": True}


class ArticleDetailOut(ArticleOut):
    raw_content: Optional[str]

    model_config = {"from_attributes": True}


class ArticleListParams(BaseModel):
    account_type: Optional[str] = None
    werss_mp_id: Optional[str] = None
    is_read: Optional[bool] = None
    is_favorite: Optional[bool] = None
    limit: int = 50
    offset: int = 0


# === 机会 ===

class OpportunityOut(BaseModel):
    id: int
    article_id: int
    is_opportunity: bool
    confidence: Optional[float]
    opp_type: Optional[str]
    opp_name: Optional[str]
    deadline: Optional[date]
    deadline_display: Optional[str]
    target_audience: Optional[str]
    requirements: Optional[str]
    notified: bool
    processed_at: datetime
    # 关联文章信息
    title: Optional[str] = None
    mp_name: Optional[str] = None
    original_url: Optional[str] = None
    published_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class OpportunityUpdate(BaseModel):
    """人工修正 AI 结果"""
    is_opportunity: Optional[bool] = None
    opp_type: Optional[str] = None
    opp_name: Optional[str] = None
    deadline: Optional[str] = None  # YYYY-MM-DD
    deadline_display: Optional[str] = None
    target_audience: Optional[str] = None
    requirements: Optional[str] = None


# === 校园信息 ===

class CampusInfoOut(BaseModel):
    id: int
    article_id: int
    event_type: Optional[str]
    event_date: Optional[date]
    location: Optional[str]
    organizer: Optional[str]
    deadline: Optional[date]
    processed_at: datetime
    # 关联文章信息
    title: Optional[str] = None
    mp_name: Optional[str] = None
    original_url: Optional[str] = None
    published_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


# === 阅读状态 ===

class ReadingStateUpdate(BaseModel):
    is_read: Optional[bool] = None
    is_favorite: Optional[bool] = None
    notes: Optional[str] = None


# === 通用响应 ===

class ApiResponse(BaseModel):
    code: int = 0
    message: str = "ok"
    data: Optional[dict | list] = None


class SyncResult(BaseModel):
    total_fetched: int = 0
    new_articles: int = 0
    ai_processed: int = 0
    alerts_sent: int = 0
    errors: list[str] = []


class HealthStatus(BaseModel):
    status: str = "ok"
    werss: str = "unknown"
    deepseek: str = "unknown"
    dashscope: str = "unknown"
    feishu: str = "unknown"
