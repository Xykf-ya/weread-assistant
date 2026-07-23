"""校园信息 API (P1)"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import CampusInfo, Article, MonitoredAccount
from app.schemas import CampusInfoOut

router = APIRouter(prefix="/api/campus", tags=["campus"])


@router.get("", response_model=list[CampusInfoOut])
async def list_campus_events(
    event_type: str | None = None,
    organizer: str | None = None,
    limit: int = Query(default=50, le=200),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
):
    """获取校园活动列表（只展示有效分类：event/lecture/competition/volunteer/internship/notice）"""
    VALID_TYPES = {"event", "lecture", "competition", "volunteer", "internship", "notice"}
    query = db.query(CampusInfo).join(Article, CampusInfo.article_id == Article.id).filter(
        CampusInfo.event_type.in_(VALID_TYPES)
    )

    if event_type:
        query = query.filter(CampusInfo.event_type == event_type)
    if organizer:
        query = query.filter(CampusInfo.organizer.contains(organizer))

    results = query.order_by(Article.published_at.desc()).offset(offset).limit(limit).all()

    out = []
    for ci in results:
        article = db.query(Article).filter(Article.id == ci.article_id).first()
        acc = db.query(MonitoredAccount).filter(
            MonitoredAccount.werss_mp_id == article.werss_mp_id
        ).first() if article else None

        out.append(CampusInfoOut(
            id=ci.id,
            article_id=ci.article_id,
            event_type=ci.event_type,
            event_date=ci.event_date,
            location=ci.location,
            organizer=ci.organizer,
            deadline=ci.deadline,
            processed_at=ci.processed_at,
            title=article.title if article else None,
            mp_name=acc.mp_name if acc else None,
            original_url=article.original_url if article else None,
            published_at=article.published_at if article else None,
        ))

    return out
