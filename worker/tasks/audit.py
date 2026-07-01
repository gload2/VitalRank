import asyncio
import logging
from datetime import datetime

from worker.celery_app import celery_app
from worker.modules.tech_audit import run_tech_audit
from worker.modules.pagespeed import run_pagespeed_audit
from worker.modules.link_checker import run_link_check
from worker.reports.report_generater import generate_report

from shared.database import SessionLocal
from shared.models import Audit, AuditResult, Issue, IssueScore

log = logging.getLogger(__name__)

CRITICAL_EFFECT = 7
QUICK_WIN_EFFORT = 2

_CATEGORY_BY_CODE = {
    "missing_title": "meta",
    "title_length": "meta",
    "missing_meta_description": "meta",
    "meta_description_length": "meta",
    "missing_h1": "content",
    "multiple_h1": "content",
    "missing_alt_attributes": "content",
    "missing_canonical": "indexing",
    "missing_robots_txt": "indexing",
    "missing_sitemap_xml": "indexing",
    "no_https": "trust",
    "broken_internal_links": "links",
    "excessive_redirects": "links",
}


def _category(code: str, source_module: str) -> str:
    if code in _CATEGORY_BY_CODE:
        return _CATEGORY_BY_CODE[code]
    if code.startswith(("lcp_", "cls_", "fid_")):
        return "performance"
    return source_module or "other"


def _detail(meta: dict | None) -> str | None:
    if not meta:
        return None
    if "current_length" in meta:
        return f"Текущая длина: {meta['current_length']} символов"
    if "missing_count" in meta and "total_count" in meta:
        return f"{meta['missing_count']} из {meta['total_count']} изображений без alt"
    if "count" in meta:
        return f"Найдено элементов: {meta['count']}"
    if meta.get("broken_urls"):
        return "Примеры: " + ", ".join(meta["broken_urls"][:3])
    if "value_ms" in meta:
        return f"Значение: {round(meta['value_ms'])} мс"
    if "value" in meta:
        return f"Значение: {meta['value']}"
    return None


def _safe(result, module_name: str) -> dict:
    if isinstance(result, Exception):
        log.warning("Модуль %s упал с ошибкой: %s", module_name, result)
        return {"ok": False, "error": str(result), "issues": []}
    return result


async def _run_all_modules(url: str, full: bool = True) -> tuple[dict, dict]:
    if full:
        tech_result, pagespeed_result, link_result = await asyncio.gather(
            run_tech_audit(url),
            run_pagespeed_audit(url),
            run_link_check(url),
            return_exceptions=True,
        )
        tech_result = _safe(tech_result, "tech_audit")
        pagespeed_result = _safe(pagespeed_result, "pagespeed")
        link_result = _safe(link_result, "link_checker")
    else:
        tech_raw = await asyncio.gather(run_tech_audit(url), return_exceptions=True)
        tech_result = _safe(tech_raw[0], "tech_audit")
        pagespeed_result = {"ok": True, "metrics": {}, "issues": []}
        link_result = {"ok": True, "checked": 0, "broken": [], "issues": []}

    report = generate_report(tech_result, pagespeed_result, link_result)
    return report, tech_result


def _engine_issues(report: dict, engine: str) -> list[dict]:
    block = report["engines"][engine]
    return block["quick_wins"] + block["long_fixes"]


def _persist_issues(db, audit_id: int, report: dict, page_url: str) -> None:
    google_list = _engine_issues(report, "google")
    yandex_by_code = {i["code"]: i for i in _engine_issues(report, "yandex")}

    for g in google_list:
        code = g["code"]
        y = yandex_by_code.get(code, g)

        issue = Issue(
            audit_id=audit_id,
            rule_id=code,
            page_url=page_url,
            category=_category(code, g.get("source_module", "")),
            title=g["title"],
            description=g.get("description"),
            detail=_detail(g.get("meta")),
            code_snippet=g.get("fix_snippet"),
        )
        db.add(issue)
        db.flush()

        for engine, data in (("google", g), ("yandex", y)):
            effect = round(data["weight"])
            effort = round(data["effort"])
            priority = data.get("priority_score")
            if priority is None:
                priority = round(effect / effort, 2) if effort else float(effect)
            db.add(IssueScore(
                issue_id=issue.id,
                engine=engine,
                effect=effect,
                effort=effort,
                priority_score=round(priority, 2),
                bucket="quick_win" if effort <= QUICK_WIN_EFFORT else "long",
                is_critical=effect >= CRITICAL_EFFECT,
            ))


def _previous_health(db, audit: Audit) -> int | None:
    prev = (
        db.query(Audit)
        .filter(
            Audit.site_id == audit.site_id,
            Audit.id != audit.id,
            Audit.status == "done",
        )
        .order_by(Audit.created_at.desc())
        .first()
    )
    return prev.health_score if prev else None


@celery_app.task(name="audit.run")
def run_audit(audit_id: int) -> dict:
    db = SessionLocal()
    try:
        audit = db.get(Audit, audit_id)
        if audit is None:
            return {"audit_id": audit_id, "status": "missing"}

        audit.status = "processing"
        db.commit()

        url = audit.site.url
        plan = getattr(audit.site.owner, "plan", "free") if audit.site else "free"
        full = plan != "free"

        report, tech_result = asyncio.run(_run_all_modules(url, full=full))

        if not tech_result.get("ok"):
            raise RuntimeError(tech_result.get("error") or "Не удалось получить страницу сайта")

        db.add(AuditResult(audit_id=audit.id, module="full_audit", data=report))
        _persist_issues(db, audit.id, report, url)

        google = report["engines"]["google"]["health_score"]
        yandex = report["engines"]["yandex"]["health_score"]
        health = round((google + yandex) / 2)
        prev_health = _previous_health(db, audit)

        audit.google_score = google
        audit.yandex_score = yandex
        audit.health_score = health
        audit.score_delta = (health - prev_health) if prev_health is not None else None
        audit.status = "done"
        audit.finished_at = datetime.utcnow()
        db.commit()

        return {"audit_id": audit_id, "status": "done", "health": health}

    except Exception as exc:  # noqa: BLE001
        db.rollback()
        message = str(exc)[:500]
        audit = db.get(Audit, audit_id)
        if audit is not None:
            audit.status = "failed"
            audit.error = message
            audit.finished_at = datetime.utcnow()
            db.commit()
        log.warning("Аудит %s провалился: %s", audit_id, message)
        return {"audit_id": audit_id, "status": "failed", "error": message}
    finally:
        db.close()
