from __future__ import annotations

from urllib.parse import urljoin, urlparse

import httpx

from app.config import settings
from app.security import validate_platform_url, host_matches


PLATFORM_GROUPS = (
    {"douyin.com", "iesdouyin.com"},
    {"kuaishou.com", "kuaishou.cn", "m.chenzhongtech.com", "m.gifshow.com"},
    {"xiaohongshu.com", "xhslink.com"},
    {"weixin.qq.com"},
)


class PlatformClient:
    def __init__(self) -> None:
        self.client = httpx.AsyncClient(
            timeout=httpx.Timeout(settings.request_timeout),
            verify=True,
            follow_redirects=False,
        )

    async def close(self) -> None:
        await self.client.aclose()

    async def resolve(self, url: str, headers: dict[str, str]) -> str:
        current = validate_platform_url(url)
        group = next(group for group in PLATFORM_GROUPS if host_matches(urlparse(current).hostname, group))
        for _ in range(6):
            response = await self.client.get(current, headers=headers)
            if response.status_code not in {301, 302, 303, 307, 308}:
                return str(response.url)
            location = response.headers.get("location")
            if not location:
                return current
            current = validate_platform_url(urljoin(current, location))
            if not host_matches(urlparse(current).hostname, group):
                raise ValueError("分享链接跳转到另一个平台，已停止传递登录状态")
        raise ValueError("分享链接重定向次数过多")

    async def get_text(self, url: str, headers: dict[str, str]) -> str:
        async with self.client.stream("GET", validate_platform_url(url), headers=headers) as response:
            response.raise_for_status()
            content = bytearray()
            async for chunk in response.aiter_bytes():
                content.extend(chunk)
                if len(content) > settings.max_html_bytes:
                    raise ValueError("页面内容超过解析限制")
            return content.decode(response.encoding or "utf-8", errors="replace")

    async def post_json(
        self, url: str, body: dict, headers: dict[str, str] | None = None
    ) -> dict:
        response = await self.client.post(url, json=body, headers=headers)
        response.raise_for_status()
        return response.json()
