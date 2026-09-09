from __future__ import annotations

import re

from app.http_client import PlatformClient
from app.models import ParsedMedia
from app.parsers.common import first_url, load_embedded_json, walk_dicts


MOBILE_UA = "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 Version/16.0 Mobile/15E148 Safari/604.1"


async def parse_douyin(url: str, client: PlatformClient) -> ParsedMedia:
    headers = {"User-Agent": MOBILE_UA, "Accept-Language": "zh-CN,zh;q=0.9"}
    resolved = await client.resolve(url, headers)
    match = re.search(r"/(?:video|note)/(\d+)", resolved)
    if not match:
        match = re.search(r"(\d{15,22})", resolved)
    if not match:
        raise ValueError("无法从抖音链接识别作品 ID")
    item_id = match.group(1)

    candidates = [resolved, f"https://www.iesdouyin.com/share/video/{item_id}"]
    data = None
    for page_url in candidates:
        try:
            html = await client.get_text(page_url, headers)
            data = load_embedded_json(html, "window._ROUTER_DATA")
            break
        except (ValueError, KeyError):
            continue
    if data is None:
        raise ValueError("抖音页面未返回可解析的作品数据")

    items = [
        item
        for item in walk_dicts(data)
        if isinstance(item.get("video"), dict) and (item.get("aweme_id") or item.get("desc") is not None)
    ]
    item = next((value for value in items if str(value.get("aweme_id")) == item_id), items[0] if items else None)
    if not item:
        raise ValueError("抖音作品数据缺少视频信息")

    video = item["video"]
    play_addr = video.get("play_addr") or video.get("playAddr") or {}
    uri = play_addr.get("uri") if isinstance(play_addr, dict) else None
    if uri:
        media_url = f"https://www.iesdouyin.com/aweme/v1/play/?video_id={uri}&ratio=1080p&line=0"
    else:
        media_url = first_url(play_addr)
    if not media_url:
        raise ValueError("抖音作品没有可用的视频地址")

    cover = first_url(video.get("cover")) or first_url(video.get("origin_cover"))
    title = str(item.get("desc") or f"抖音作品_{item_id}").strip()
    author = item.get("author") or {}
    stats = item.get("statistics") or {}
    return ParsedMedia(
        platform="douyin",
        item_id=item_id,
        title=title,
        cover_url=cover,
        media_urls=[("video", media_url)],
        headers={"User-Agent": MOBILE_UA, "Referer": resolved},
        author_name=str(author.get("nickname") or ""),
        counts={label: str(stats[key]) for label, key in (
            ("likes", "digg_count"), ("favorites", "collect_count"),
            ("comments", "comment_count"), ("shares", "share_count"),
        ) if stats.get(key) not in (None, "")},
    )

