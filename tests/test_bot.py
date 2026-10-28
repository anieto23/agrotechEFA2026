from datetime import datetime, timedelta, timezone

from sqlmodel import Session

from agrotechEFA2026.db.lecturas import guardar_lectura
from agrotechEFA2026.db.models import SensorData
from agrotechEFA2026.services import bot, riego

AGRICULTOR, SUELO = 1, 3


def _sin_red(monkeypatch):
    monkeypatch.setattr(riego, "obtener_prevision", lambda: {"lluvia_mm": 0.0, "tmax": 25.0, "en_vivo": True})


def test_pregunta_libre_da_resumen_de_todas_las_parcelas(claves, motor, monkeypatch):
    _sin_red(monkeypatch)
    r = bot.responder("¿cómo va mi parcela?", AGRICULTOR)
    assert "Invernadero tomates" in r and "Aguacates" in r and "Mangos" in r and "💧" in r


def test_estado_de_una_parcela_y_parcela_inexistente(claves, motor, monkeypatch):
    _sin_red(monkeypatch)
    r = bot.responder("/estado 2", AGRICULTOR)
    assert "Aguacates" in r and "Mangos" not in r
    assert "No encuentro" in bot.responder("/estado 99", AGRICULTOR)


def test_alertas_y_aviso_automatico_una_sola_vez(claves, motor):
    assert "Sin alertas" in bot.responder("/alertas", AGRICULTOR)
    guardar_lectura(SUELO, claves[str(SUELO)], 20.0)  # bajo el umbral 40 % del invernadero
    assert "humedad del suelo" in bot.responder("/alertas", AGRICULTOR).lower()
    enviadas = set()
    (id_alerta, texto), = bot.alertas_nuevas(AGRICULTOR, enviadas)
    assert texto.startswith("⚠️ Invernadero tomates:")
    enviadas.add(id_alerta)
    assert bot.alertas_nuevas(AGRICULTOR, enviadas) == []
