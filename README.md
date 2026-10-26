# agrotechEFA2026
Proyecto de EFA El Soto para el Reto Agrotech 2026

App para dibujar la parcela a escala, colocar sus sensores, comparar cada lectura con
los valores óptimos del cultivo y actuar desde el móvil. Idea completa y fases en
[`docs/IDEA-PROYECTO.md`](docs/IDEA-PROYECTO.md).

## Instalación

Requiere Python 3.11 o superior.

```bash
python -m venv .venv
.venv\Scripts\Activate.ps1        # Windows (en Linux/Mac: source .venv/bin/activate)
pip install -r requirements.txt
python -m pytest                  # comprobar que todo funciona
python -m reflex run              # web en http://localhost:3000
```

## Base de datos

Tablas, API y funciones descritas en [`docs/contrato.md`](docs/contrato.md); el código está en
`agrotechEFA2026/db/`. Por defecto usa SQLite (`agrotech.db`); para MySQL/MariaDB, define
`AGROTECH_DB_URL` (ver `.env.example`).

Datos de ejemplo (2 usuarios, las 3 parcelas del simulador y 12 sensores):

```bash
python -m agrotechEFA2026.db.seed
```

Muestra las contraseñas de `agricultor` y `tecnico` si no están en `AGROTECH_PASS_FARMER` /
`AGROTECH_PASS_TECHNICIAN`, y guarda las claves de los aparatos en `claves_demo.json` para
el simulador (`--claves claves_demo.json`).

## Panel de control

La aplicación registra la página principal desde `agrotechEFA2026/agrotechEFA2026.py`.
La interfaz del panel está en `agrotechEFA2026/pages/dashboard.py`; sus tarjetas
reutilizables y la paleta de colores están en `agrotechEFA2026/components/`.
Los valores actuales son datos ficticios para probar la interfaz.
