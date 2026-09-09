import pytest
from app.models import ParsedMedia
from report import make_result, render_html, render_markdown
from transcribe import write_reports


def sample():
    parsed = ParsedMedia(platform="weixin", item_id="test-id", title='标题 <script>alert(1)</script>',
                         cover_url="https://example.com/cover.jpg", media_urls=[("video", "https://example.com/v.mp4?a=1&b=2")],
                         author_name="作者", counts={"likes": "0", "comments": "17", "shares": ""},
                         headers={"Cookie": "private-cookie"}, expires_at="2030-01-01T00:00:00+00:00")
    return make_result(parsed, "https://weixin.qq.com/sph/example", "第一段。\n\n第二段。")


def test_reports_keep_zero_missing_counts_and_direct_urls_distinct(tmp_path):
    result = sample()
    paths = write_reports(result, tmp_path / "文稿.html")
    assert len(paths) == 1
    html = paths[0].read_text(encoding="utf-8")
    markdown = render_markdown(result)
    assert "| 点赞 | 0 |" in markdown
    assert "| 评论 | 17 |" in markdown
    assert "| 分享 |" not in markdown
    assert "https://example.com/v.mp4?a=1&b=2" in markdown
    assert 'href="https://example.com/v.mp4?a=1&amp;b=2"' in html
    assert "2030-01-01" in html and "2030-01-01" in markdown
    assert "第一段。\n\n第二段。" in markdown
    assert "private-cookie" not in markdown + html
    assert "<script>" not in html and "&lt;script&gt;" in html


def test_reports_reject_active_url_schemes():
    result = sample()
    result["source_url"] = "javascript:alert(1)"
    result["media_urls"] = [("video", "data:text/html,bad")]
    result["cover_url"] = "javascript:alert(2)"
    for content in (render_markdown(result), render_html(result)):
        assert "javascript:" not in content
        assert "data:text/html" not in content


def test_html_only_avoids_extra_file(tmp_path):
    paths = write_reports(sample(), tmp_path / "only.html")
    assert len(paths) == 1
    assert not (tmp_path / "only.md").exists()
    with pytest.raises(ValueError, match="html"):
        write_reports(sample(), tmp_path / "invalid.md")
