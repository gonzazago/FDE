"""Modelos de datos (pydantic): qué forma tienen el estado, las aprobaciones y los resultados."""
from agente.models.aprobacion import DecisionAprobacion, SolicitudAprobacion
from agente.models.estado import EstadoAgente, entrada_turno
from agente.models.herramientas import (
    ConsultaDocumentos, ErrorHerramienta, Fragmento, Rechazo, ResultadoBusqueda,
)

__all__ = [
    "EstadoAgente", "entrada_turno", "SolicitudAprobacion", "DecisionAprobacion",
    "ConsultaDocumentos", "Fragmento", "ResultadoBusqueda", "Rechazo", "ErrorHerramienta",
]
