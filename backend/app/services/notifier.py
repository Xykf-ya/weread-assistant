"""通知服务：飞书群机器人 Webhook + 可选邮件"""

import json
import httpx
from datetime import date

from app.config import settings


FEISHU_CARD_TEMPLATE = {
    "msg_type": "interactive",
    "card": {
        "header": {
            "title": {"content": "", "tag": "plain_text"},
            "template": "blue",
        },
        "elements": [],
    },
}

OPP_TYPE_EMOJI = {
    "job": "💼",
    "internship": "📋",
    "competition": "🏆",
    "camp": "🏕️",
    "volunteer": "🤝",
    "registration": "📝",
    "other": "📌",
}

OPP_TYPE_LABEL = {
    "job": "招聘",
    "internship": "实习",
    "competition": "比赛",
    "camp": "训练营/夏校",
    "volunteer": "志愿活动",
    "registration": "报名/招募",
    "other": "其他机会",
}


async def send_feishu_opportunity(
    opp_name: str,
    opp_type: str,
    mp_name: str,
    published_at: str,
    deadline_display: str | None,
    target_audience: str | None,
    summary: str | None,
    original_url: str,
) -> bool:
    """发送飞书机会提醒消息卡片

    Returns:
        是否发送成功
    """
    if not settings.feishu_webhook_url:
        return False

    emoji = OPP_TYPE_EMOJI.get(opp_type, "📌")
    type_label = OPP_TYPE_LABEL.get(opp_type, "其他机会")

    # 构建消息内容
    lines = [f"**{opp_name}**", ""]
    if deadline_display:
        lines.append(f"⏰ 截止: {deadline_display}")
    if target_audience:
        lines.append(f"👥 面向: {target_audience}")
    if summary:
        lines.append(f"📝 {summary}")

    markdown_content = "\n".join(lines)

    card = {
        "msg_type": "interactive",
        "card": {
            "header": {
                "title": {"content": f"{emoji} {type_label}机会", "tag": "plain_text"},
                "template": "blue",
            },
            "elements": [
                {"tag": "markdown", "content": markdown_content},
                {"tag": "hr"},
                {
                    "tag": "note",
                    "elements": [
                        {"tag": "plain_text", "content": f"来源: {mp_name} | 发布于 {published_at}"}
                    ],
                },
                {
                    "tag": "action",
                    "elements": [
                        {
                            "tag": "button",
                            "text": {"tag": "plain_text", "content": "查看原文"},
                            "type": "default",
                            "url": original_url,
                        }
                    ],
                },
            ],
        },
    }

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(
                settings.feishu_webhook_url,
                json=card,
                headers={"Content-Type": "application/json"},
            )
            resp.raise_for_status()
            result = resp.json()
            return result.get("code") == 0 or result.get("StatusCode") == 0
    except Exception:
        return False


async def send_feishu_test() -> bool:
    """发送飞书测试消息"""
    if not settings.feishu_webhook_url:
        return False

    card = {
        "msg_type": "interactive",
        "card": {
            "header": {
                "title": {"content": "✅ 公众号助手通知测试", "tag": "plain_text"},
                "template": "green",
            },
            "elements": [
                {"tag": "markdown", "content": "如果你收到这条消息，说明飞书通知配置正确。\n\n系统将在发现新的机会信息时自动推送通知。"},
            ],
        },
    }

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(
                settings.feishu_webhook_url,
                json=card,
                headers={"Content-Type": "application/json"},
            )
            resp.raise_for_status()
            return True
    except Exception:
        return False
