import os
from typing import Literal

import aiohttp

from worker.common.types import Issue, Severity

API_URL = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"
TIMEOUT = aiohttp.ClientTimeout(total=30)

THRESHOLDS = {
    "lcp": 2500,
    "cls": 0.1,
    "fid": 100,
}


async def _fetch_strategy(
    session: aiohttp.ClientSession, url: str, strategy: Literal["mobile", "desktop"]
) -> dict:
    params = {"url": url, "strategy": strategy, "category": "performance"}
    api_key = os.getenv("PAGESPEED_API_KEY")
    if api_key:
        params["key"] = api_key

    async with session.get(API_URL, params=params) as resp:
        if resp.status != 200:
            raise RuntimeError(f"PageSpeed API вернул статус {resp.status} для strategy={strategy}")
        return await resp.json()


def _extract_metrics(raw: dict) -> dict:
    lighthouse = raw.get("lighthouseResult", {})
    audits = lighthouse.get("audits", {})
    categories = lighthouse.get("categories", {})

    performance_score = categories.get("performance", {}).get("score")
    performance_score = round(performance_score * 100) if performance_score is not None else None

    return {
        "performance_score": performance_score,
        "lcp_ms": audits.get("largest-contentful-paint", {}).get("numericValue"),
        "cls": audits.get("cumulative-layout-shift", {}).get("numericValue"),
        "fid_ms": audits.get("max-potential-fid", {}).get("numericValue"),
    }


def _build_issues(strategy: str, metrics: dict) -> list[Issue]:
    issues = []
    lcp, cls, fid = metrics.get("lcp_ms"), metrics.get("cls"), metrics.get("fid_ms")

    if lcp is not None and lcp > THRESHOLDS["lcp"]:
        issues.append(Issue(
            code=f"lcp_slow_{strategy}",
            title=f"Медленный LCP ({strategy})",
            description=f"LCP составляет {lcp/1000:.1f} с при рекомендованных Google ≤2.5 с. "
                         f"Влияет на восприятие скорости загрузки и является официальным фактором ранжирования.",
            severity=Severity.CRITICAL if lcp > THRESHOLDS["lcp"] * 1.5 else Severity.WARNING,
            source_module="pagespeed",
            meta={"strategy": strategy, "value_ms": lcp},
        ))

    if cls is not None and cls > THRESHOLDS["cls"]:
        issues.append(Issue(
            code=f"cls_high_{strategy}",
            title=f"Высокий CLS ({strategy})",
            description=f"CLS равен {cls:.2f} при рекомендованном ≤0.1. Элементы страницы "
                         f"смещаются во время загрузки, что раздражает пользователей и штрафуется поисковиками.",
            severity=Severity.WARNING,
            source_module="pagespeed",
            fix_snippet="Задайте width/height для изображений и резервируйте место под баннеры/рекламу заранее.",
            meta={"strategy": strategy, "value": cls},
        ))

    if fid is not None and fid > THRESHOLDS["fid"]:
        issues.append(Issue(
            code=f"fid_slow_{strategy}",
            title=f"Медленный отклик на действия ({strategy})",
            description=f"Задержка отклика на первое действие пользователя — {fid:.0f} мс при рекомендованных ≤100 мс.",
            severity=Severity.WARNING,
            source_module="pagespeed",
            meta={"strategy": strategy, "value_ms": fid},
        ))

    return issues


async def run_pagespeed_audit(url: str) -> dict:
    issues: list[Issue] = []
    raw_metrics = {}

    async with aiohttp.ClientSession(timeout=TIMEOUT) as session:
        for strategy in ("mobile", "desktop"):
            try:
                raw = await _fetch_strategy(session, url, strategy)
            except (aiohttp.ClientError, RuntimeError) as exc:
                raw_metrics[strategy] = {"error": str(exc)}
                continue

            metrics = _extract_metrics(raw)
            raw_metrics[strategy] = metrics
            issues += _build_issues(strategy, metrics)

    ok = any("error" not in v for v in raw_metrics.values())
    return {"ok": ok, "metrics": raw_metrics, "issues": issues}
