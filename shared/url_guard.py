import ipaddress
import socket
import time
from urllib.parse import urlparse


def _resolve(host: str, attempts: int = 2):
    last = None
    for i in range(attempts):
        try:
            return socket.getaddrinfo(host, None)
        except socket.gaierror as exc:
            last = exc
            if i + 1 < attempts:
                time.sleep(0.3)
    raise last


def is_safe_public_url(url: str) -> tuple[bool, str]:
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
        infos = _resolve(host)
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
