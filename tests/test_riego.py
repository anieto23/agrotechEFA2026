from agrotechEFA2026.services.riego import decidir

TOMATE = {"umbral_suelo": 40, "objetivo_suelo": 65, "min_por_punto": 0.8}
SECO = {"lluvia_mm": 0.0, "tmax": 25.0, "en_vivo": True}


def test_suelo_seco_riega():
    r = decidir(28, TOMATE, SECO)
    assert r["regar"] and r["minutos"] == round((65 - 28) * 0.8) and r["confianza"] == "alta"


def test_suelo_seco_con_lluvia_no_riega():
    r = decidir(28, TOMATE, {**SECO, "lluvia_mm": 5.0})
    assert not r["regar"] and r["minutos"] == 0 and "lloverá" in r["motivo"]


def test_suelo_humedo_no_riega():
    assert not decidir(55, TOMATE, SECO)["regar"]


def test_calor_aumenta_el_tiempo():
    assert decidir(28, TOMATE, {**SECO, "tmax": 33.0})["minutos"] > decidir(28, TOMATE, SECO)["minutos"]


def test_sin_prevision_confianza_media_y_sin_datos_no_recomienda():
    assert decidir(28, TOMATE, None)["confianza"] == "media"
    assert decidir(28, TOMATE, {**SECO, "en_vivo": False})["confianza"] == "media"
    r = decidir(None, TOMATE, SECO)
    assert not r["regar"] and r["confianza"] == "baja"
