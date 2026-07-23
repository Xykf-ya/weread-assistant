"""同步 + AI 处理 API"""

import logging
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.models import MonitoredAccount, Article, Opportunity, CampusInfo
from app.schemas import SyncResult
from app.services.werss import WeRSSClient, strip_html, extract_images, is_image_article
from app.services.ai import classify_article
from app.services.notifier import send_feishu_opportunity
from app.services.scheduler import should_sync, mark_synced

router = APIRouter(prefix="/api", tags=["sync"])
logger = logging.getLogger(__name__)

werss = WeRSSClient()

# 合法的校园活动类型（非 None 才是有效分类）
VALID_CAMPUS_TYPES = {"event", "lecture", "competition", "volunteer", "internship", "notice"}


def _get_last_sync_time(db: Session) -> datetime | None:
    """获取上次同步时间（取最新文章的 fetched_at）"""
    result = db.query(func.max(Article.fetched_at)).scalar()
    return result


def _is_first_sync(db: Session) -> bool:
    return db.query(Article.id).first() is None


@router.post("/sync", response_model=SyncResult)
async def sync_articles(db: Session = Depends(get_db)):
    """触发同步：从 WeRSS 拉取新文章 → AI 处理 → 发送通知"""
    result = SyncResult()

    accounts = db.query(MonitoredAccount).filter(MonitoredAccount.is_active == True).all()
    if not accounts:
        result.errors.append("没有配置任何监控公众号")
        return result

    # 构建 mp_id → 公众号映射
    mp_id_to_account = {acc.werss_mp_id: acc for acc in accounts}

    # 确定需要同步的类型
    types_to_sync = set()
    for acc in accounts:
        if should_sync(acc.account_type):
            types_to_sync.add(acc.account_type)

    if not types_to_sync:
        result.errors.append("所有类型都还没到同步时间")
        return result

    # === 拉取规则 ===
    # 首次同步：拉最近 50 篇
    # 后续同步：拉最近 100 篇，按发布时间过滤（只保留上次同步之后的）
    is_first = _is_first_sync(db)
    fetch_limit = 50 if is_first else 100

    try:
        all_articles = await werss.get_articles(limit=fetch_limit)
    except Exception as e:
        result.errors.append(f"从 WeRSS 拉取文章失败: {e}")
        return result

    result.total_fetched = len(all_articles)

    # 如果不是首次，按时间过滤
    if not is_first:
        last_sync = _get_last_sync_time(db)
        if last_sync:
            # 留一点余量，多保留 1 小时内的文章
            cutoff = last_sync - timedelta(hours=1)
            filtered = []
            for art_data in all_articles:
                publish_ts = art_data.get("publish_time")
                if publish_ts and isinstance(publish_ts, (int, float)):
                    pub_time = datetime.fromtimestamp(publish_ts)
                    if pub_time > cutoff:
                        filtered.append(art_data)
            all_articles = filtered

    for art_data in all_articles:
        werss_art_id = str(art_data.get("id", ""))
        if not werss_art_id:
            continue

        # 去重
        existing = db.query(Article).filter(
            Article.werss_article_id == werss_art_id
        ).first()
        if existing:
            continue

        # 用 mp_id 匹配公众号
        article_mp_id = art_data.get("mp_id", "")
        acc = mp_id_to_account.get(article_mp_id)
        if not acc:
            continue

        # 新闻类跳过拉取（用户已取消订阅，但保留兼容）
        if acc.account_type == "news":
            continue

        # 检查是否到了该类型的同步时间
        if acc.account_type not in types_to_sync:
            continue

        # 获取文章详情
        detail = await werss.get_article_detail(werss_art_id)
        raw_content = detail.get("content", "") if detail else ""

        # 解析发布时间（Unix 时间戳）
        publish_ts = art_data.get("publish_time")
        if publish_ts and isinstance(publish_ts, (int, float)):
            published_at = datetime.fromtimestamp(publish_ts)
        else:
            published_at = datetime.now()

        article = Article(
            werss_article_id=werss_art_id,
            werss_mp_id=article_mp_id,
            title=art_data.get("title", "无标题"),
            author=art_data.get("author"),
            summary=art_data.get("description") or art_data.get("digest", ""),
            cover_url=art_data.get("pic_url") or art_data.get("cover_url", ""),
            original_url=art_data.get("url", ""),
            raw_content=raw_content,
            published_at=published_at,
            ai_processed=False,
        )
        db.add(article)
        result.new_articles += 1

    db.commit()

    for t in types_to_sync:
        mark_synced(t)

    # === AI 处理 ===
    pending = db.query(Article).filter(Article.ai_processed == False).all()

    for article in pending:
        acc = mp_id_to_account.get(article.werss_mp_id)
        if not acc:
            continue

        # 兴趣类跳过 AI
        if acc.account_type == "interest":
            article.ai_processed = True
            db.commit()
            continue

        task_type = "opportunity" if acc.account_type == "opportunity" else "campus"

        # 避免重复处理
        if task_type == "opportunity":
            if db.query(Opportunity).filter(Opportunity.article_id == article.id).first():
                article.ai_processed = True
                db.commit()
                continue
        elif task_type == "campus":
            if db.query(CampusInfo).filter(CampusInfo.article_id == article.id).first():
                article.ai_processed = True
                db.commit()
                continue

        img = is_image_article(article.raw_content)
        img_urls = extract_images(article.raw_content) if img else []

        try:
            ai_result = await classify_article(
                title=article.title,
                raw_content=article.raw_content or "",
                is_image=img,
                image_urls=img_urls,
                task=task_type,
            )
            meta = ai_result.pop("_meta", {})

            if task_type == "opportunity":
                deadline_str = ai_result.get("deadline")
                deadline_date = None
                if deadline_str:
                    try:
                        deadline_date = datetime.strptime(deadline_str, "%Y-%m-%d").date()
                    except (ValueError, TypeError):
                        pass

                opp = Opportunity(
                    article_id=article.id,
                    is_opportunity=ai_result.get("is_opportunity", False),
                    confidence=ai_result.get("confidence", 0),
                    opp_type=ai_result.get("opp_type"),
                    opp_name=ai_result.get("opp_name"),
                    deadline=deadline_date,
                    deadline_display=ai_result.get("deadline_display"),
                    target_audience=ai_result.get("target_audience"),
                    requirements=ai_result.get("summary"),
                    ai_raw_response=str(ai_result),
                    ai_model=meta.get("model", "unknown"),
                    ai_tokens=meta.get("tokens_in", 0) + meta.get("tokens_out", 0),
                )
                db.add(opp)
                db.commit()

                if opp.is_opportunity and opp.confidence and opp.confidence >= 0.7:
                    sent = await send_feishu_opportunity(
                        opp_name=opp.opp_name or article.title,
                        opp_type=opp.opp_type or "other",
                        mp_name=acc.mp_name,
                        published_at=article.published_at.strftime("%m-%d"),
                        deadline_display=opp.deadline_display,
                        target_audience=opp.target_audience,
                        summary=ai_result.get("summary"),
                        original_url=article.original_url,
                    )
                    if sent:
                        opp.notified = True
                        opp.notified_at = datetime.now()
                        db.commit()
                        result.alerts_sent += 1

            elif task_type == "campus":
                event_date_str = ai_result.get("event_date")
                event_date = None
                if event_date_str:
                    try:
                        event_date = datetime.strptime(event_date_str, "%Y-%m-%d").date()
                    except (ValueError, TypeError):
                        pass

                deadline_str = ai_result.get("deadline")
                campus_deadline = None
                if deadline_str:
                    try:
                        campus_deadline = datetime.strptime(deadline_str, "%Y-%m-%d").date()
                    except (ValueError, TypeError):
                        pass

                campus = CampusInfo(
                    article_id=article.id,
                    event_type=ai_result.get("event_type"),
                    event_date=event_date,
                    location=ai_result.get("location"),
                    organizer=ai_result.get("organizer"),
                    deadline=campus_deadline,
                    ai_raw_response=str(ai_result),
                    ai_model=meta.get("model", "unknown"),
                )
                db.add(campus)
                db.commit()

            article.ai_processed = True
            result.ai_processed += 1
            db.commit()

        except Exception as e:
            logger.error(f"AI processing failed for article {article.id}: {e}")
            db.rollback()
            result.errors.append(f"AI处理失败 (文章 {article.id}): {str(e)}")

    return result


