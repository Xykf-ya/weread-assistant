"""通知与健康检查 API"""

from fastapi import APIRouter, Depends

from app.services.notifier import send_feishu_test
from app.services.werss import WeRSSClient
from app.services.ai import check_deepseek_health, check_dashscope_health
from app.schemas import HealthStatus

router = APIRouter(prefix="/api", tags=["alerts"])


@router.post("/alerts/test")
async def test_feishu():
    """发送飞书测试通知"""
    success = await send_feishu_test()
    if success:
        return {"code": 0, "message": "测试消息已发送，请检查飞书群"}
    else:
        return {"code": 1, "message": "发送失败，请检查 FEISHU_WEBHOOK_URL 配置"}


@router.get("/health", response_model=HealthStatus)
async def health_check():
    """系统健康检查"""
    werss = WeRSSClient()
    status = HealthStatus()

    # WeRSS
    try:
        werss_ok = await werss.health_check()
        status.werss = "ok" if werss_ok else "unreachable"
    except Exception:
        status.werss = "error"

    # DeepSeek
    try:
        ds_ok = await check_deepseek_health()
        status.deepseek = "ok" if ds_ok else "auth_error"
    except Exception:
        status.deepseek = "error"

    # DashScope
    try:
        ds_ok = await check_dashscope_health()
        status.dashscope = "ok" if ds_ok else "auth_error"
    except Exception:
        status.dashscope = "error"

    # 飞书
    from app.config import settings
    status.feishu = "configured" if settings.feishu_webhook_url else "not_configured"

    # 总体状态
    if status.werss != "ok":
        status.status = "degraded"
    if status.deepseek != "ok" and status.dashscope != "ok":
        status.status = "no_ai_available"

    return status
