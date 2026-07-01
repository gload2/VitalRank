import asyncio
from urllib.parse import urljoin, urlparse

import aiohttp
from bs4 import BeautifulSoup

from worker.common.types import Issue, Severity

TIMEOUT = aiohttp.ClientTimeout(total=15)
USER_AGENT = "VitalRankBot/1.0 (+https://vitalrank.example/bot)"


async def _fetch(session: aiohttp.ClientSession, url: str) -> tuple[int, str]:
    async with session.get(url, headers={"User-Agent": USER_AGENT}, allow_redirects=True) as resp:
        text = await resp.text(errors="ignore")
        return resp.status, text


async def _check_aux_file(session: aiohttp.ClientSession, base_url: str, path: str) -> bool:
    target = urljoin(base_url, path)
    try:
        async with session.get(target, headers={"User-Agent": USER_AGENT}) as resp:
            return resp.status == 200
    except (aiohttp.ClientError, asyncio.TimeoutError):
        return False


def _check_title(soup: BeautifulSoup) -> list[Issue]:
    issues = []
    tag = soup.find("title")
    if not tag or not tag.text.strip():
        issues.append(Issue(
            code="missing_title",
            title="Отсутствует тег <title>",
            description="На странице не найден или пуст тег <title>. Это один из главных сигналов для обеих поисковых систем.",
            severity=Severity.CRITICAL,
            source_module="tech_audit",
            fix_snippet='<title>Краткое и точное название страницы (50-60 символов)</title>',
        ))
    else:
        length = len(tag.text.strip())
        if length < 10 or length > 60:
            issues.append(Issue(
                code="title_length",
                title="Неоптимальная длина title",
                description=f"Длина title — {length} символов. Рекомендуемый диапазон 10-60 символов, иначе title обрезается в выдаче.",
                severity=Severity.WARNING,
                source_module="tech_audit",
                meta={"current_length": length},
            ))
    return issues


def _check_meta_description(soup: BeautifulSoup) -> list[Issue]:
    issues = []
    tag = soup.find("meta", attrs={"name": "description"})
    content = tag.get("content", "").strip() if tag else ""
    if not content:
        issues.append(Issue(
            code="missing_meta_description",
            title="Отсутствует meta description",
            description="Нет описания страницы. Без него поисковик сам генерирует сниппет, что снижает CTR в выдаче.",
            severity=Severity.WARNING,
            source_module="tech_audit",
            fix_snippet='<meta name="description" content="Краткое описание страницы, 120-160 символов">',
        ))
    elif not (120 <= len(content) <= 160):
        issues.append(Issue(
            code="meta_description_length",
            title="Неоптимальная длина meta description",
            description=f"Длина description — {len(content)} символов. Рекомендуется 120-160 символов.",
            severity=Severity.INFO,
            source_module="tech_audit",
            meta={"current_length": len(content)},
        ))
    return issues


def _check_headings(soup: BeautifulSoup) -> list[Issue]:
    issues = []
    h1_tags = soup.find_all("h1")
    if len(h1_tags) == 0:
        issues.append(Issue(
            code="missing_h1",
            title="Отсутствует H1",
            description="На странице нет заголовка первого уровня. H1 помогает поисковику и пользователю понять тему страницы.",
            severity=Severity.CRITICAL,
            source_module="tech_audit",
            fix_snippet="<h1>Главный заголовок страницы</h1>",
        ))
    elif len(h1_tags) > 1:
        issues.append(Issue(
            code="multiple_h1",
            title="Несколько тегов H1",
            description=f"Найдено {len(h1_tags)} тегов H1. Рекомендуется использовать только один H1 на странице.",
            severity=Severity.WARNING,
            source_module="tech_audit",
            meta={"count": len(h1_tags)},
        ))
    return issues


def _check_canonical(soup: BeautifulSoup) -> list[Issue]:
    issues = []
    tag = soup.find("link", attrs={"rel": "canonical"})
    if not tag or not tag.get("href"):
        issues.append(Issue(
            code="missing_canonical",
            title="Отсутствует canonical-тег",
            description="Без canonical поисковик может посчитать одинаковые по содержанию страницы дублями и хуже их ранжировать.",
            severity=Severity.WARNING,
            source_module="tech_audit",
            fix_snippet='<link rel="canonical" href="https://example.com/page/">',
        ))
    return issues


def _check_https(url: str) -> list[Issue]:
    issues = []
    if urlparse(url).scheme != "https":
        issues.append(Issue(
            code="no_https",
            title="Сайт работает без HTTPS",
            description="Отсутствие SSL-сертификата — прямой негативный сигнал для обеих поисковых систем и снижает доверие пользователей.",
            severity=Severity.CRITICAL,
            source_module="tech_audit",
        ))
    return issues


def _check_images_alt(soup: BeautifulSoup) -> list[Issue]:
    issues = []
    images = soup.find_all("img")
    missing = [img for img in images if not img.get("alt", "").strip()]
    if images and missing:
        issues.append(Issue(
            code="missing_alt_attributes",
            title="Изображения без alt-атрибута",
            description=f"{len(missing)} из {len(images)} изображений не имеют alt-текста. Это ухудшает доступность и индексацию картинок.",
            severity=Severity.INFO,
            source_module="tech_audit",
            fix_snippet='<img src="photo.jpg" alt="Описание того, что на фото">',
            meta={"missing_count": len(missing), "total_count": len(images)},
        ))
    return issues


async def run_tech_audit(url: str) -> dict:
    issues: list[Issue] = []
    async with aiohttp.ClientSession(timeout=TIMEOUT) as session:
        try:
            status, html = await _fetch(session, url)
        except (aiohttp.ClientError, asyncio.TimeoutError) as exc:
            return {"ok": False, "error": f"Не удалось получить страницу: {exc}", "issues": []}

        if status >= 400:
            return {"ok": False, "error": f"Страница вернула статус {status}", "issues": []}

        soup = BeautifulSoup(html, "lxml")

        issues += _check_title(soup)
        issues += _check_meta_description(soup)
        issues += _check_headings(soup)
        issues += _check_canonical(soup)
        issues += _check_https(url)
        issues += _check_images_alt(soup)

        has_robots, has_sitemap = await asyncio.gather(
            _check_aux_file(session, url, "/robots.txt"),
            _check_aux_file(session, url, "/sitemap.xml"),
        )
        if not has_robots:
            issues.append(Issue(
                code="missing_robots_txt",
                title="Отсутствует robots.txt",
                description="Файл robots.txt не найден по стандартному пути. Поисковые роботы используют его как первую точку входа на сайт.",
                severity=Severity.WARNING,
                source_module="tech_audit",
            ))
        if not has_sitemap:
            issues.append(Issue(
                code="missing_sitemap_xml",
                title="Отсутствует sitemap.xml",
                description="Карта сайта не найдена по стандартному пути /sitemap.xml. Без неё индексация крупных сайтов идёт медленнее.",
                severity=Severity.WARNING,
                source_module="tech_audit",
            ))

    return {"ok": True, "issues": issues}
