"""机会信息 API"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Opportunity, Article, MonitoredAccount
from app.schemas import OpportunityOut, OpportunityUpdate

router = APIRouter(prefix="/api/opportunities", tags=["opportunities"])


@router.get("", response_model=list[OpportunityOut])
async def list_opportunities(
    opp_type: str | None = None,
    is_opportunity: bool | None = True,
    min_confidence: float | None = 0.7,
    limit: int = Query(default=50, le=200),
    offset: int = Query(default=0, ge=0),
    upcoming_only: bool = False,
    db: Session = Depends(get_db),
):
    """获取机会列表"""
    query = db.query(Opportunity).join(Article, Opportunity.article_id == Article.id)

    if is_opportunity is not None:
        query = query.filter(Opportunity.is_opportunity == is_opportunity)
    if opp_type:
        query = query.filter(Opportunity.opp_type == opp_type)
    if min_confidence is not None:
        query = query.filter(Opportunity.confidence >= min_confidence)
    if upcoming_only:
        from datetime import date
        query = query.filter(Opportunity.deadline >= date.today())

    results = query.order_by(Article.published_at.desc()).offset(offset).limit(limit).all()

    # 补充文章信息
    out = []
    for opp in results:
        article = db.query(Article).filter(Article.id == opp.article_id).first()
        acc = db.query(MonitoredAccount).filter(
            MonitoredAccount.werss_mp_id == article.werss_mp_id
        ).first() if article else None

        out.append(OpportunityOut(
            id=opp.id,
            article_id=opp.article_id,
            is_opportunity=opp.is_opportunity,
            confidence=opp.confidence,
            opp_type=opp.opp_type,
            opp_name=opp.opp_name,
            deadline=opp.deadline,
            deadline_display=opp.deadline_display,
            target_audience=opp.target_audience,
            requirements=opp.requirements,
            notified=opp.notified,
            processed_at=opp.processed_at,
            title=article.title if article else None,
            mp_name=acc.mp_name if acc else None,
            original_url=article.original_url if article else None,
            published_at=article.published_at if article else None,
        ))

    return out


@router.get("/upcoming")
async def upcoming_deadlines(
    days: int = Query(default=7, le=90),
    db: Session = Depends(get_db),
):
    """获取即将截止的机会"""
    from datetime import date, timedelta
    today = date.today()
    end_date = today + timedelta(days=days)

    query = db.query(Opportunity).filter(
        Opportunity.is_opportunity == True,
        Opportunity.deadline.isnot(None),
        Opportunity.deadline >= today,
        Opportunity.deadline <= end_date,
    )

    results = query.order_by(Opportunity.deadline.asc()).all()

    out = []
    for opp in results:
        article = db.query(Article).filter(Article.id == opp.article_id).first()
        acc = db.query(MonitoredAccount).filter(
            MonitoredAccount.werss_mp_id == article.werss_mp_id
        ).first() if article else None

        out.append({
            "id": opp.id,
            "opp_name": opp.opp_name,
            "opp_type": opp.opp_type,
            "deadline": str(opp.deadline) if opp.deadline else None,
            "days_left": (opp.deadline - today).days if opp.deadline else None,
            "mp_name": acc.mp_name if acc else None,
            "original_url": article.original_url if article else None,
        })

    return out


@router.put("/{opportunity_id}")
async def update_opportunity(
    opportunity_id: int,
    data: OpportunityUpdate,
    db: Session = Depends(get_db),
):
    """人工修正 AI 结果"""
    opp = db.query(Opportunity).filter(Opportunity.id == opportunity_id).first()
    if not opp:
        raise HTTPException(status_code=404, detail="机会不存在")

    update_data = data.model_dump(exclude_unset=True)
    if "deadline" in update_data and update_data["deadline"]:
        from datetime import datetime
        try:
            update_data["deadline"] = datetime.strptime(update_data["deadline"], "%Y-%m-%d").date()
        except ValueError:
            update_data["deadline"] = None

    for key, value in update_data.items():
        if value is not None:
            setattr(opp, key, value)

    db.commit()
    return {"code": 0, "message": "已更新"}
