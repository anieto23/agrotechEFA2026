from scripts import esp32_virtual as v


def test_volcar_conserva_lo_pendiente_si_falla(monkeypatch):
    resultados = iter([True, False])
    monkeypatch.setattr(v, "enviar", lambda *a: next(resultados))
    pendientes = [{"n": 1}, {"n": 2}, {"n": 3}]
    v.volcar("u", "k", pendientes)
    assert pendientes == [{"n": 2}, {"n": 3}]


def test_volcar_limita_la_memoria(monkeypatch):
    monkeypatch.setattr(v, "enviar", lambda *a: False)
    pendientes = [{"n": i} for i in range(v.MAX_PENDIENTES + 50)]
    v.volcar("u", "k", pendientes)
    assert len(pendientes) == v.MAX_PENDIENTES and pendientes[-1] == {"n": v.MAX_PENDIENTES + 49}
