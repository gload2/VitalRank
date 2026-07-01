from worker.common.types import Engine, Issue, WeightedIssue

GOOGLE_WEIGHTS: dict[str, tuple[float, float]] = {
    "missing_title":            (10, 1),
    "title_length":             (4, 1),
    "missing_meta_description": (5, 1),
    "meta_description_length":  (2, 1),
    "missing_h1":               (8, 1),
    "multiple_h1":              (3, 2),
    "missing_alt_attributes":   (3, 2),
    "missing_canonical":        (6, 2),
    "broken_internal_links":    (7, 3),
    "excessive_redirects":      (3, 3),
    "no_https":                 (9, 4),
    "missing_robots_txt":       (4, 1),
    "missing_sitemap_xml":      (5, 1),
    "lcp_slow_mobile":          (8, 4),
    "lcp_slow_desktop":         (6, 4),
    "cls_high_mobile":          (5, 3),
    "cls_high_desktop":         (4, 3),
    "fid_slow_mobile":          (5, 3),
    "fid_slow_desktop":         (4, 3),
}

DEFAULT_WEIGHT = (3, 2)


def analyze_for_google(issues: list[Issue]) -> list[WeightedIssue]:
    weighted = []
    for issue in issues:
        weight, effort = GOOGLE_WEIGHTS.get(issue.code, DEFAULT_WEIGHT)
        weighted.append(WeightedIssue(issue=issue, engine=Engine.GOOGLE, weight=weight, effort=effort))
    return sorted(weighted, key=lambda w: w.impact_effort_ratio, reverse=True)
