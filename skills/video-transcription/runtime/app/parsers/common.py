from __future__ import annotations

import json
import re
from collections.abc import Iterator
from typing import Any


def extract_balanced_object(text: str, marker: str) -> str:
    marker_index = text.find(marker)
    if marker_index < 0:
        raise ValueError("页面中没有找到作品数据")
    start = text.find("{", marker_index + len(marker))
    if start < 0:
        raise ValueError("作品数据格式错误")
    depth = 0
    quoted = False
    escaped = False
    for index in range(start, len(text)):
        char = text[index]
        if quoted:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                quoted = False
            continue
        if char == '"':
            quoted = True
        elif char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return text[start : index + 1]
    raise ValueError("作品数据不完整")


def load_embedded_json(text: str, marker: str) -> dict:
    raw = extract_balanced_object(text, marker)
    raw = re.sub(r"(?<=:)undefined(?=\s*[,}])", "null", raw)
    return json.loads(raw)


def walk_dicts(value: Any) -> Iterator[dict]:
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from walk_dicts(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk_dicts(child)


def first_url(value: Any) -> str | None:
    if isinstance(value, str) and value.startswith(("http://", "https://")):
        return value
    if isinstance(value, list):
        for item in value:
            found = first_url(item)
            if found:
                return found
    if isinstance(value, dict):
        for key in ("urlDefault", "masterUrl", "url", "url_list", "backupUrls"):
            if key in value:
                found = first_url(value[key])
                if found:
                    return found
        for child in value.values():
            found = first_url(child)
            if found:
                return found
    return None
