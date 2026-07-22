"""阅读状态管理 API (P2)

前端页面由独立的前端项目负责，本模块只提供 API。
"""

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Article, ReadingState
from app.schemas import ReadingStateUpdate

router = APIRouter(tags=["reading"])


@router.put("/api/articles/{article_id}/reading-state")
async def update_reading_state(
    article_id: int,
    data: ReadingStateUpdate,
    db: Session = Depends(get_db),
):
    """更新文章阅读状态（已读/未读/收藏）"""
    article = db.query(Article).filter(Article.id == article_id).first()
    if not article:
        raise HTTPException(status_code=404, detail="文章不存在")

    state = db.query(ReadingState).filter(ReadingState.article_id == article_id).first()
    if not state:
        state = ReadingState(article_id=article_id)
        db.add(state)

    if data.is_read is not None:
        state.is_read = data.is_read
        if data.is_read:
            state.read_at = datetime.now()
    if data.is_favorite is not None:
        state.is_favorite = data.is_favorite
    if data.notes is not None:
        state.notes = data.notes

    db.commit()
    return {"code": 0, "message": "ok"}
