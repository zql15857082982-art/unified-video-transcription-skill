"""Local reports; platform data is rendered as text, never executable markup."""
from datetime import datetime
from html import escape
from urllib.parse import urlsplit, quote

PLATFORMS = {"weixin": "视频号", "douyin": "抖音", "kuaishou": "快手", "xiaohongshu": "小红书"}
COUNTS = {"views": "播放", "likes": "点赞", "favorites": "收藏", "comments": "评论", "shares": "分享"}


def safe_url(value):
    value = str(value or "")
    try:
        parsed = urlsplit(value)
        return value if parsed.scheme in {"http", "https"} and parsed.hostname and not parsed.username and not parsed.password else ""
    except ValueError:
        return ""


def md_text(value):
    text = escape(str(value), quote=False).replace("\r", " ").replace("\n", " ")
    for char in "\\`*_{}[]()#+.!|":
        text = text.replace(char, "\\" + char)
    return text


def md_link(label, url):
    url = safe_url(url)
    return f"[{label}](<{quote(url, safe=':/?&=%#@+;,~!$*-._')}>)" if url else ""


def metadata(result):
    rows = [("平台", PLATFORMS.get(result["platform"], result["platform"]))]
    if result.get("author_name"):
        rows.append(("作者", result["author_name"]))
    rows.append(("作品 ID", result["item_id"]))
    if result.get("captured_at"):
        rows.append(("信息获取时间", result["captured_at"]))
    if result.get("expires_at"):
        rows.append(("平台返回的链接到期时间", result["expires_at"]))
    return rows


def available_counts(result):
    return [(label, result.get("counts", {}).get(key)) for key, label in COUNTS.items()
            if result.get("counts", {}).get(key) not in (None, "")]


def make_result(parsed, source_url, transcript):
    return {"platform": parsed.platform, "item_id": parsed.item_id, "title": parsed.title,
            "author_name": parsed.author_name, "source_url": source_url, "transcript": transcript,
            "cover_url": parsed.cover_url, "media_urls": parsed.media_urls, "counts": parsed.counts,
            "expires_at": parsed.expires_at, "captured_at": datetime.now().astimezone().isoformat(timespec="seconds"),
            "needs_headers": bool(parsed.headers)}


def link_note(result):
    note = "解析后的地址可能过期；失效时需重新解析原链接。"
    if result.get("needs_headers"):
        note += "此平台下载可能需要原站访问来源或登录状态，浏览器直接打开不一定成功。"
    return note


def render_markdown(result):
    rows = ["# 视频转写", "", "## 视频信息", "", md_text(result["title"]), ""]
    rows.extend(f"- {label}：{md_text(value)}" for label, value in metadata(result))
    rows.extend(["", "## 视频数据", ""])
    counts = available_counts(result)
    if counts:
        rows.extend(["| 指标 | 数值 |", "| --- | --- |"])
        rows.extend(f"| {label} | {md_text(value)} |" for label, value in counts)
    else:
        rows.append("平台未返回互动数据。")
    rows.extend(["", "仅列出平台实际返回的数据；未返回的项目不按 0 计算。数据为获取时的快照。", "", "## 链接与下载", ""])
    rows.append("- " + md_link("打开原视频页面", result["source_url"]))
    for index, (kind, url) in enumerate(result.get("media_urls", []), 1):
        if safe_url(url):
            rows.append("- " + md_link(f"{'视频' if kind == 'video' else '媒体'}地址 {index}（打开 / 下载）", url))
    if safe_url(result.get("cover_url")):
        rows.append("- " + md_link("查看 / 下载原视频封面", result["cover_url"]))
    rows.extend(["", link_note(result), "", "## 文稿", "", result["transcript"], ""])
    return "\n".join(rows)


