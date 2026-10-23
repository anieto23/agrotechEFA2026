import random
from datetime import datetime, timedelta, timezone

from scripts import gen_sample_data as g

AHORA = datetime(2026, 10, 30, 12, 0, tzinfo=timezone.utc)
CLAVES = {"sensor_id", "timestamp", "type", "value", "unit"}


def test_formato_y_rangos_en_14_dias():
    lecturas = list(g.historico(14, 15, 42, AHORA))
    assert len(lecturas) > 14 * 96 * 12 * 0.99
    for l in lecturas:
        assert set(l) == CLAVES
        unidad, minimo, maximo = g.TIPOS[l["type"]]
        assert minimo <= l["value"] <= maximo
        assert l["unit"] == unidad


def test_misma_semilla_mismos_datos():
    assert list(g.historico(2, 60, 7, AHORA)) == list(g.historico(2, 60, 7, AHORA))


def test_temperatura_pico_por_la_tarde_y_luz_nula_de_noche():
    sim = g.Simulador(g.PARCELAS[1], random.Random(1))
    dia = datetime(2026, 7, 10, 0, 0, tzinfo=timezone.utc)
    horas = {h: sim.lecturas(dia + timedelta(hours=h)) for h in range(24)}
    assert max(horas, key=lambda h: horas[h]["temperature"]) in (14, 15, 16)
    assert horas[3]["light"] == 0 and horas[13]["light"] > 20000


def test_suelo_baja_y_el_riego_lo_sube():
    sim = g.Simulador(g.PARCELAS[0], random.Random(3))
    t = datetime(2026, 8, 1, 0, 0, tzinfo=timezone.utc)
    suelo = []
    for _ in range(24 * 12):  # 12 días cada hora
        suelo.append(sim.lecturas(t)["soil_moisture"])
        t += timedelta(hours=1)
    assert min(suelo) > 0
    assert any(b - a > 10 for a, b in zip(suelo, suelo[1:]))  # hubo un riego o lluvia


def test_evento_sequia_baja_del_umbral():
    p = g.PARCELAS[0]
    sim = g.Simulador(p, random.Random(1), sequia=True)
    t = AHORA
    for _ in range(12):
        v = sim.lecturas(t)["soil_moisture"]
        t += timedelta(hours=1)
    assert v < p.umbral_suelo
