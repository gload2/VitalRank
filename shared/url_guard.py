import ipaddress
import socket
from urllib.parse import urlparse


def is_safe_public_url(url: str) -> tuple[bool, str]:
    """Проверяет, что URL публичный (защита от SSRF).

    Отклоняет нестандартные схемы и адреса, ведущие во внутреннюю сеть
    (localhost, приватные диапазоны, loopback, link-local, метадата облака).
    """
    try:
        parsed = urlparse(url)
    except ValueError:
        return False, "некорректный URL"

    if parsed.scheme not in ("http", "https"):
        return False, "разрешены только http и https"

    host = parsed.hostname
    if not host:
        return False, "не указан хост"

    if host.lower() in ("localhost", "localhost.localdomain"):
        return False, "локальный адрес запрещён"

    try:
        infos = socket.getaddrinfo(host, None)
    except socket.gaierror:
        return False, "не удалось разрешить домен"

    for info in infos:
        ip_str = info[4][0]
        try:
            addr = ipaddress.ip_address(ip_str)
        except ValueError:
            continue
        if (
            addr.is_private
            or addr.is_loopback
            or addr.is_link_local
            or addr.is_reserved
            or addr.is_multicast
            or addr.is_unspecified
        ):
            return False, "адрес ведёт во внутреннюю сеть"

    return True, ""
