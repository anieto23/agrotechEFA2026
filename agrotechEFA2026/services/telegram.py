"""Avisos por Telegram: `avisar("⚠️ Parcela 2: humedad del suelo 22 % (mínimo 35 %)")`.

TELEGRAM_TOKEN y TELEGRAM_CHAT_ID salen del entorno o de `.env` (ignorado por git).
Sin spam: como mucho 1 aviso por `clave` cada 30 min (por defecto, la clave es el propio mensaje).
"""
import os
import time
from pathlib import Path
from typing import Optional

import requests

ENFRIAMIENTO_S = 30 * 60
_ultimo: dict[str, float] = {}
_ENV = Path(__file__).resolve().parents[2] / ".env"


def _config() -> tuple[Optional[str], Optional[str]]:
    if _ENV.exists():
        for linea in _ENV.read_text(encoding="utf-8").splitlines():
            if "=" in linea and not linea.lstrip().startswith("#"):
                k, v = linea.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))
    return os.environ.get("TELEGRAM_TOKEN"), os.environ.get("TELEGRAM_CHAT_ID")


def avisar(mensaje: str, clave: Optional[str] = None, ahora: Optional[float] = None) -> bool:
    """Envía el aviso. Devuelve True si se envió; False si se omitió (spam o sin configurar) o falló."""
    token, chat = _config()
    if not (token and chat):
        return False
    clave = clave or mensaje
    ahora = time.time() if ahora is None else ahora
    if ahora - _ultimo.get(clave, -ENFRIAMIENTO_S) < ENFRIAMIENTO_S:
        return False
    try:
        r = requests.post(f"https://api.telegram.org/bot{token}/sendMessage",
                          json={"chat_id": chat, "text": mensaje}, timeout=10)
        r.raise_for_status()
    except requests.RequestException:
        return False  # un fallo de Telegram no debe tumbar la recepción de lecturas
    _ultimo[clave] = ahora
    return True
