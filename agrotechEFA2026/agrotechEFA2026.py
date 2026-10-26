import reflex as rx

from .pages.dashboard import dashboard


app = rx.App()
app.add_page(dashboard, route="/", title="Agrotech | Panel de control")
