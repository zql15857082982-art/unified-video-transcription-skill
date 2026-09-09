from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class ParsedMedia:
    platform: str
    item_id: str
    title: str
    cover_url: str | None
    media_urls: list[tuple[str, str]]
    headers: dict[str, str] = field(default_factory=dict)
    author_name: str = ""
    author_avatar_url: str = ""
    counts: dict[str, str] = field(default_factory=dict)
    expires_at: str | None = None
    resolver: str = ""
