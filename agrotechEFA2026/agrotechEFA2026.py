import reflex as rx

from .api import api
from .db.migrar import actualizar_bd
from .pages.dashboard import dashboard

# Aplica las migraciones que falten (la primera vez crea agrotech.db); no borra datos
actualizar_bd()

app = rx.App(api_transformer=api)
app.add_page(dashboard, route="/", title="Agrotech | Panel de control")
