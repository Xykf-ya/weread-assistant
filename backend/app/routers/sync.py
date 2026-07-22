"""同步 + AI 处理 API"""

import logging
from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import MonitoredAccount, Article, Opportunity, CampusInfo, AlertLog
from app.schemas import SyncResult
from app.services.werss import WeRSSClient, strip_html, extract_images, is_image_article
from app.services.ai import classify_article
from app.services.notifier import send_feishu_opportunity
from app.services.scheduler import should_sync, mark_synced

router = APIRouter(prefix="/api", tags=["sync"])
logger = logging.getLogger(__name__)

werss = WeRSSClient()


@router.post("/sync", response_model=SyncResult)
async def sync_articles(db: Session = Depends(get_db)):
    """手动触发同步：从 WeRSS 拉取新文章 → AI 处理 → 发送通知"""
    result = SyncResult()

    # 获取所有活跃的监控公众号
    accounts = db.query(MonitoredAccount).filter(MonitoredAccount.is_active == True).all()
    if not accounts:
        result.errors.append("没有配置任何监控公众号，请先在设置中添加")
        return result

    # 按类型分组，检查是否到了同步时间
    accounts_to_sync = []
    for acc in accounts:
        if should_sync(acc.account_type):
            accounts_to_sync.append(acc)

    if not accounts_to_sync:
        result.errors.append("所有类型都还没到同步时间")
        return result

    # 为每个需要同步的公众号拉取文章
    for acc in accounts_to_sync:
        try:
            articles = await werss.get_articles(feed_id=acc.werss_mp_id, limit=20)
            result.total_fetched += len(articles)

            for art_data in articles:
                werss_art_id = str(art_data.get("id", ""))
                if not werss_art_id:
                    continue

                # 去重：检查是否已存在
                existing = db.query(Article).filter(
                    Article.werss_article_id == werss_art_id
                ).first()
                if existing:
                    continue

                # 获取文章详情（含正文）
                detail = await werss.get_article_detail(werss_art_id)
                raw_content = detail.get("content", "") if detail else ""

                # 解析发布时间
                published_at_str = art_data.get("publish_time") or art_data.get("create_time", "")
                try:
                    published_at = datetime.fromisoformat(published_at_str.replace("Z", "+00:00"))
                except (ValueError, AttributeError):
                    published_at = datetime.now()

                # 入库
                article = Article(
                    werss_article_id=werss_art_id,
                    werss_mp_id=acc.werss_mp_id,
                    title=art_data.get("title", "无标题"),
                    author=art_data.get("author"),
                    summary=art_data.get("digest") or art_data.get("summary"),
                    cover_url=art_data.get("cover_url") or art_data.get("cover"),
                    original_url=art_data.get("content_url") or art_data.get("url", ""),
                    raw_content=raw_content,
                    published_at=published_at,
                    ai_processed=False,
                )
                db.add(article)
                result.new_articles += 1

            db.commit()

            # 标记该类型已同步
            mark_synced(acc.account_type)

        except Exception as e:
            logger.error(f"Failed to sync account {acc.mp_name} ({acc.werss_mp_id}): {e}")
            result.errors.append(f"{acc.mp_name}: {str(e)}")

    # AI 处理新文章（按类型分流）
    pending = db.query(Article).filter(Article.ai_processed == False).all()

    for article in pending:
        # 找到对应的公众号
        acc = db.query(MonitoredAccount).filter(
            MonitoredAccount.werss_mp_id == article.werss_mp_id
        ).first()
        if not acc:
            continue

        # NEWS 和 INTEREST 类型跳过 AI
        if acc.account_type in ("news", "interest"):
            article.ai_processed = True
            db.commit()
            continue

        # 判断文章类型
        img = is_image_article(article.raw_content)
        img_urls = extract_images(article.raw_content) if img else []

        try:
            ai_result = await classify_article(
                title=article.title,
                raw_content=article.raw_content or "",
                is_image=img,
                image_urls=img_urls,
                task="opportunity" if acc.account_type == "opportunity" else "campus",
            )

            meta = ai_result.pop("_meta", {})

            if acc.account_type == "opportunity":
                # 存入 Opportunity 表
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

                # 发送通知
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

            elif acc.account_type == "campus":
                # 存入 CampusInfo 表
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
            result.errors.append(f"AI处理失败 (文章 {article.id}): {str(e)}")

    return result
