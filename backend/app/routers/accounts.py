"""公众号管理 API"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import MonitoredAccount
from app.schemas import AccountCreate, AccountUpdate, AccountOut

router = APIRouter(prefix="/api/accounts", tags=["accounts"])


@router.get("", response_model=list[AccountOut])
async def list_accounts(
    account_type: str | None = None,
    is_active: bool | None = None,
    db: Session = Depends(get_db),
):
    """获取公众号列表"""
    query = db.query(MonitoredAccount)
    if account_type:
        query = query.filter(MonitoredAccount.account_type == account_type)
    if is_active is not None:
        query = query.filter(MonitoredAccount.is_active == is_active)
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
