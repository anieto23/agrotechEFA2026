from scripts.vigilante import ENFRIAMIENTO, decidir

SECO = {"sensor_id": 2, "type": "soil_moisture", "value": 18.0, "unit": "%"}
BIEN = {**SECO, "value": 40.0}


def test_en_rango_no_avisa():
    assert decidir(BIEN, {}, 0) is None


def test_fuera_de_rango_avisa():
    assert "baja" in decidir(SECO, {}, 0)


def test_no_repite_dentro_del_enfriamiento():
    estado = {}
    assert decidir(SECO, estado, 0)
    assert decidir(SECO, estado, ENFRIAMIENTO - 1) is None
    assert decidir(SECO, estado, ENFRIAMIENTO)


def test_al_volver_a_rango_el_siguiente_fallo_avisa():
    estado = {}
    decidir(SECO, estado, 0)
    decidir(BIEN, estado, 10)
    assert decidir(SECO, estado, 20)
