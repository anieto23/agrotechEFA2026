"""Prueba mínima de aviso por Telegram.

Uso:
    python scripts/telegram_prueba.py --chat-id    # muestra tu chat id (escribe antes algo al bot)
    python scripts/telegram_prueba.py              # envía un aviso de prueba

Lee TELEGRAM_TOKEN y TELEGRAM_CHAT_ID de .env (ignorado por git).
"""
import argparse
import os
import sys
from pathlib import Path

import requests

API = "https://api.telegram.org/bot{token}/{metodo}"


def cargar_env(ruta=Path(__file__).resolve().parent.parent / ".env"):
    if ruta.exists():
        for linea in ruta.read_text(encoding="utf-8").splitlines():
            if "=" in linea and not linea.lstrip().startswith("#"):
                k, v = linea.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


def llamar(token, metodo, **datos):
    r = requests.post(API.format(token=token, metodo=metodo), json=datos, timeout=10)
    r.raise_for_status()
    return r.json()["result"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--chat-id", action="store_true", help="listar chats que han escrito al bot")
    args = ap.parse_args()

    cargar_env()
    token = os.environ.get("TELEGRAM_TOKEN")
    if not token:
        sys.exit("Falta TELEGRAM_TOKEN en .env")

    if args.chat_id:
        for u in llamar(token, "getUpdates"):
            chat = (u.get("message") or {}).get("chat")
            if chat:
                print(chat["id"], chat.get("first_name", ""))
        return

    chat = os.environ.get("TELEGRAM_CHAT_ID")
    if not chat:
        sys.exit("Falta TELEGRAM_CHAT_ID en .env (usa --chat-id para verlo)")
    llamar(token, "sendMessage", chat_id=chat,
           text="⚠️ Prueba Agrotech: humedad del suelo en parcela 2 al 18 % (umbral 25 %)")
    print("Enviado")


if __name__ == "__main__":
    main()
