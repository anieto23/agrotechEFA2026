"""Exportar el histórico: CSV por rango de fechas e informe PDF de una página."""
import csv
import io
from datetime import datetime
from typing import Optional

from fpdf import FPDF

from ..db import consultas

NOMBRES = {"temperature": "Temperatura", "air_humidity": "Humedad del aire",
           "soil_moisture": "Humedad del suelo", "light": "Luz"}
LIMITE = 5000  # máximo de la API (ver docs/contrato.md)


def historico_csv(usuario_id: int, parcela_id: int, desde: datetime, hasta: datetime) -> str:
    """CSV con sensor_id, tipo, unidad, fecha (UTC) y valor de todos los sensores de la parcela."""
    salida = io.StringIO()
    w = csv.writer(salida)
    w.writerow(["sensor_id", "type", "unit", "timestamp", "value"])
    for e in consultas.ultimas_lecturas(usuario_id, parcela_id):
        for d in consultas.historico(usuario_id, e.sensor_id, desde, hasta, LIMITE):
            w.writerow([e.sensor_id, e.type, e.unit, d.timestamp.isoformat(timespec="seconds"), d.value])
    return salida.getvalue()


def _grafico(pdf: FPDF, x: float, y: float, w: float, h: float, puntos: list[float], titulo: str) -> None:
    pdf.set_font("Helvetica", "B", 10)
    pdf.text(x, y - 2, titulo)
    pdf.rect(x, y, w, h)
    if len(puntos) < 2:
        return
    lo, hi = min(puntos), max(puntos)
    hi = hi if hi > lo else lo + 1
    xy = [(x + w * i / (len(puntos) - 1), y + h - h * (v - lo) / (hi - lo)) for i, v in enumerate(puntos)]
    pdf.set_draw_color(30, 120, 60)
    for (x1, y1), (x2, y2) in zip(xy, xy[1:]):
        pdf.line(x1, y1, x2, y2)
    pdf.set_draw_color(0, 0, 0)
    pdf.set_font("Helvetica", "", 8)
    pdf.text(x + w + 2, y + 3, f"{hi:.1f}")
    pdf.text(x + w + 2, y + h, f"{lo:.1f}")


def informe_pdf(usuario_id: int, parcela_id: int, desde: datetime, hasta: datetime,
                recomendacion: Optional[str] = None) -> bytes:
    """Una página: últimas lecturas, un gráfico por magnitud y la recomendación de riego."""
    parcela = consultas.obtener_parcela(usuario_id, parcela_id)
    if parcela is None:
        raise ValueError("La parcela no existe o no tienes permiso para verla.")
    estados = consultas.ultimas_lecturas(usuario_id, parcela_id)
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, f"Agrotech - {parcela.name}", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 9)
    pdf.cell(0, 6, f"Del {desde:%d/%m/%Y} al {hasta:%d/%m/%Y}", new_x="LMARGIN", new_y="NEXT")
    if recomendacion:
        pdf.set_font("Helvetica", "B", 10)
        pdf.multi_cell(0, 6, f"Riego: {recomendacion}", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)
    pdf.set_font("Helvetica", "", 10)
    for e in estados:
        valor = "sin datos" if e.value is None else f"{e.value:g} {e.unit}"
        pdf.cell(0, 6, f"{NOMBRES.get(e.type, e.type)}: {valor}  [{e.status}]", new_x="LMARGIN", new_y="NEXT")
    y = pdf.get_y() + 12
    for i, e in enumerate(estados):
        serie = [d.value for d in consultas.historico(usuario_id, e.sensor_id, desde, hasta, LIMITE)]
        x = 15 if i % 2 == 0 else 110
        _grafico(pdf, x, y + (i // 2) * 60, 75, 40, serie[:: max(1, len(serie) // 200)], NOMBRES.get(e.type, e.type))
    return bytes(pdf.output())
