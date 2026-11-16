"""UI web del agente (estilo "adk web"): chat + eventos en vivo + grafo.

Uso:  make ui      (o:  python ui/server.py)   →  http://localhost:8000

Cómo funciona:
- Cada mensaje o aprobación corre el grafo en un hilo aparte con
  grafo.stream(..., stream_mode="tasks"), que emite un evento cuando cada nodo
  arranca y cuando termina (con su actualización de estado o su interrupt).
- Esos eventos viajan al navegador por Server-Sent Events (SSE) y la página
  los muestra en la línea de tiempo, en el chat y resaltando el nodo en el grafo.
- El estado vive en el checkpointer SQLite (data/checkpoints.db): si recargás
  la página con el mismo thread_id, la conversación sigue donde quedó.
"""
import json
import os
import queue
import sys
import threading
import time
import webbrowser
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from fastapi import FastAPI  # noqa: E402
from fastapi.responses import FileResponse, StreamingResponse  # noqa: E402
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, ToolMessage  # noqa: E402
from langgraph.types import Command  # noqa: E402
from pydantic import BaseModel  # noqa: E402

from agente.models import entrada_turno  # noqa: E402
from agente import llm  # noqa: E402
from agente.grafo import aprobacion_pendiente, construir_grafo, respuesta_final  # noqa: E402
from agente.tools import es_escritura  # noqa: E402
from config import MAX_PASOS, MODELO  # noqa: E402

AQUI = Path(__file__).resolve().parent
app = FastAPI(title="Agente supervisado · UI")
grafo = construir_grafo()
candados: dict[str, threading.Lock] = {}


# ---------------------------------------------------------------- serialización
def _json(valor):
    """Convierte el estado de LangGraph (mensajes incluidos) a algo serializable."""
    if isinstance(valor, AIMessage):
        return {"rol": "ai", "contenido": valor.text,
                "tool_calls": [{"nombre": c["name"], "argumentos": c["args"]} for c in valor.tool_calls]}
    if isinstance(valor, ToolMessage):
        return {"rol": "tool", "nombre": valor.name, "contenido": valor.content}
    if isinstance(valor, BaseMessage):
        return {"rol": valor.type, "contenido": valor.text}
    if isinstance(valor, dict):
        return {k: _json(v) for k, v in valor.items()}
    if isinstance(valor, (list, tuple)):
        return [_json(v) for v in valor]
    if isinstance(valor, (str, int, float, bool)) or valor is None:
        return valor
    return str(valor)


def _sse(evento: dict) -> str:
    return f"data: {json.dumps(evento, ensure_ascii=False)}\n\n"


# ---------------------------------------------------------------- ejecución
def _correr(entrada, thread_id: str, cola: queue.Queue):
    config = {"configurable": {"thread_id": thread_id}}
    candado = candados.setdefault(thread_id, threading.Lock())
    if not candado.acquire(blocking=False):
        cola.put({"tipo": "error", "detalle": "Este thread ya está procesando un mensaje."})
        cola.put(None)
        return
    try:
        cola.put({"tipo": "inicio_run", "t": time.time()})
        inicios = {}
        for _, ev in grafo.stream(entrada, config, stream_mode=["tasks"]):
            nodo = ev["name"]
            if "input" in ev:  # el nodo arranca
                inicios[ev["id"]] = time.time()
                cola.put({"tipo": "nodo_inicio", "nodo": nodo, "t": time.time()})
                continue
            dur = round((time.time() - inicios.pop(ev["id"], time.time())) * 1000)
            actualizacion = _json(dict(ev.get("result") or {}))
            cola.put({"tipo": "nodo_fin", "nodo": nodo, "ms": dur, "t": time.time(),
                      "actualizacion": actualizacion,
                      "error": str(ev["error"]) if ev.get("error") else None})
            for intr in ev.get("interrupts") or []:
                cola.put({"tipo": "aprobacion", "payload": _json(intr["value"]), "t": time.time()})
        if not aprobacion_pendiente(grafo, config):
            texto = respuesta_final(grafo.get_state(config).values)
            cola.put({"tipo": "respuesta", "texto": texto, "t": time.time()})
    except Exception as e:  # que el error llegue a la UI en lugar de cortar el stream
        cola.put({"tipo": "error", "detalle": f"{type(e).__name__}: {e}", "t": time.time()})
    finally:
        candado.release()
        cola.put({"tipo": "fin_run", "t": time.time()})
        cola.put(None)


def _stream(entrada, thread_id: str) -> StreamingResponse:
    cola: queue.Queue = queue.Queue()
    threading.Thread(target=_correr, args=(entrada, thread_id, cola), daemon=True).start()

    def generar():
        while (evento := cola.get()) is not None:
            yield _sse(evento)

    return StreamingResponse(generar(), media_type="text/event-stream",
                             headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})


# ---------------------------------------------------------------- API
class Mensaje(BaseModel):
    thread_id: str
    texto: str
    usuario: str = "cliente_12"


class Aprobacion(BaseModel):
    thread_id: str
    aprobado: bool
    comentario: str = ""
    revisor: str = "ui"


@app.get("/")
def index():
    return FileResponse(AQUI / "index.html")


@app.get("/api/info")
def info():
    return {
        "modelo": MODELO, "max_pasos": MAX_PASOS,
        "herramientas": [{"nombre": t.name, "solo_lectura": not es_escritura(t.name),
                          "descripcion": t.description.splitlines()[0]} for t in llm.tools()],
    }


@app.get("/api/grafo")
def grafo_mermaid():
    g = grafo.get_graph()
    return {"mermaid": g.draw_mermaid(), "nodos": list(g.nodes.keys())}


@app.get("/api/estado")
def estado(thread_id: str):
    config = {"configurable": {"thread_id": thread_id}}
    valores = grafo.get_state(config).values
    mensajes = [_json(m) for m in valores.get("mensajes", [])
                if isinstance(m, HumanMessage) or (isinstance(m, AIMessage) and m.text)]
    return {"mensajes": mensajes, "pendiente": _json(aprobacion_pendiente(grafo, config)),
            "pasos": valores.get("pasos", 0)}


@app.post("/api/mensaje")
def mensaje(m: Mensaje):
    return _stream(entrada_turno(m.texto, m.usuario), m.thread_id)


@app.post("/api/aprobar")
def aprobar(a: Aprobacion):
    return _stream(Command(resume={"aprobado": a.aprobado, "revisor": a.revisor,
                                   "comentario": a.comentario}), a.thread_id)


if __name__ == "__main__":
    import uvicorn

    puerto = int(os.getenv("PORT", "8000"))
    url = f"http://localhost:{puerto}"
    print(f"\n  UI del agente en {url}   (Ctrl+C para cortar)\n")
    if not os.getenv("NO_BROWSER"):
        threading.Timer(1.5, webbrowser.open, args=(url,)).start()
    uvicorn.run(app, host="127.0.0.1", port=puerto, log_level="warning")
