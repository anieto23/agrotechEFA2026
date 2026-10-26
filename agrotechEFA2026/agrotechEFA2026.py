import reflex as rx

from .api import api
from .db.session import crear_tablas
from .pages.dashboard import dashboard

# Crea las tablas que falten (la primera vez, agrotech.db); las que ya existen no se tocan
crear_tablas()

app = rx.App(api_transformer=api)
app.add_page(dashboard, route="/", title="Agrotech | Panel de control")
