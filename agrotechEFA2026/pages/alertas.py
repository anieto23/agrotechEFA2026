"""Página de Alertas. De momento vacía: sirve para probar el menú (tarea C1)."""

import reflex as rx

from ..components.layout import en_construccion, pagina


def alertas() -> rx.Component:
    return pagina(
        en_construccion("Aquí irá la lista de alertas con filtros y el botón Reconocer (tarea C6)."),
        "Alertas",
    )
