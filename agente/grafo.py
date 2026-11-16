"""El grafo del agente: un nodo por paso y un nodo por cada tool.

    inicio -> decidir -> <tool de lectura> -> decidir ...        (bucle con máximo de pasos)
                      -> pedir_aprobacion -> <tool de escritura> -> decidir
                      -> responder -> fin

Los nodos de las tools se crean solos a partir de agente/tools: sumar una tool suma su nodo.
"""
import json
import sqlite3

from langchain_core.messages import AIMessage, ToolMessage
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import interrupt

from agente import llm
from agente.model import (
    DecisionAprobacion, ErrorHerramienta, EstadoAgente, Rechazo, SolicitudAprobacion,
)
from agente.tools import ESCRITURA, LECTURA, TODAS, es_escritura
from config import DB_CHECKPOINTS, MAX_PASOS


def _ultimo_ai(mensajes: list) -> AIMessage:
    return next(m for m in reversed(mensajes) if isinstance(m, AIMessage))


def _escrituras(ai: AIMessage) -> list[dict]:
    return [c for c in ai.tool_calls if es_escritura(c["name"])]


def _nodos_de_tools(ai: AIMessage) -> list[str]:
    """Los nodos (uno por tool distinta) que hay que correr para este mensaje del modelo."""
    return list(dict.fromkeys(c["name"] for c in ai.tool_calls))


def nodo_tool(tool):
    """Crea el nodo de una tool: ejecuta sus tool_calls y devuelve un ToolMessage por cada una."""

    def ejecutar(estado: EstadoAgente) -> dict:
        resultados, traza = [], []
        for llamada in (c for c in _ultimo_ai(estado.mensajes).tool_calls if c["name"] == tool.name):
            decision = estado.aprobaciones.get(llamada["id"])
            if decision and not DecisionAprobacion(**decision).aprobado:
                salida = Rechazo(revisor=decision.get("revisor"), comentario=decision.get("comentario", "")).model_dump()
            else:
                try:
                    salida = tool.invoke(llamada["args"])
                except Exception as e:  # una falla de la tool no tira el grafo: se la contamos al modelo
                    salida = ErrorHerramienta(error=f"{type(e).__name__}: {e}").model_dump()
            texto = json.dumps(salida, ensure_ascii=False, default=str)
            resultados.append(ToolMessage(content=texto, name=tool.name, tool_call_id=llamada["id"]))
            traza.append(f"{tool.name} -> {texto[:140]}")
        return {"mensajes": resultados, "traza": traza}

    return ejecutar


def construir_grafo(checkpointer=None, max_pasos: int = MAX_PASOS):

    # ---------------- nodos ----------------
    def decidir(estado: EstadoAgente) -> dict:
        """El modelo (con bind_tools) responde con texto o pide tools."""
        if estado.pasos >= max_pasos:
            return {"limite": True, "traza": [f"decidir -> LÍMITE de {max_pasos} pasos"]}
        ai = llm.decidir(estado.mensajes)
        escrituras = _escrituras(ai)
        llamadas = ", ".join(f"{c['name']}({json.dumps(c['args'], ensure_ascii=False)})" for c in ai.tool_calls)
        pendiente = (SolicitudAprobacion(usuario=estado.usuario, herramienta=escrituras[0]["name"],
                                         argumentos=escrituras[0]["args"]).model_dump(exclude={"tipo"})
                     if escrituras else None)
        return {"mensajes": [ai], "pasos": estado.pasos + 1, "aprobaciones": {},
                "pendiente_aprobacion": pendiente,
                "traza": [f"paso {estado.pasos + 1}: decidir -> {llamadas or 'responder'}"]}

    def pedir_aprobacion(estado: EstadoAgente) -> dict:
        """Pausa el grafo por cada tool de escritura hasta que una persona responda."""
        ai = _ultimo_ai(estado.mensajes)
        aprobaciones, traza = {}, []
        for llamada in _escrituras(ai):
            pedido = SolicitudAprobacion(usuario=estado.usuario, herramienta=llamada["name"],
                                         argumentos=llamada["args"], razon=ai.text, tool_call_id=llamada["id"])
            decision = DecisionAprobacion(**interrupt(pedido.model_dump()))  # <- acá se pausa
            aprobaciones[llamada["id"]] = decision.model_dump()
            traza.append(f"pedir_aprobacion -> {llamada['name']} "
                         f"{'APROBADA' if decision.aprobado else 'RECHAZADA'} por {decision.revisor}")
        return {"aprobaciones": aprobaciones, "pendiente_aprobacion": None, "traza": traza}

    def responder(estado: EstadoAgente) -> dict:
        """Cierra el turno. Si se agotaron los pasos, pide un cierre explícito al modelo."""
        if estado.limite:
            return {"mensajes": [llm.cerrar_por_limite(estado.mensajes, max_pasos)],
                    "traza": ["responder -> fin (por límite)"]}
        return {"traza": ["responder -> fin"]}  # la respuesta ya la dio decidir

    # ---------------- aristas ----------------
    def despues_de_decidir(estado: EstadoAgente):
        if estado.limite or not _ultimo_ai(estado.mensajes).tool_calls:
            return "responder"
        if estado.pendiente_aprobacion:
            return "pedir_aprobacion"
        return _nodos_de_tools(_ultimo_ai(estado.mensajes))  # lecturas: una o varias en paralelo

    def despues_de_aprobar(estado: EstadoAgente):
        return _nodos_de_tools(_ultimo_ai(estado.mensajes))

    g = StateGraph(EstadoAgente)
    g.add_node("decidir", decidir)
    g.add_node("pedir_aprobacion", pedir_aprobacion)
    for tool in TODAS:  # un nodo por tool
        g.add_node(tool.name, nodo_tool(tool))
    g.add_node("responder", responder)

    g.add_edge(START, "decidir")
    g.add_conditional_edges("decidir", despues_de_decidir,
                            ["responder", "pedir_aprobacion", *(t.name for t in LECTURA)])
    g.add_conditional_edges("pedir_aprobacion", despues_de_aprobar, [t.name for t in TODAS])
    for tool in TODAS:
        g.add_edge(tool.name, "decidir")
    g.add_edge("responder", END)

    if checkpointer is None:  # memoria persistente: se retoma con el mismo thread_id
        DB_CHECKPOINTS.parent.mkdir(parents=True, exist_ok=True)
        checkpointer = SqliteSaver(sqlite3.connect(DB_CHECKPOINTS, check_same_thread=False))
    return g.compile(checkpointer=checkpointer)


def aprobacion_pendiente(grafo, config) -> dict | None:
    """Si el thread está pausado esperando aprobación, devuelve qué se va a ejecutar."""
    for tarea in grafo.get_state(config).tasks:
        for intr in tarea.interrupts:
            return intr.value
    return None


def respuesta_final(estado: dict) -> str:
    """Texto de la última respuesta del modelo."""
    return _ultimo_ai(estado["mensajes"]).text if estado.get("mensajes") else ""
