from worker.common.types import Engine, Issue, WeightedIssue

YANDEX_WEIGHTS: dict[str, tuple[float, float]] = {
    "no_https":                 (10, 4),
    "broken_internal_links":    (9, 3),
    "excessive_redirects":      (4, 3),
    "lcp_slow_mobile":          (9, 4),
    "cls_high_mobile":          (7, 3),
    "fid_slow_mobile":          (6, 3),
    "lcp_slow_desktop":         (4, 4),
    "cls_high_desktop":         (3, 3),
    "fid_slow_desktop":         (3, 3),
    "missing_title":            (6, 1),
    "title_length":             (2, 1),
    "missing_meta_description": (3, 1),
    "meta_description_length":  (1, 1),
    "missing_h1":               (5, 1),
    "multiple_h1":              (2, 2),
    "missing_alt_attributes":   (2, 2),
    "missing_canonical":        (3, 2),
    "missing_robots_txt":       (5, 1),
    "missing_sitemap_xml":      (4, 1),
}

DEFAULT_WEIGHT = (3, 2)


def analyze_for_yandex(issues: list[Issue]) -> list[WeightedIssue]:
    weighted = []
    for issue in issues:
        weight, effort = YANDEX_WEIGHTS.get(issue.code, DEFAULT_WEIGHT)
        weighted.append(WeightedIssue(issue=issue, engine=Engine.YANDEX, weight=weight, effort=effort))
    return sorted(weighted, key=lambda w: w.impact_effort_ratio, reverse=True)
