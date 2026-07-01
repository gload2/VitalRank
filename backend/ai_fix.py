import html as html_lib
import os
import re

import httpx

from shared.url_guard import is_safe_public_url

LLM_BASE_URL = os.getenv("LLM_BASE_URL", "http://host.docker.internal:11434").rstrip("/")
LLM_MODEL = os.getenv("LLM_MODEL", "qwen2.5:3b")
LLM_TIMEOUT = float(os.getenv("LLM_TIMEOUT", "120"))
PAGE_FETCH_TIMEOUT = float(os.getenv("PAGE_FETCH_TIMEOUT", "10"))
MAX_HTML_BYTES = 400_000


class LLMUnavailable(Exception):
    """Локальная модель недоступна (Ollama не запущен / модель не скачана)."""


def _clean(s: str) -> str:
    return re.sub(r"\s+", " ", html_lib.unescape(s)).strip()


def _extract_context(html_text: str) -> dict:
    def first(pattern: str) -> str:
        m = re.search(pattern, html_text, re.I | re.S)
        return _clean(m.group(1)) if m else ""

    title = first(r"<title[^>]*>(.*?)</title>")
    h1 = first(r"<h1[^>]*>(.*?)</h1>")

    meta_desc = ""
    m = re.search(r'<meta[^>]+name=["\']description["\'][^>]*>', html_text, re.I)
    if m:
        c = re.search(r'content=["\'](.*?)["\']', m.group(0), re.I | re.S)
        meta_desc = _clean(c.group(1)) if c else ""

    body = re.sub(r"(?is)<(script|style|noscript)[^>]*>.*?</\1>", " ", html_text)
    body = re.sub(r"(?s)<[^>]+>", " ", body)
    text = _clean(body)[:1500]

    return {"title": title, "h1": h1, "meta_desc": meta_desc, "text": text}


async def _fetch_page_context(url: str) -> dict | None:
    ok, _reason = is_safe_public_url(url)
    if not ok:
        return None
    try:
        async with httpx.AsyncClient(
            timeout=PAGE_FETCH_TIMEOUT,
            follow_redirects=True,
            headers={"User-Agent": "VitalRankBot/1.0 (+seo-audit)"},
        ) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            if "html" not in resp.headers.get("content-type", "").lower():
                return None
            html_text = resp.text[:MAX_HTML_BYTES]
    except httpx.HTTPError:
        return None

    ctx = _extract_context(html_text)
    return ctx if any(ctx.values()) else None


def _build_prompt(
    issue_title: str,
    description: str | None,
    page_url: str | None,
    code_snippet: str | None,
    page_context: dict | None,
) -> str:
    lines = [
        "Ты — SEO-эксперт и веб-разработчик. Дай КОНКРЕТНОЕ, готовое к применению решение "
        "найденной проблемы ИМЕННО для этой страницы. Используй реальный контент страницы "
        "(тематику, услуги, товары, город) — НЕ пиши плейсхолдеры вроде «Краткое описание». "
        "Сначала дай готовый фрагмент (код или текст) для вставки как есть, затем 1–3 коротких "
        "шага как его применить. Отвечай по-русски, без воды.",
    ]

    if page_context:
        lines.append("\n=== ДАННЫЕ РЕАЛЬНОЙ СТРАНИЦЫ ===")
        if page_url:
            lines.append(f"URL: {page_url}")
        if page_context.get("title"):
            lines.append(f"Title: {page_context['title']}")
        if page_context.get("meta_desc"):
            lines.append(f"Текущее описание: {page_context['meta_desc']}")
        if page_context.get("h1"):
            lines.append(f"H1: {page_context['h1']}")
        if page_context.get("text"):
            lines.append(f"Текст страницы: {page_context['text']}")
    elif page_url:
        lines.append(f"\nСтраница: {page_url}")

    lines.append("\n=== ПРОБЛЕМА ===")
    lines.append(issue_title)
    if description:
        lines.append(description)
    if code_snippet:
        lines.append(f"Образец/шаблон: {code_snippet}")

    lines.append("\n=== ГОТОВОЕ РЕШЕНИЕ ===")
    return "\n".join(lines)


async def generate_fix(
    title: str,
    description: str | None = None,
    page_url: str | None = None,
    code_snippet: str | None = None,
) -> tuple[str, bool]:
    page_context = await _fetch_page_context(page_url) if page_url else None

    payload = {
        "model": LLM_MODEL,
        "prompt": _build_prompt(title, description, page_url, code_snippet, page_context),
        "stream": False,
        "options": {"temperature": 0.3},
    }
    try:
        async with httpx.AsyncClient(timeout=LLM_TIMEOUT) as client:
            resp = await client.post(f"{LLM_BASE_URL}/api/generate", json=payload)
            resp.raise_for_status()
            data = resp.json()
    except httpx.HTTPStatusError as exc:
        raise LLMUnavailable(f"модель вернула статус {exc.response.status_code}") from exc
    except httpx.HTTPError as exc:
        raise LLMUnavailable(str(exc) or "нет соединения с Ollama") from exc

    text = (data.get("response") or "").strip()
    if not text:
        raise LLMUnavailable("пустой ответ модели")
    return text, page_context is not None
