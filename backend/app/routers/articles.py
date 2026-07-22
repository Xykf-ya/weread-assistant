"""文章 API"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Article, MonitoredAccount, ReadingState
from app.schemas import ArticleOut, ArticleDetailOut, ReadingStateUpdate

router = APIRouter(prefix="/api/articles", tags=["articles"])


@router.get("", response_model=list[ArticleOut])
async def list_articles(
    account_type: str | None = None,
    werss_mp_id: str | None = None,
    limit: int = Query(default=50, le=200),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
):
    """获取文章列表"""
    query = db.query(Article)

    # 按公众号类型过滤
    if account_type:
        mp_ids = db.query(MonitoredAccount.werss_mp_id).filter(
            MonitoredAccount.account_type == account_type
        ).all()
        mp_id_list = [r[0] for r in mp_ids]
        if mp_id_list:
            query = query.filter(Article.werss_mp_id.in_(mp_id_list))
        else:
            return []

    # 按具体公众号过滤
    if werss_mp_id:
        query = query.filter(Article.werss_mp_id == werss_mp_id)

    return query.order_by(Article.published_at.desc()).offset(offset).limit(limit).all()


@router.get("/{article_id}", response_model=ArticleDetailOut)
async def get_article(article_id: int, db: Session = Depends(get_db)):
    """获取文章详情"""
    article = db.query(Article).filter(Article.id == article_id).first()
    if not article:
        raise HTTPException(status_code=404, detail="文章不存在")
    return article


@router.put("/{article_id}/reading-state")
async def update_reading_state(
    article_id: int,
    data: ReadingStateUpdate,
    db: Session = Depends(get_db),
):
    """更新阅读状态"""
    article = db.query(Article).filter(Article.id == article_id).first()
    if not article:
        raise HTTPException(status_code=404, detail="文章不存在")

    state = db.query(ReadingState).filter(ReadingState.article_id == article_id).first()
    if not state:
        from datetime import datetime
        state = ReadingState(article_id=article_id)
        db.add(state)

    if data.is_read is not None:
        state.is_read = data.is_read
        if data.is_read:
            from datetime import datetime
            state.read_at = datetime.now()
    if data.is_favorite is not None:
        state.is_favorite = data.is_favorite
    if data.notes is not None:
        state.notes = data.notes

    db.commit()
    return {"code": 0, "message": "ok"}
