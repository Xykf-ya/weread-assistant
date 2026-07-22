"""SQLAlchemy 数据模型"""

from datetime import datetime

from sqlalchemy import (
    Column, Integer, String, Text, Float, Boolean, Date, DateTime, ForeignKey,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class MonitoredAccount(Base):
    """监控的公众号"""
    __tablename__ = "monitored_account"

    id = Column(Integer, primary_key=True, autoincrement=True)
    werss_mp_id = Column(String(255), unique=True, nullable=False, comment="WeRSS 内部公众号 ID")
    mp_name = Column(String(255), nullable=False, comment="公众号名称")
    cover_url = Column(Text, comment="公众号头像 URL")
    account_type = Column(
        String(20), nullable=False, default="opportunity",
        comment="opportunity / campus / news / interest"
    )
    tags = Column(Text, comment='JSON 数组，如 ["浙大","就业"]')
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


class Article(Base):
    """文章（从 WeRSS 同步）"""
    __tablename__ = "article"

    id = Column(Integer, primary_key=True, autoincrement=True)
    werss_article_id = Column(String(255), unique=True, nullable=False, comment="WeRSS 内部文章 ID，去重键")
    werss_mp_id = Column(String(255), nullable=False, comment="WeRSS 公众号 ID")
    title = Column(Text, nullable=False)
    author = Column(String(255))
    summary = Column(Text, comment="摘要")
    cover_url = Column(Text, comment="封面图 URL")
    original_url = Column(Text, nullable=False, comment="微信原文链接")
    raw_content = Column(Text, comment="全文 HTML，AI 分析用")
    published_at = Column(DateTime, nullable=False, comment="发布时间")
    fetched_at = Column(DateTime, default=func.now(), comment="同步时间")
    ai_processed = Column(Boolean, default=False, comment="是否已完成 AI 处理")
    created_at = Column(DateTime, default=func.now())

    # 关联
    opportunity = relationship("Opportunity", back_populates="article", uselist=False, cascade="all, delete-orphan")
    campus_info = relationship("CampusInfo", back_populates="article", uselist=False, cascade="all, delete-orphan")
    reading_state = relationship("ReadingState", back_populates="article", uselist=False, cascade="all, delete-orphan")


class Opportunity(Base):
    """AI 提取的机会信息"""
    __tablename__ = "opportunity"

    id = Column(Integer, primary_key=True, autoincrement=True)
    article_id = Column(Integer, ForeignKey("article.id", ondelete="CASCADE"), unique=True, nullable=False)
    is_opportunity = Column(Boolean, default=False)
    confidence = Column(Float, comment="AI 置信度 0-1")
    opp_type = Column(String(30), comment="job/internship/competition/camp/volunteer/registration/other")
    opp_name = Column(Text, comment="机会名称")
    deadline = Column(Date, comment="截止日期")
    deadline_display = Column(Text, comment="原始截止日期文本")
    target_audience = Column(Text, comment="面向人群")
    requirements = Column(Text, comment="报名要求摘要")
    ai_raw_response = Column(Text, comment="AI 完整返回 JSON，调试用")
    ai_model = Column(String(50), comment="使用的模型")
    ai_tokens = Column(Integer, comment="消耗 token 数")
    notified = Column(Boolean, default=False, comment="是否已推送通知")
    notified_at = Column(DateTime)
    processed_at = Column(DateTime, default=func.now())

    article = relationship("Article", back_populates="opportunity")


class CampusInfo(Base):
    """AI 提取的校园活动信息 (P1)"""
    __tablename__ = "campus_info"

    id = Column(Integer, primary_key=True, autoincrement=True)
    article_id = Column(Integer, ForeignKey("article.id", ondelete="CASCADE"), unique=True, nullable=False)
    event_type = Column(String(30), comment="event/lecture/competition/volunteer/internship/notice")
    event_date = Column(Date, comment="活动日期")
    location = Column(Text, comment="地点")
    organizer = Column(Text, comment="主办方/学院")
    deadline = Column(Date, comment="报名截止")
    ai_raw_response = Column(Text)
    ai_model = Column(String(50))
    processed_at = Column(DateTime, default=func.now())

    article = relationship("Article", back_populates="campus_info")


class ReadingState(Base):
    """阅读状态 (P2)"""
    __tablename__ = "reading_state"

    id = Column(Integer, primary_key=True, autoincrement=True)
    article_id = Column(Integer, ForeignKey("article.id", ondelete="CASCADE"), unique=True, nullable=False)
    is_read = Column(Boolean, default=False)
    is_favorite = Column(Boolean, default=False)
    notes = Column(Text)
    read_at = Column(DateTime)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    article = relationship("Article", back_populates="reading_state")


class AiProcessLog(Base):
    """AI 处理日志"""
    __tablename__ = "ai_process_log"

    id = Column(Integer, primary_key=True, autoincrement=True)
    article_id = Column(Integer, comment="关联文章 ID")
    task_type = Column(String(30), comment="opportunity_detect / campus_classify")
    model = Column(String(50), comment="使用的模型")
    tokens_in = Column(Integer, comment="输入 token 数")
    tokens_out = Column(Integer, comment="输出 token 数")
    cost = Column(Float, comment="费用")
    duration_ms = Column(Integer, comment="耗时（毫秒）")
    success = Column(Boolean, default=True)
    error = Column(Text)
    created_at = Column(DateTime, default=func.now())


class AlertLog(Base):
    """通知发送记录"""
    __tablename__ = "alert_log"

    id = Column(Integer, primary_key=True, autoincrement=True)
    opportunity_id = Column(Integer, ForeignKey("opportunity.id", ondelete="CASCADE"), nullable=False)
    channel = Column(String(20), nullable=False, comment="feishu / email")
    status = Column(String(20), nullable=False, comment="sent / failed")
    error_message = Column(Text)
    sent_at = Column(DateTime, default=func.now())
