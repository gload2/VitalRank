import asyncio
from urllib.parse import urljoin, urlparse

import aiohttp
from bs4 import BeautifulSoup

from worker.common.types import Issue, Severity

TIMEOUT = aiohttp.ClientTimeout(total=10)
USER_AGENT = "VitalRankBot/1.0 (+https://vitalrank.example/bot)"
MAX_LINKS_TO_CHECK = 50
CONCURRENCY = 8


def _extract_internal_links(base_url: str, html: str) -> list[str]:
    soup = BeautifulSoup(html, "lxml")
    domain = urlparse(base_url).netloc
    links = set()

    for a in soup.find_all("a", href=True):
        href = a["href"].strip()
        if href.startswith(("mailto:", "tel:", "javascript:", "#")):
            continue
        absolute = urljoin(base_url, href)
        if urlparse(absolute).netloc == domain:
            links.add(absolute.split("#")[0])

    links.discard(base_url)
    return list(links)[:MAX_LINKS_TO_CHECK]


async def _check_one(session: aiohttp.ClientSession, sem: asyncio.Semaphore, url: str) -> dict:
    async with sem:
        try:
            async with session.head(
                url, headers={"User-Agent": USER_AGENT}, allow_redirects=True, timeout=TIMEOUT
            ) as resp:
                return {"url": url, "status": resp.status, "redirected": str(resp.url) != url}
        except (aiohttp.ClientError, asyncio.TimeoutError):
            try:
                async with session.get(
                    url, headers={"User-Agent": USER_AGENT}, allow_redirects=True, timeout=TIMEOUT
                ) as resp:
                    return {"url": url, "status": resp.status, "redirected": str(resp.url) != url}
            except (aiohttp.ClientError, asyncio.TimeoutError) as exc:
                return {"url": url, "status": None, "error": str(exc)}


async def run_link_check(url: str) -> dict:
    async with aiohttp.ClientSession(timeout=TIMEOUT) as session:
        try:
            async with session.get(url, headers={"User-Agent": USER_AGENT}) as resp:
                html = await resp.text(errors="ignore")
        except (aiohttp.ClientError, asyncio.TimeoutError) as exc:
            return {"ok": False, "error": str(exc), "issues": []}

        internal_links = _extract_internal_links(url, html)
        if not internal_links:
            return {"ok": True, "checked": 0, "broken": [], "redirects": [], "issues": []}

        sem = asyncio.Semaphore(CONCURRENCY)
        results = await asyncio.gather(*(_check_one(session, sem, link) for link in internal_links))

    broken = [r for r in results if r.get("status") is None or r.get("status", 200) >= 400]
    redirects = [r for r in results if r.get("redirected") and r.get("status", 0) < 400]

    issues: list[Issue] = []
    if broken:
        issues.append(Issue(
            code="broken_internal_links",
            title="Битые внутренние ссылки",
            description=f"Найдено {len(broken)} нерабочих внутренних ссылок из {len(internal_links)} проверенных. "
                         f"Битые ссылки портят опыт пользователя и расходуют краулинговый бюджет поисковика.",
            severity=Severity.CRITICAL if len(broken) > 3 else Severity.WARNING,
            source_module="link_checker",
            meta={"broken_urls": [b["url"] for b in broken][:10]},
        ))
    if len(redirects) > 5:
        issues.append(Issue(
            code="excessive_redirects",
            title="Много внутренних редиректов",
            description=f"{len(redirects)} внутренних ссылок ведут через редирект вместо прямого URL. "
                         f"Рекомендуется обновить ссылки на конечные адреса.",
            severity=Severity.INFO,
            source_module="link_checker",
        ))

    return {
        "ok": True,
        "checked": len(internal_links),
        "broken": broken,
        "redirects": redirects,
        "issues": issues,
    }
