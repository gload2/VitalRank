from fastapi import APIRouter

from backend.schemas import AuditReport

router = APIRouter(prefix="/demo", tags=["service"])


def _score(engine, effect, effort, critical=False):
    return {
        "engine": engine,
        "effect": effect,
        "effort": effort,
        "priority_score": round(effect / effort, 2),
        "bucket": "quick_win" if effort == 1 else "long",
        "is_critical": critical,
    }


SAMPLE = {
    "id": 0,
    "site_id": 0,
    "status": "done",
    "google_score": 61,
    "yandex_score": 66,
    "health_score": 64,
    "score_delta": -3,
    "error": None,
    "created_at": "2026-06-23T17:42:00",
    "finished_at": "2026-06-23T17:43:24",
    "issues": [
        {
            "id": 1, "rule_id": "title_too_long", "page_url": "https://example.ru/",
            "category": "meta", "title": "Title слишком длинный",
            "description": "Длинный заголовок обрезается в выдаче. Рекомендуется до 60 символов.",
            "detail": "Title 83 символа, надо до 60", "code_snippet": None,
            "scores": [_score("google", 4, 1), _score("yandex", 3, 1)],
        },
        {
            "id": 2, "rule_id": "h1_missing", "page_url": "https://example.ru/",
            "category": "content", "title": "Нет заголовка H1",
            "description": "H1 задаёт главную тему страницы для пользователя и поиска.",
            "detail": None, "code_snippet": "<h1>Главный заголовок страницы</h1>",
            "scores": [_score("google", 7, 1), _score("yandex", 5, 1)],
        },
        {
            "id": 3, "rule_id": "no_contacts", "page_url": "https://example.ru/",
            "category": "trust", "title": "Нет контактов на странице",
            "description": "Телефон и почта это коммерческие сигналы доверия, особенно для Яндекса.",
            "detail": None, "code_snippet": None,
            "scores": [_score("google", 2, 2), _score("yandex", 9, 2, critical=True)],
        },
        {
            "id": 4, "rule_id": "lcp_slow", "page_url": "https://example.ru/",
            "category": "speed", "title": "Медленная загрузка (LCP)",
            "description": "LCP больше 2.5с ухудшает Core Web Vitals и ранжирование.",
            "detail": "LCP 4.2с, надо меньше 2.5с", "code_snippet": None,
            "scores": [_score("google", 8, 3, critical=True), _score("yandex", 5, 3)],
        },
        {
            "id": 5, "rule_id": "no_canonical", "page_url": "https://example.ru/",
            "category": "indexing", "title": "Нет canonical",
            "description": "Canonical защищает от дублей и склейки веса страниц.",
            "detail": None, "code_snippet": '<link rel="canonical" href="https://example.ru/page" />',
            "scores": [_score("google", 8, 2, critical=True), _score("yandex", 4, 2)],
        },
        {
            "id": 6, "rule_id": "no_schema", "page_url": "https://example.ru/",
            "category": "trust", "title": "Нет микроразметки Schema.org",
            "description": "Структурированные данные дают расширенные сниппеты. Для Яндекса важны.",
            "detail": None, "code_snippet": None,
            "scores": [_score("google", 4, 2), _score("yandex", 6, 2)],
        },
    ],
}


@router.get("/report", response_model=AuditReport, summary="Пример готового отчёта")
def demo_report():
    """Показательный отчёт для лендинга. Без авторизации и без ожидания аудита."""
    return SAMPLE
