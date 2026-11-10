"""Corre las 5 conversaciones de ejemplo pedidas por la consigna y guarda su traza.

  1. Solo consulta (sistema)        2. Solo consulta (documentos)
  3. Acción aprobada                4. Acción rechazada
  5. Llega al límite de pasos

Uso:  python run_demo.py          (resetea la base del cliente antes de empezar)
Las trazas quedan en docs/conversaciones/.
"""
import uuid

from langgraph.types import Command

from agente.estado import entrada_turno
from agente.grafo import aprobacion_pendiente, construir_grafo, respuesta_final
from config import DECISOR, MAX_PASOS, RAIZ
from sistema_cliente.seed import crear

CONVERSACIONES = [
    ("01_consulta_pedido", "¿En qué estado está el pedido 1042?", None),
    ("02_consulta_politica", "¿Cuál es la política de devoluciones?", None),
    ("03_accion_aprobada",
     "Reprogramá la entrega del pedido 1042 para el 2026-11-20 porque no hay nadie en el local esa semana",
     {"aprobado": True, "revisor": "ana.supervisora"}),
    ("04_accion_rechazada", "Necesito reprogramar el pedido 1043 para el 2026-12-01",
     {"aprobado": False, "revisor": "ana.supervisora", "comentario": "el pedido ya está despachado, hay que coordinar con logística"}),
    ("05_limite_de_pasos", "¿Qué dice la política sobre envíos a la Antártida?", None),
]


def correr(grafo, nombre, texto, decision_humana, usuario="cliente_12"):
    config = {"configurable": {"thread_id": f"demo-{nombre}-{uuid.uuid4().hex[:6]}"}}
    grafo.invoke(entrada_turno(texto, usuario), config)
    aprobacion = None
    pendiente = aprobacion_pendiente(grafo, config)
    if pendiente:
        aprobacion = (pendiente, decision_humana)
        grafo.invoke(Command(resume=decision_humana), config)
    estado = grafo.get_state(config).values
    return config, estado, aprobacion


def a_markdown(nombre, texto, config, estado, aprobacion) -> str:
    md = [f"# {nombre.replace('_', ' ')}", "",
          f"- thread_id: `{config['configurable']['thread_id']}`",
          f"- decisor: `{DECISOR}` · máximo de pasos: {MAX_PASOS}", "",
          f"**Usuario ({estado['usuario']}):** {texto}", ""]
    if aprobacion:
        pendiente, decision = aprobacion
        md += ["**Pausa para aprobación humana**", "",
               f"- herramienta: `{pendiente['herramienta']}`",
               f"- parámetros: `{pendiente['argumentos']}`",
               f"- decisión: {'APROBADA' if decision['aprobado'] else 'RECHAZADA'} por {decision['revisor']}"
               + (f" — {decision['comentario']}" if decision.get("comentario") else ""), ""]
    md += ["**Traza de pasos**", "", "```"] + estado["traza"] + ["```", "",
           f"**Agente:** {respuesta_final_from(estado)}", ""]
    return "\n".join(md)


def respuesta_final_from(estado):
    return estado["mensajes"][-1].content


if __name__ == "__main__":
    crear()
    grafo = construir_grafo()
    salida = RAIZ / "docs" / "conversaciones"
    salida.mkdir(parents=True, exist_ok=True)
    for nombre, texto, decision in CONVERSACIONES:
        config, estado, aprobacion = correr(grafo, nombre, texto, decision)
        md = a_markdown(nombre, texto, config, estado, aprobacion)
        (salida / f"{nombre}.md").write_text(md, encoding="utf-8")
        print(md)
        print("-" * 80)
