"""公众号管理 API"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import MonitoredAccount
from app.schemas import AccountCreate, AccountUpdate, AccountOut
from app.services.werss import WeRSSClient

router = APIRouter(prefix="/api/accounts", tags=["accounts"])


@router.get("", response_model=list[AccountOut])
async def list_accounts(
    account_type: str | None = None,
    is_active: bool | None = None,
    db: Session = Depends(get_db),
):
    """获取公众号列表"""
    query = db.query(MonitoredAccount).filter(MonitoredAccount.is_active == True)
    if account_type:
        query = query.filter(MonitoredAccount.account_type == account_type)
    return query.order_by(MonitoredAccount.created_at.desc()).all()


@router.post("", response_model=AccountOut)
async def create_account(data: AccountCreate, db: Session = Depends(get_db)):
    """添加监控公众号"""
    existing = db.query(MonitoredAccount).filter(
        MonitoredAccount.werss_mp_id == data.werss_mp_id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="该公众号已存在")

    acc = MonitoredAccount(
        werss_mp_id=data.werss_mp_id,
        mp_name=data.mp_name,
        cover_url=data.cover_url,
        account_type=data.account_type,
        tags=data.tags or "[]",
    )
    db.add(acc)
    db.commit()
    db.refresh(acc)
    return acc


@router.put("/{account_id}", response_model=AccountOut)
async def update_account(account_id: int, data: AccountUpdate, db: Session = Depends(get_db)):
    """更新公众号设置"""
    acc = db.query(MonitoredAccount).filter(MonitoredAccount.id == account_id).first()
    if not acc:
        raise HTTPException(status_code=404, detail="公众号不存在")

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(acc, key, value)

    db.commit()
    db.refresh(acc)
    return acc


@router.delete("/{account_id}")
async def delete_account(account_id: int, db: Session = Depends(get_db)):
    """删除监控公众号（软删除，设 is_active=False）"""
    acc = db.query(MonitoredAccount).filter(MonitoredAccount.id == account_id).first()
    if not acc:
        raise HTTPException(status_code=404, detail="公众号不存在")

    acc.is_active = False
    db.commit()
    return {"code": 0, "message": "已停用"}


@router.post("/sync-from-werss")
async def sync_accounts_from_werss(db: Session = Depends(get_db)):
    """从 WeRSS 一键导入已订阅的公众号"""
    werss = WeRSSClient()
    try:
        werss_mps = await werss.get_subscribed_mps()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"无法连接 WeRSS: {e}")

    if not werss_mps:
        return {"code": 0, "message": "WeRSS 中没有已订阅的公众号", "added": 0, "accounts": []}

    added = []
    skipped = []
    for mp in werss_mps:
        werss_mp_id = str(mp.get("id", "") or mp.get("fakeid", ""))
        if not werss_mp_id:
            continue

        # 检查是否已存在
        existing = db.query(MonitoredAccount).filter(
            MonitoredAccount.werss_mp_id == werss_mp_id
        ).first()
        if existing:
            skipped.append({"name": mp.get("mp_name", "未知"), "reason": "已存在"})
            continue

        # 新建（默认设为 opportunity 类型，用户可在前端修改）
        acc = MonitoredAccount(
            werss_mp_id=werss_mp_id,
            mp_name=mp.get("mp_name", "未知"),
            cover_url=mp.get("mp_cover"),
            account_type="opportunity",
            tags="[]",
        )
        db.add(acc)
        added.append(acc.mp_name)

    db.commit()

    return {
        "code": 0,
        "message": f"导入完成：新增 {len(added)} 个，跳过 {len(skipped)} 个（已存在）",
        "added": len(added),
        "skipped": len(skipped),
        "added_names": added,
        "skipped_names": [s["name"] for s in skipped],
    }
