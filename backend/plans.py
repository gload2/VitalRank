DEFAULT_PLAN = "free"

PLANS = {
    "free": {
        "id": "free",
        "label": "Free",
        "price": "0 ₽",
        "tagline": "Для первого знакомства",
        "max_sites": 1,
        "features": {
            "full_audit": False,
            "pdf": False,
            "compare": False,
            "ai_fix": False,
            "monitoring": False,
        },
    },
    "pro": {
        "id": "pro",
        "label": "Pro",
        "price": "990 ₽/мес",
        "tagline": "Для владельцев сайтов",
        "max_sites": 10,
        "features": {
            "full_audit": True,
            "pdf": True,
            "compare": True,
            "ai_fix": False,
            "monitoring": False,
        },
    },
    "business": {
        "id": "business",
        "label": "Business",
        "price": "2990 ₽/мес",
        "tagline": "Для агентств и команд",
        "max_sites": 1000,
        "features": {
            "full_audit": True,
            "pdf": True,
            "compare": True,
            "ai_fix": True,
            "monitoring": True,
        },
    },
}

FEATURE_LABELS = {
    "full_audit": "Полный аудит (PageSpeed + ссылки)",
    "pdf": "Экспорт отчёта в PDF",
    "compare": "Сравнение с конкурентом",
    "ai_fix": "AI-починка проблем",
    "monitoring": "Мониторинг по расписанию",
}


def get_plan(name: str | None) -> dict:
    return PLANS.get(name or DEFAULT_PLAN, PLANS[DEFAULT_PLAN])


def plan_allows(name: str | None, feature: str) -> bool:
    return bool(get_plan(name)["features"].get(feature, False))


def max_sites(name: str | None) -> int:
    return get_plan(name)["max_sites"]
