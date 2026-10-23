"""Página de Sensores. De momento vacía: sirve para probar el menú (tarea C1)."""

import reflex as rx

from ..components.layout import en_construccion, pagina


def sensores() -> rx.Component:
    return pagina(
        en_construccion("Aquí irán los sensores de cada parcela, sus umbrales y su clave API (tarea C4)."),
        "Sensores",
    )
