"""Tests del grafo con el decisor de reglas (no necesitan API key).

Uso:  python -m pytest -q
"""
import sqlite3
import sys
import uuid
from pathlib import Path

import pytest
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import Command

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from agente.decisor import DecisorReglas  # noqa: E402
from agente.estado import entrada_turno  # noqa: E402
from agente.grafo import aprobacion_pendiente, construir_grafo, respuesta_final  # noqa: E402
from config import DB_CLIENTE, MAX_PASOS  # noqa: E402
from sistema_cliente.seed import crear  # noqa: E402


@pytest.fixture
def grafo():
    crear()
    return construir_grafo(decisor=DecisorReglas(), checkpointer=InMemorySaver())


def cfg():
    return {"configurable": {"thread_id": uuid.uuid4().hex}}


def fecha_de(pedido_id):
    with sqlite3.connect(DB_CLIENTE) as con:
        return con.execute("SELECT fecha_entrega FROM pedidos WHERE id=?", (pedido_id,)).fetchone()[0]


def test_consulta_no_pide_aprobacion(grafo):
    c = cfg()
    grafo.invoke(entrada_turno("¿Cómo viene el pedido 1042?", "t"), c)
    assert aprobacion_pendiente(grafo, c) is None
    assert "en preparación" in respuesta_final(grafo, c)


def test_escritura_pausa_y_aprobada_ejecuta(grafo):
    c = cfg()
    grafo.invoke(entrada_turno("Reprogramá el pedido 1042 para el 2026-11-25", "t"), c)
    pendiente = aprobacion_pendiente(grafo, c)
    assert pendiente["herramienta"] == "reprogramar_entrega"
    assert fecha_de(1042) == "2026-11-10"          # todavía no se escribió nada
    grafo.invoke(Command(resume={"aprobado": True, "revisor": "test"}), c)
    assert fecha_de(1042) == "2026-11-25"


def test_escritura_rechazada_no_ejecuta(grafo):
    c = cfg()
    grafo.invoke(entrada_turno("Reprogramá el pedido 1042 para el 2026-11-25", "t"), c)
    grafo.invoke(Command(resume={"aprobado": False, "revisor": "test"}), c)
    assert fecha_de(1042) == "2026-11-10"
    assert "rechazada" in respuesta_final(grafo, c)


def test_bucle_termina_en_el_limite(grafo):
    c = cfg()
    grafo.invoke(entrada_turno("¿Qué dice la política sobre envíos a la Antártida?", "t"), c)
    estado = grafo.get_state(c).values
    assert estado["pasos"] == MAX_PASOS
    assert "máximo" in respuesta_final(grafo, c)
