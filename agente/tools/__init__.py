"""Todas las tools del agente: read/ (lectura) y write/ (escritura)."""
from agente.tools.read import LECTURA
from agente.tools.write import ESCRITURA

TODAS = [*LECTURA, *ESCRITURA]
_NOMBRES_ESCRITURA = {t.name for t in ESCRITURA}


def es_escritura(nombre: str) -> bool:
    """True si la tool modifica el sistema y por lo tanto necesita aprobación humana."""
    return nombre in _NOMBRES_ESCRITURA
