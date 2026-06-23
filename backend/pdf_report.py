from io import BytesIO

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

FONT = "Helvetica"
FONT_BOLD = "Helvetica-Bold"
try:
    pdfmetrics.registerFont(TTFont("DejaVu", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"))
    pdfmetrics.registerFont(TTFont("DejaVu-Bold", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"))
    FONT, FONT_BOLD = "DejaVu", "DejaVu-Bold"
except Exception:
    pass


def build_pdf(audit) -> bytes:
    """Собирает PDF-отчёт по аудиту."""
    buf = BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    width, height = A4
    left = 2 * cm
    y = height - 2 * cm

    def line(text, size=11, bold=False, gap=0.6):
        nonlocal y
        if y < 2 * cm:
            c.showPage()
            y = height - 2 * cm
        c.setFont(FONT_BOLD if bold else FONT, size)
        c.drawString(left, y, text)
        y -= gap * cm

    line("VitalRank. Отчёт SEO-аудита", size=18, bold=True, gap=1.0)
    line(f"Сайт: {audit.site.url}", size=12)
    line(f"Дата: {audit.created_at:%d.%m.%Y %H:%M}", size=10, gap=0.9)

    line(
        f"Google: {audit.google_score}    Яндекс: {audit.yandex_score}    "
        f"Health: {audit.health_score}",
        size=14, bold=True, gap=1.0,
    )

    line(f"Найдено проблем: {len(audit.issues)}", size=12, bold=True, gap=0.8)

    for issue in audit.issues:
        prios = {s.engine: s for s in issue.scores}
        g = prios.get("google")
        yx = prios.get("yandex")
        tag = []
        if g:
            tag.append(f"G {g.priority_score}{'!' if g.is_critical else ''}")
        if yx:
            tag.append(f"Y {yx.priority_score}{'!' if yx.is_critical else ''}")
        line(f"• {issue.title}   [{'  '.join(tag)}]", size=11, bold=True, gap=0.5)
        if issue.detail:
            line(f"   {issue.detail}", size=9, gap=0.45)
        line(f"   {issue.description}", size=9, gap=0.7)

    c.save()
    return buf.getvalue()