def render_html(result):
    def a(label, url, primary=False):
        url = safe_url(url)
        return f'<a class="button {"primary" if primary else ""}" href="{escape(url, quote=True)}" target="_blank" rel="noopener noreferrer">{escape(label)}</a>' if url else ""
    links = a("打开原视频", result["source_url"])
    for i, (kind, url) in enumerate(result.get("media_urls", []), 1):
        links += a(f"{'视频' if kind == 'video' else '媒体'}地址 {i} · 打开 / 下载", url, True)
    links += a("查看封面", result.get("cover_url"))
    stats = "".join(f'<div class="stat"><strong>{escape(str(value))}</strong><span>{label}</span></div>' for label, value in available_counts(result))
    if not stats:
        stats = '<p class="muted">平台未返回互动数据。</p>'
    meta = "".join(f'<dt>{label}</dt><dd>{escape(str(value))}</dd>' for label, value in metadata(result))
    paragraphs = "".join(f'<p>{escape(p).replace(chr(10), "<br>")}</p>' for p in result["transcript"].split("\n\n") if p.strip())
    return f'''<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>视频转写 · {escape(result['author_name'] or '文稿')}</title>
<style>
:root{{color-scheme:light;--ink:#19312c;--muted:#65746b;--line:#dce3da;--accent:#236a51}}
*{{box-sizing:border-box}}body{{margin:0;background:#f3f4ee;color:var(--ink);font:16px/1.75 system-ui,-apple-system,"Segoe UI","Microsoft YaHei",sans-serif}}
main{{max-width:960px;margin:48px auto;padding:0 24px}}.eyebrow{{color:var(--accent);font-size:12px;letter-spacing:.18em;font-weight:700}}
h1{{font-size:38px;line-height:1.25;letter-spacing:-.03em;margin:12px 0}}.description{{max-width:800px;color:#53635b;font-size:16px}}
.card{{background:#fff;border:1px solid var(--line);border-radius:18px;padding:28px;margin:22px 0}}h2{{font-size:19px;margin:0 0 18px}}.stats{{display:flex;flex-wrap:wrap;gap:24px}}.stat{{min-width:100px}}.stat strong{{display:block;font-size:27px;font-weight:600}}.stat span,.muted{{color:var(--muted);font-size:13px}}
.links{{display:flex;flex-wrap:wrap;gap:10px}}.button{{display:inline-block;border:1px solid var(--line);border-radius:8px;padding:9px 14px;text-decoration:none;color:var(--ink);font-size:14px}}.primary{{background:var(--accent);color:white;border-color:var(--accent)}}a:focus-visible{{outline:3px solid #ce9a24;outline-offset:3px}}
dl{{display:grid;grid-template-columns:180px 1fr;gap:10px 20px;font-size:13px}}dt{{color:var(--muted)}}dd{{margin:0;overflow-wrap:anywhere}}.transcript p{{font-size:19px;line-height:2;white-space:normal;margin:0 0 20px}}.transcript p:last-child{{margin-bottom:0}}footer{{color:var(--muted);font-size:12px;margin:26px 0}}
@media(max-width:600px){{main{{margin:28px auto;padding:0 16px}}h1{{font-size:30px}}.card{{padding:20px}}dl{{grid-template-columns:1fr;gap:4px}}dd{{margin-bottom:10px}}.transcript p{{font-size:17px}}}}
@media print{{body{{background:#fff}}main{{margin:0;max-width:none}}.card{{break-inside:avoid}}.button{{border:0;padding:0}}}}
</style></head><body><main>
<header><div class="eyebrow">VIDEO TRANSCRIPT / 视频转写</div><h1>{escape(result['author_name'] or '视频文稿')}</h1><p class="description">{escape(result['title'])}</p></header>
<section class="card"><h2>视频数据</h2><div class="stats">{stats}</div><p class="muted">仅展示平台实际返回的数据；未返回项目不按 0 计算。数据为获取时的快照。</p></section>
<section class="card transcript"><h2>转写正文</h2>{paragraphs}</section>
<section class="card"><h2>链接与下载</h2><div class="links">{links}</div><p class="muted">{escape(link_note(result))} 打开视频后可使用浏览器的保存功能。</p></section>
<section class="card"><h2>来源信息</h2><dl>{meta}</dl></section>
<footer>本地生成 · 正文保留转写原文 · 外部视频及封面需联网打开</footer>
</main></body></html>'''
