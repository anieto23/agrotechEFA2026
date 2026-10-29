import reflex as rx

from .api import api
from .db.migrar import actualizar_bd
from .pages.alertas import alertas
from .pages.dashboard import dashboard
from .pages.parcelas import parcelas
from .pages.sensores import sensores

# Aplica las migraciones que falten (la primera vez crea agrotech.db); no borra datos
actualizar_bd()

app = rx.App(api_transformer=api)
app.add_page(dashboard, route="/", title="Agrotech | Panel de control")
app.add_page(parcelas, route="/parcelas", title="Agrotech | Parcelas")
app.add_page(sensores, route="/sensores", title="Agrotech | Sensores")
app.add_page(alertas, route="/alertas", title="Agrotech | Alertas")
