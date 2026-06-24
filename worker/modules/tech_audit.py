import requests
from bs4 import BeautifulSoup

HEADERS = {"User-Agent": "VitalRankBot/0.1"}


def fetch_html(url):
    response = requests.get(url, headers=HEADERS, timeout=10)
    response.raise_for_status()
    return response.text


def check_title(soup):
    title = soup.find("title")
    if title is None or not title.get_text(strip=True):
        return {"name": "title", "ok": False, "message": "Тег title отсутствует или пуст"}
    return {"name": "title", "ok": True, "value": title.get_text(strip=True)}


def check_description(soup):
    tag = soup.find("meta", attrs={"name": "description"})
    if tag is None or not tag.get("content", "").strip():
        return {"name": "description", "ok": False, "message": "Meta description отсутствует"}
    return {"name": "description", "ok": True, "value": tag["content"].strip()}


def run(url):
    html = fetch_html(url)
    soup = BeautifulSoup(html, "html.parser")
    checks = [check_title(soup), check_description(soup)]
    passed = sum(1 for c in checks if c["ok"])
    return {
        "url": url,
        "score": round(passed / len(checks) * 100),
        "checks": checks,
    }
