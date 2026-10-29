from datetime import datetime, timedelta, timezone

from sqlmodel import Session

from agrotechEFA2026.db.models import SensorData
from agrotechEFA2026.services import export, riego, telegram

AHORA = datetime(2026, 10, 30, 12, 0, tzinfo=timezone.utc)
AGRICULTOR, INVERNADERO, SUELO = 1, 1, 3


def _suelo(motor, valor, horas=(0.5, 1, 2)):
    with Session(motor) as s:
        s.add_all(SensorData(sensor_id=SUELO, timestamp=AHORA - timedelta(hours=h), value=valor) for h in horas)
        s.commit()


def test_recomendar_con_la_base_de_datos(motor, monkeypatch):
    monkeypatch.setattr(riego, "obtener_prevision", lambda: {"lluvia_mm": 0.0, "tmax": 25.0, "en_vivo": True})
    _suelo(motor, 30.0)
    r = riego.recomendar(AGRICULTOR, INVERNADERO, AHORA)
    assert r["regar"] and r["minutos"] > 0
    monkeypatch.setattr(riego, "obtener_prevision", lambda: {"lluvia_mm": 9.0, "tmax": 25.0, "en_vivo": True})
    assert not riego.recomendar(AGRICULTOR, INVERNADERO, AHORA)["regar"]


def test_csv_y_pdf(motor):
    _suelo(motor, 30.0)
    desde = AHORA - timedelta(days=1)
    filas = export.historico_csv(AGRICULTOR, INVERNADERO, desde, AHORA).strip().splitlines()
    assert filas[0] == "sensor_id,type,unit,timestamp,value" and len(filas) == 4
    assert export.informe_pdf(AGRICULTOR, INVERNADERO, desde, AHORA, "Regar 10 min").startswith(b"%PDF")


def test_telegram_sin_configurar_no_envia(monkeypatch):
    monkeypatch.setattr(telegram, "_config", lambda: (None, None))
    assert telegram.avisar("hola") is False


def test_telegram_maximo_un_aviso_cada_30_min(monkeypatch):
    enviados = []
    monkeypatch.setattr(telegram, "_config", lambda: ("t", "c"))
    monkeypatch.setattr(telegram.requests, "post", lambda *a, **k: enviados.append(k) or type("R", (), {"raise_for_status": lambda s: None})())
    telegram._ultimo.clear()
    assert telegram.avisar("x", ahora=0) and not telegram.avisar("x", ahora=600) and telegram.avisar("x", ahora=1900)
    assert len(enviados) == 2
