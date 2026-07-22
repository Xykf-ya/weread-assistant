"""阅读状态管理 API (P2)

阅读状态相关的 API 已整合到 articles.py 中（PUT /api/articles/{id}/reading-state）。
本模块保留为占位，供后续 P2 扩展使用。
"""

from fastapi import APIRouter

router = APIRouter(tags=["reading"])
