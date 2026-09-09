from __future__ import annotations

import os
import secrets
from dataclasses import dataclass


def _csv(name: str) -> tuple[str, ...]:
    return tuple(item.strip() for item in os.getenv(name, "").split(",") if item.strip())


@dataclass(frozen=True)
class Settings:
    environment: str
    app_secret: str
    api_key: str
    allowed_origins: tuple[str, ...]
    xhs_cookie: str
    kuaishou_cookie: str
    yuanbao_cookie: str
    weixin_worker_fallback: bool
    request_timeout: float
    token_ttl: int
    max_html_bytes: int
    max_download_bytes: int
    max_download_seconds: int
    max_concurrent_downloads: int
    agent_token: str
    max_queued_jobs: int
    job_db_path: str


def load_settings() -> Settings:
    environment = os.getenv("ENVIRONMENT", "development").strip().lower()
    secret = os.getenv("APP_SECRET", "").strip()
    if environment == "production" and (
        len(secret) < 32 or secret == "change-this-to-a-long-random-secret"
    ):
        raise RuntimeError("生产环境必须配置至少 32 个字符的 APP_SECRET")
    if not secret:
        secret = secrets.token_urlsafe(32)
    agent_token = os.getenv("AGENT_TOKEN", "").strip()
    if environment == "production" and len(agent_token) < 32:
        raise RuntimeError("生产环境必须配置至少 32 个字符的 AGENT_TOKEN")
    if not agent_token:
        agent_token = "development-agent-token"
    return Settings(
        environment=environment,
        app_secret=secret,
        api_key=os.getenv("API_KEY", "").strip(),
        allowed_origins=_csv("ALLOWED_ORIGINS"),
        xhs_cookie=os.getenv("XHS_COOKIE", "").strip(),
        kuaishou_cookie=os.getenv("KUAISHOU_COOKIE", "").strip(),
        yuanbao_cookie=os.getenv("YUANBAO_COOKIE", "").strip(),
        weixin_worker_fallback=os.getenv("WEIXIN_WORKER_FALLBACK", "false").strip().lower()
        in {"1", "true", "yes"},
        request_timeout=float(os.getenv("REQUEST_TIMEOUT", "15")),
        token_ttl=int(os.getenv("DOWNLOAD_TOKEN_TTL", "900")),
        max_html_bytes=int(os.getenv("MAX_HTML_BYTES", str(5 * 1024 * 1024))),
        max_download_bytes=int(os.getenv("MAX_DOWNLOAD_BYTES", str(2 * 1024 * 1024 * 1024))),
        max_download_seconds=int(os.getenv("MAX_DOWNLOAD_SECONDS", "600")),
        max_concurrent_downloads=int(os.getenv("MAX_CONCURRENT_DOWNLOADS", "4")),
        agent_token=agent_token,
        max_queued_jobs=int(os.getenv("MAX_QUEUED_JOBS", "30")),
        job_db_path=os.getenv("JOB_DB_PATH", "").strip(),
    )


settings = load_settings()