# === 调试接口：查看 AI 全量判定结果 ===

@router.get("/debug/ai-results")
async def debug_ai_results(
    task_type: str = Query(default="opportunity", description="opportunity 或 campus"),
    db: Session = Depends(get_db),
):
    """调试接口：展示 AI 的所有判定结果，包括被拒绝的"""
    out = []

    if task_type == "opportunity":
        results = db.query(Opportunity, Article, MonitoredAccount).join(
            Article, Opportunity.article_id == Article.id
        ).join(
            MonitoredAccount, Article.werss_mp_id == MonitoredAccount.werss_mp_id
        ).order_by(Article.published_at.desc()).limit(50).all()

        for opp, art, acc in results:
            out.append({
                "title": art.title,
                "mp_name": acc.mp_name,
                "published_at": str(art.published_at),
                "is_opportunity": opp.is_opportunity,
                "confidence": opp.confidence,
                "opp_type": opp.opp_type,
                "opp_name": opp.opp_name,
                "deadline_display": opp.deadline_display,
                "verdict": "✅ 机会" if opp.is_opportunity else "❌ 非机会",
                "original_url": art.original_url,
            })

    elif task_type == "campus":
        results = db.query(CampusInfo, Article, MonitoredAccount).join(
            Article, CampusInfo.article_id == Article.id
        ).join(
            MonitoredAccount, Article.werss_mp_id == MonitoredAccount.werss_mp_id
        ).order_by(Article.published_at.desc()).limit(50).all()

        for ci, art, acc in results:
            is_valid = ci.event_type in VALID_CAMPUS_TYPES if ci.event_type else False
            out.append({
                "title": art.title,
                "mp_name": acc.mp_name,
                "published_at": str(art.published_at),
                "event_type": ci.event_type,
                "event_date": str(ci.event_date) if ci.event_date else None,
                "location": ci.location,
                "organizer": ci.organizer,
                "verdict": f"✅ {ci.event_type}" if is_valid else "➖ 非活动/新闻",
                "original_url": art.original_url,
            })

    return {"total": len(out), "results": out}
