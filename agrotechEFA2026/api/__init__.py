"""API REST de Agrotech. Se monta en la app de Reflex con `rx.App(api_transformer=api)`.

Documentación interactiva en http://localhost:8000/docs con la app en marcha.
"""
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from .lecturas import router as router_lecturas

api = FastAPI(title="Agrotech API", description="Sensores de parcelas agrícolas (II Reto Agrotech 2026)")
api.include_router(router_lecturas, prefix="/api")


@api.exception_handler(RequestValidationError)
async def _datos_no_validos(_: Request, error: RequestValidationError) -> JSONResponse:
    # El contrato pide siempre {"detail": "<texto>"}, no la lista de errores de FastAPI
    campos = ", ".join(".".join(str(p) for p in e["loc"] if p != "body") or "cuerpo" for e in error.errors())
    return JSONResponse(status_code=422, content={"detail": f"Datos no válidos en: {campos}."})
