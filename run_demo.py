"""Corre las 5 conversaciones de ejemplo de la consigna y guarda su traza en docs/conversaciones/.

  1. Solo consulta (sistema)     2. Solo consulta (documentos)
  3. Acción aprobada             4. Acción rechazada
  5. Llega al límite de pasos (se corre con un máximo de 2 pasos)

Uso:  make demo   (o: python run_demo.py). Usa Claude: necesita ANTHROPIC_API_KEY en .env.
"""
import uuid

from langgraph.types import Command

from agente.model import entrada_turno
from agente.grafo import aprobacion_pendiente, construir_grafo, respuesta_final
from config import MAX_PASOS, MODELO, RAIZ
from sistema_cliente.seed import crear

APROBAR = {"aprobado": True, "revisor": "ana.supervisora"}
RECHAZAR = {"aprobado": False, "revisor": "ana.supervisora", "comentario": "falta confirmar el pago del pedido"}

# (archivo, mensaje del usuario, respuesta de la persona si se pide aprobación, máximo de pasos)
CONVERSACIONES = [
    ("01_consulta_pedido", "¿En qué estado está el pedido 1042?", None, MAX_PASOS),
    ("02_consulta_politica", "¿Cuál es la política de devoluciones?", None, MAX_PASOS),
    ("03_accion_aprobada", "Reprogramá la entrega del pedido 1042 para el 2026-11-20 porque cierra el local esa semana",
     APROBAR, MAX_PASOS),
    ("04_accion_rechazada", "Necesito reprogramar el pedido 1061 para el 2026-12-01", RECHAZAR, MAX_PASOS),
    ("05_limite_de_pasos", "Consultá los pedidos 1042, 1043 y 1050 y decime cuál se entrega primero", None, 2),
]


def correr(nombre, texto, decision_humana, max_pasos):
    grafo = construir_grafo(max_pasos=max_pasos)
    config = {"configurable": {"thread_id": f"demo-{nombre}-{uuid.uuid4().hex[:6]}"}}
    grafo.invoke(entrada_turno(texto, "cliente_12"), config)
    pausa = aprobacion_pendiente(grafo, config)
    if pausa and decision_humana:
        grafo.invoke(Command(resume=decision_humana), config)
    estado = grafo.get_state(config).values

    md = [f"# {nombre.replace('_', ' ')}", "",
          f"- thread_id: `{config['configurable']['thread_id']}`",
          f"- modelo: `{MODELO}` · máximo de pasos: {max_pasos}", "",
          f"**Usuario:** {texto}", ""]
    if pausa:
        md += ["**Pausa para aprobación humana**", "",
               f"- herramienta: `{pausa['herramienta']}`", f"- parámetros: `{pausa['argumentos']}`",
               f"- decisión: {'APROBADA' if decision_humana['aprobado'] else 'RECHAZADA'} por {decision_humana['revisor']}"
               + (f" — {decision_humana['comentario']}" if decision_humana.get("comentario") else ""), ""]
    md += ["**Traza de pasos**", "", "```", *estado["traza"], "```", "",
           f"**Agente:** {respuesta_final(estado)}", ""]
    return "\n".join(md)


if __name__ == "__main__":
    crear()  # base del cliente con los datos originales
    salida = RAIZ / "docs" / "conversaciones"
    salida.mkdir(parents=True, exist_ok=True)
    for nombre, texto, decision, max_pasos in CONVERSACIONES:
        md = correr(nombre, texto, decision, max_pasos)
        (salida / f"{nombre}.md").write_text(md, encoding="utf-8")
        print(md, "-" * 80, sep="\n")
