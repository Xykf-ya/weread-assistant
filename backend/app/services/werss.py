"""WeRSS API 客户端"""

import time
import httpx
from bs4 import BeautifulSoup
from app.config import settings


class WeRSSClient:
    """封装 WeRSS REST API 调用"""

    def __init__(self):
        self.base_url = settings.werss_base_url.rstrip("/")
        self.username = settings.werss_username
        self.password = settings.werss_password
        self._token: str | None = None
        self._token_expiry: float = 0

    async def _ensure_auth(self, client: httpx.AsyncClient):
        """获取或刷新 JWT token"""
        if self._token and time.time() < self._token_expiry - 60:
            return

        resp = await client.post(
            f"{self.base_url}/api/v1/wx/auth/login",
            data={"username": self.username, "password": self.password},
        )
        resp.raise_for_status()
        data = resp.json()
        if data.get("code") == 0 and data.get("data", {}).get("access_token"):
            self._token = data["data"]["access_token"]
            self._token_expiry = time.time() + 3600  # WeRSS token 一般 1 小时有效
        else:
            raise RuntimeError(f"WeRSS login failed: {data.get('message', 'unknown error')}")

    async def _client(self) -> httpx.AsyncClient:
        """创建带认证的 HTTP 客户端"""
        client = httpx.AsyncClient(timeout=30.0)
        await self._ensure_auth(client)
        client.headers["Authorization"] = f"Bearer {self._token}"
        return client

    async def get_articles(
        self, feed_id: str | None = None, limit: int = 50, offset: int = 0
    ) -> list[dict]:
        """获取文章列表

        Args:
            feed_id: 公众号 ID（WeRSS 内部 ID），None 表示获取所有
            limit: 每页数量
            offset: 偏移量
        """
        client = await self._client()
        try:
            params = {"limit": limit, "offset": offset}
            if feed_id:
                params["feed_id"] = feed_id
            resp = await client.get(f"{self.base_url}/api/v1/wx/articles", params=params)
            resp.raise_for_status()
            data = resp.json()
            if data.get("code") == 0:
                return data.get("data", {}).get("list", [])
            return []
        finally:
            await client.aclose()

    async def get_article_detail(self, article_id: str) -> dict | None:
        """获取文章详情（含正文 HTML）

        Args:
            article_id: WeRSS 内部文章 ID
        """
        client = await self._client()
        try:
            resp = await client.get(f"{self.base_url}/api/v1/wx/articles/{article_id}")
            resp.raise_for_status()
            data = resp.json()
            if data.get("code") == 0:
                return data.get("data", {})
            return None
        finally:
            await client.aclose()

    async def get_subscribed_mps(self) -> list[dict]:
        """获取已订阅的公众号列表"""
        client = await self._client()
        try:
            resp = await client.get(f"{self.base_url}/api/v1/wx/mps")
            resp.raise_for_status()
            data = resp.json()
            if data.get("code") == 0:
                return data.get("data", {}).get("list", [])
            return []
        finally:
            await client.aclose()

    async def health_check(self) -> bool:
        """检查 WeRSS 是否可达"""
        try:
            client = httpx.AsyncClient(timeout=10.0)
            resp = await client.get(f"{self.base_url}/api/v1/health")
            await client.aclose()
            return resp.status_code == 200
        except Exception:
            return False


def strip_html(html: str) -> str:
    """去掉 HTML 标签，提取纯文本"""
    if not html:
        return ""
    soup = BeautifulSoup(html, "html.parser")
    return soup.get_text(separator="\n", strip=True)


def extract_images(html: str) -> list[str]:
    """从 HTML 中提取图片 URL 列表"""
    if not html:
        return []
    soup = BeautifulSoup(html, "html.parser")
    return [img.get("src") for img in soup.find_all("img") if img.get("src")]


def is_image_article(raw_content: str) -> bool:
    """判断文章是否为图片形式（长图）"""
    if not raw_content:
        return True
    text = strip_html(raw_content)
    return len(text.strip()) < 100
