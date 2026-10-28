"""Datos de ejemplo para desarrollar y para la demo.

Uso (desde la raíz del repo):
    python -m agrotechEFA2026.db.seed

Crea las tablas, 2 usuarios, 3 parcelas (las mismas que el simulador) y 12 sensores, y
guarda las claves de los aparatos en `claves_demo.json` (ignorado por git) para lanzar:
    python scripts/gen_sample_data.py --url http://localhost:8000 --claves claves_demo.json

Contraseñas: AGROTECH_PASS_FARMER y AGROTECH_PASS_TECHNICIAN si están definidas
(ver .env.example); si no, se generan al azar y se muestran una sola vez.
"""
import json
import os
import secrets
from pathlib import Path

from sqlmodel import Session, select

from .models import TIPOS_MEDIDA, Crop, Parcel, ParcelViewer, Sector, Sensor, User
from .seguridad import generar_api_key, hash_api_key, hash_password
from .session import crear_tablas, obtener_motor

# (nombre, tipo, superficie m², forma, cultivo, umbral bajo de humedad del suelo)
# Parcelas y umbrales iguales que en scripts/gen_sample_data.py; superficies y formas de ejemplo.
PARCELAS_DEMO = [
    ("Invernadero tomates", "indoor", 1000.0, "rectangle", "tomate", 40.0),
    ("Aguacates", "outdoor", 6000.0, "polygon", "aguacate", 35.0),
    ("Mangos", "outdoor", 4000.0, "rectangle", "mango", 30.0),
]
# Sin rangos óptimos hasta tener fuentes fiables (ver docs/contrato.md)
CULTIVOS_DEMO = ["tomate", "aguacate", "mango", "chirimoya"]


def sembrar(s: Session, passwords: dict[str, str]) -> dict[str, str]:
    """Inserta los datos de ejemplo y devuelve {sensor_id: api_key} en el formato del simulador.

    Debe usarse con la base de datos vacía: así los sensores salen con los ids 1-12,
    en el mismo orden que el simulador (4 por parcela, en el orden de TIPOS_MEDIDA).
    """
    agricultor = User(username="agricultor", role="farmer", password_hash=hash_password(passwords["farmer"]))
    tecnico = User(username="tecnico", role="technician", password_hash=hash_password(passwords["technician"]))
    s.add_all([agricultor, tecnico])

    cultivos = {nombre: Crop(name=nombre) for nombre in CULTIVOS_DEMO}
    s.add_all(cultivos.values())
    s.flush()  # para tener los ids antes de usarlos como claves ajenas

    claves: dict[str, str] = {}
    for nombre, tipo, area, forma, cultivo, umbral_suelo in PARCELAS_DEMO:
        parcela = Parcel(owner_id=agricultor.id, name=nombre, kind=tipo, area_m2=area, shape=forma, location="Motril")
        s.add(parcela)
        s.flush()
        s.add(ParcelViewer(parcel_id=parcela.id, user_id=tecnico.id))

        # Un sector que ocupa toda la parcela, con los 4 sensores que manda el simulador
        clave = generar_api_key()
        sector = Sector(
            parcel_id=parcela.id, name="Sector 1", crop_id=cultivos[cultivo].id, api_key_hash=hash_api_key(clave)
        )
        s.add(sector)
        s.flush()

        for tipo_medida, (unidad, _, _) in TIPOS_MEDIDA.items():
            bajo = umbral_suelo if tipo_medida == "soil_moisture" else None
            sensor = Sensor(sector_id=sector.id, type=tipo_medida, unit=unidad, threshold_low=bajo)
            s.add(sensor)
            s.flush()
            claves[str(sensor.id)] = clave

    s.commit()
    return claves


def _password(variable: str) -> tuple[str, bool]:
    """Devuelve la contraseña y si se ha generado al azar."""
    valor = os.environ.get(variable)
    return (valor, False) if valor else (secrets.token_urlsafe(9), True)


def main() -> None:
    motor = obtener_motor()
    crear_tablas(motor)
    with Session(motor) as s:
        if s.exec(select(User)).first():
            print("La base de datos ya tiene datos; no se toca. Borra agrotech.db para empezar de cero.")
            return
        passwords, generadas = {}, []
        for rol, variable in (("farmer", "AGROTECH_PASS_FARMER"), ("technician", "AGROTECH_PASS_TECHNICIAN")):
            passwords[rol], al_azar = _password(variable)
            if al_azar:
                generadas.append(rol)
        claves = sembrar(s, passwords)

    Path("claves_demo.json").write_text(json.dumps(claves, indent=2), encoding="utf-8")
    print(f"Creados 2 usuarios, {len(PARCELAS_DEMO)} parcelas y {len(claves)} sensores.")
    print("Claves de los aparatos guardadas en claves_demo.json")
    for rol in generadas:
        usuario = "agricultor" if rol == "farmer" else "tecnico"
        print(f"Contraseña generada para '{usuario}': {passwords[rol]}  (apúntala: no se vuelve a mostrar)")


if __name__ == "__main__":
    main()
