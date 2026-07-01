from worker.analyzers.google_analyzer import analyze_for_google
from worker.analyzers.yandex_analyzer import analyze_for_yandex
from worker.common.types import Engine, Issue, WeightedIssue

MAX_POSSIBLE_WEIGHT_PER_ENGINE = 100
QUICK_WIN_EFFORT_THRESHOLD = 2


def _health_score(weighted_issues: list[WeightedIssue]) -> int:
    total_penalty = sum(w.weight for w in weighted_issues)
    score = 100 - round(100 * total_penalty / MAX_POSSIBLE_WEIGHT_PER_ENGINE)
    return max(0, min(100, score))


def _split_by_effort(weighted_issues: list[WeightedIssue]) -> dict:
    quick_wins = [w for w in weighted_issues if w.effort <= QUICK_WIN_EFFORT_THRESHOLD]
    long_fixes = [w for w in weighted_issues if w.effort > QUICK_WIN_EFFORT_THRESHOLD]
    return {"quick_wins": quick_wins, "long_fixes": long_fixes}


def _serialize(weighted: WeightedIssue) -> dict:
    issue = weighted.issue
    return {
        "code": issue.code,
        "title": issue.title,
        "description": issue.description,
        "severity": issue.severity.value,
        "source_module": issue.source_module,
        "fix_snippet": issue.fix_snippet,
        "weight": weighted.weight,
        "effort": weighted.effort,
        "priority_score": round(weighted.impact_effort_ratio, 2),
        "meta": issue.meta,
    }


def generate_report(tech_result: dict, pagespeed_result: dict, link_result: dict) -> dict:
    all_issues: list[Issue] = (
        tech_result.get("issues", [])
        + pagespeed_result.get("issues", [])
        + link_result.get("issues", [])
    )

    google_weighted = analyze_for_google(all_issues)
    yandex_weighted = analyze_for_yandex(all_issues)

    google_split = _split_by_effort(google_weighted)
    yandex_split = _split_by_effort(yandex_weighted)

    return {
        "engines": {
            Engine.GOOGLE.value: {
                "health_score": _health_score(google_weighted),
                "quick_wins": [_serialize(w) for w in google_split["quick_wins"]],
                "long_fixes": [_serialize(w) for w in google_split["long_fixes"]],
            },
            Engine.YANDEX.value: {
                "health_score": _health_score(yandex_weighted),
                "quick_wins": [_serialize(w) for w in yandex_split["quick_wins"]],
                "long_fixes": [_serialize(w) for w in yandex_split["long_fixes"]],
            },
        },
        "raw": {
            "pagespeed_metrics": pagespeed_result.get("metrics"),
            "links_checked": link_result.get("checked"),
            "broken_links_count": len(link_result.get("broken", [])),
        },
        "errors": [
            e for e in (
                tech_result.get("error"),
                pagespeed_result.get("error") if not pagespeed_result.get("ok") else None,
                link_result.get("error"),
            ) if e
        ],
    }
