"""Bot de Telegram de Agrotech: contesta «¿cómo va mi parcela?» y avisa solo si algo va mal.

    python -m agrotechEFA2026.services.bot

Solo habla con el chat de TELEGRAM_CHAT_ID (.env) y actúa como el usuario AGROTECH_BOT_USUARIO
(por defecto `agricultor`). Es de lectura: no da órdenes. Mensajes sueltos o /estado = resumen
de todas tus parcelas; /estado 2, /riego 2, /alertas, /parcelas y /ayuda.
"""
import os
import re
import sys
import time

import requests
from sqlmodel import select

from ..db import consultas
from ..db.models import Alert, Parcel, Sector, Sensor, User
from ..db.session import sesion
from . import riego, telegram

ICONOS = {"ok": "✅", "low": "🔻", "high": "🔺", "no_data": "❔", "no_range": "➖"}
NOMBRES = {"temperature": "Temperatura", "air_humidity": "Humedad del aire",
           "soil_moisture": "Humedad del suelo", "light": "Luz"}
AYUDA = ("Pregúntame «¿cómo va mi parcela?» o usa /estado, /estado 2, /riego 2, /alertas, /parcelas. "
         "Si algo va mal te aviso yo.")
REVISION_S = 60  # cada cuánto se buscan alertas nuevas


def _riego(usuario_id: int, parcela_id: int) -> str:
    try:
        return riego.recomendar(usuario_id, parcela_id)["motivo"]
    except (ValueError, PermissionError) as e:
        return str(e)


def estado_parcela(usuario_id: int, parcela) -> str:
    lineas = [f"🌱 {parcela.name} (parcela {parcela.id})"]
    for e in consultas.ultimas_lecturas(usuario_id, parcela.id):
        valor = "sin datos" if e.value is None else f"{e.value:g} {e.unit}"
        lineas.append(f"{ICONOS.get(e.status, '')} {NOMBRES.get(e.type, e.type)}: {valor}")
    lineas.append("💧 " + _riego(usuario_id, parcela.id))
    return "\n".join(lineas)


def responder(texto: str, usuario_id: int) -> str:
    """Respuesta al mensaje del usuario. Cualquier texto que no sea un comando da el resumen."""
    texto = texto.strip().lower()
    parcelas = consultas.listar_parcelas(usuario_id)
    if not parcelas:
        return "Todavía no tienes parcelas."
    numero = re.search(r"\d+", texto)
    if texto.startswith(("/ayuda", "/start")):
        return AYUDA
    if texto.startswith("/parcelas"):
        return "\n".join(f"{p.id}. {p.name}" for p in parcelas)
    if texto.startswith("/alertas"):
        alertas = consultas.alertas_pendientes(usuario_id)
        return "\n".join(f"⚠️ {a.message}" for a in alertas) or "✅ Sin alertas pendientes."
    elegidas = [p for p in parcelas if numero and p.id == int(numero.group())]
    if not elegidas:
        if numero and texto.startswith("/"):
            return f"No encuentro la parcela {numero.group()}. Usa /parcelas para ver las tuyas."
        elegidas = parcelas
    if texto.startswith("/riego"):
        return "\n".join(f"💧 {p.name}: {_riego(usuario_id, p.id)}" for p in elegidas)
    return "\n\n".join(estado_parcela(usuario_id, p) for p in elegidas)


def alertas_nuevas(usuario_id: int, enviadas: set) -> list[tuple[int, str]]:
    """(id, texto con el nombre de la parcela) de las alertas pendientes que aún no se han avisado."""
    nuevas = []
    for a in consultas.alertas_pendientes(usuario_id):
        if a.id in enviadas:
            continue
        with sesion() as s:
            nombre = s.exec(select(Parcel.name).join(Sector, Sector.parcel_id == Parcel.id)
                            .join(Sensor, Sensor.sector_id == Sector.id).where(Sensor.id == a.sensor_id)).first()
        nuevas.append((a.id, f"⚠️ {nombre}: {a.message}"))
    return nuevas


def _api(token: str, metodo: str, **datos):
    r = requests.post(f"https://api.telegram.org/bot{token}/{metodo}", json=datos, timeout=40)
    r.raise_for_status()
    return r.json()["result"]


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    token, chat = telegram._config()
    if not (token and chat):
        raise SystemExit("Faltan TELEGRAM_TOKEN / TELEGRAM_CHAT_ID en .env")
    with sesion() as s:
        usuario = s.exec(select(User).where(User.username == os.environ.get("AGROTECH_BOT_USUARIO", "agricultor"))).first()
    if usuario is None:
        raise SystemExit("No existe el usuario del bot (¿has ejecutado `python -m agrotechEFA2026.db.seed`?)")

    # Lo que ya estaba pendiente al arrancar no se vuelve a avisar
    enviadas = {a.id for a in consultas.alertas_pendientes(usuario.id)}
    offset, proxima_revision = None, 0.0
    print("Bot en marcha. Ctrl+C para parar.")
    while True:
        try:
            for u in _api(token, "getUpdates", offset=offset, timeout=20):
                offset = u["update_id"] + 1
                mensaje = u.get("message") or {}
                if str(mensaje.get("chat", {}).get("id")) == str(chat) and mensaje.get("text"):
                    _api(token, "sendMessage", chat_id=chat, text=responder(mensaje["text"], usuario.id))
            if time.time() >= proxima_revision:
                proxima_revision = time.time() + REVISION_S
                for id_alerta, texto in alertas_nuevas(usuario.id, enviadas):
                    if telegram.avisar(texto, clave=f"alerta-{id_alerta}"):
                        enviadas.add(id_alerta)
                        print("Aviso enviado:", texto)
        except requests.RequestException as e:
            print("[aviso] Telegram no responde:", e)
            time.sleep(5)


if __name__ == "__main__":
    main()
