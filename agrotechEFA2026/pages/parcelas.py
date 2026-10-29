"""Página de Parcelas. De momento vacía: sirve para probar el menú (tarea C1)."""

import reflex as rx

from ..components.layout import en_construccion, pagina


def parcelas() -> rx.Component:
    return pagina(
        en_construccion("Aquí irá la tabla de parcelas con su formulario de alta y edición (tarea C3)."),
        "Parcelas",
    )
