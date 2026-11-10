"""Grafo del agente supervisado.

    START -> decidir -> (ejecutar_herramienta | pedir_aprobacion | responder)
    ejecutar_herramienta -> decidir          (bucle, con máximo de pasos)
    pedir_aprobacion --aprobada--> ejecutar_herramienta
    pedir_aprobacion --rechazada--> responder
    responder -> END
"""
import json
import sqlite3
import uuid

from langchain_core.messages import AIMessage, ToolMessage
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, interrupt

from agente.decisor import crear_decisor
from agente.estado import EstadoAgente
from agente.mcp_cliente import herramienta, llamar_herramienta
from agente.rag import buscar_documentos
from config import DB_CHECKPOINTS, DECISOR, MAX_PASOS


def construir_grafo(decisor=None, checkpointer=None):
    decisor = decisor or crear_decisor(DECISOR)

    # ---------------- nodos ----------------
    def decidir(estado: EstadoAgente) -> dict:
        if estado["pasos"] >= MAX_PASOS:
            return {"decision": {"accion": "limite", "razon": f"Se alcanzó el máximo de {MAX_PASOS} pasos."},
                    "traza": estado["traza"] + [f"decidir -> LÍMITE de {MAX_PASOS} pasos"]}
        d = decisor.decidir(estado)
        pendiente = None
        if d.accion == "usar_herramienta" and not herramienta(d.herramienta).solo_lectura:
            pendiente = {"herramienta": d.herramienta, "argumentos": d.argumentos, "razon": d.razon}
        etiqueta = d.herramienta or d.accion
        return {
            "decision": d.model_dump(),
            "pasos": estado["pasos"] + 1,
            "pendiente_aprobacion": pendiente,
            "traza": estado["traza"] + [f"paso {estado['pasos'] + 1}: decidir -> {etiqueta} "
                                        f"{json.dumps(d.argumentos, ensure_ascii=False)} | {d.razon}"],
        }

    def pedir_aprobacion(estado: EstadoAgente) -> Command:
        pendiente = estado["pendiente_aprobacion"]
        # El grafo se pausa acá. El checkpointer guarda el estado; se retoma con
        # graph.invoke(Command(resume={"aprobado": bool, "revisor": str, "comentario": str}), config)
        respuesta = interrupt({"tipo": "aprobacion", "usuario": estado["usuario"], **pendiente})
        aprobado = bool(respuesta.get("aprobado"))
        revisor = respuesta.get("revisor", "revisor")
        linea = f"pedir_aprobacion -> {'APROBADA' if aprobado else 'RECHAZADA'} por {revisor}"
        if aprobado:
            return Command(goto="ejecutar_herramienta",
                           update={"pendiente_aprobacion": None, "traza": estado["traza"] + [linea]})
        salida = {"rechazado": True, "revisor": revisor, "comentario": respuesta.get("comentario", "")}
        return Command(goto="responder", update={
            "pendiente_aprobacion": None,
            "resultados": estado["resultados"] + [{"herramienta": pendiente["herramienta"],
                                                   "argumentos": pendiente["argumentos"], "salida": salida}],
            "traza": estado["traza"] + [linea],
        })

    def ejecutar_herramienta(estado: EstadoAgente) -> dict:
        d = estado["decision"]
        nombre = "buscar_documentos" if d["accion"] == "buscar_documentos" else d["herramienta"]
        try:
            salida = (buscar_documentos(**d["argumentos"]) if nombre == "buscar_documentos"
                      else llamar_herramienta(nombre, d["argumentos"]))
        except Exception as e:  # una falla de red/herramienta no debe tirar el grafo
            salida = {"ok": False, "error": f"{type(e).__name__}: {e}"}
        resumen = json.dumps(salida, ensure_ascii=False, default=str)
        return {
            "resultados": estado["resultados"] + [{"herramienta": nombre, "argumentos": d["argumentos"],
                                                   "salida": salida}],
            "mensajes": [ToolMessage(content=resumen, name=nombre, tool_call_id=str(uuid.uuid4()))],
            "traza": estado["traza"] + [f"ejecutar_herramienta -> {nombre}: {resumen[:140]}"],
        }

    def responder(estado: EstadoAgente) -> dict:
        limite = (estado.get("decision") or {}).get("accion") == "limite"
        texto = decisor.responder(estado, limite=limite)
        return {"mensajes": [AIMessage(content=texto)], "traza": estado["traza"] + ["responder -> fin"]}

    # ---------------- aristas ----------------
    def ruta_desde_decidir(estado: EstadoAgente) -> str:
        accion = estado["decision"]["accion"]
        if accion in ("responder", "limite"):
            return "responder"
        if estado["pendiente_aprobacion"]:
            return "pedir_aprobacion"
        return "ejecutar_herramienta"

    g = StateGraph(EstadoAgente)
    g.add_node("decidir", decidir)
    g.add_node("ejecutar_herramienta", ejecutar_herramienta)
    g.add_node("pedir_aprobacion", pedir_aprobacion, destinations=("ejecutar_herramienta", "responder"))
    g.add_node("responder", responder)
    g.add_edge(START, "decidir")
    g.add_conditional_edges("decidir", ruta_desde_decidir,
                            ["ejecutar_herramienta", "pedir_aprobacion", "responder"])
    g.add_edge("ejecutar_herramienta", "decidir")
    g.add_edge("responder", END)

    if checkpointer is None:
        DB_CHECKPOINTS.parent.mkdir(parents=True, exist_ok=True)
        checkpointer = SqliteSaver(sqlite3.connect(DB_CHECKPOINTS, check_same_thread=False))
    return g.compile(checkpointer=checkpointer)


def aprobacion_pendiente(grafo, config) -> dict | None:
    """Si el thread está pausado esperando aprobación, devuelve lo que se va a ejecutar."""
    estado = grafo.get_state(config)
    for tarea in estado.tasks:
        for intr in tarea.interrupts:
            return intr.value
    return None


def respuesta_final(grafo, config) -> str:
    mensajes = grafo.get_state(config).values.get("mensajes", [])
    return mensajes[-1].content if mensajes and isinstance(mensajes[-1], AIMessage) else ""
