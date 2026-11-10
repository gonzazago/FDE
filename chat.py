"""Chat por consola con el agente supervisado.

  python chat.py                         # thread nuevo
  python chat.py --thread soporte-ana    # retoma (o crea) un thread con ese id

Si cerrás el programa mientras una acción espera aprobación, al volver con el
mismo --thread el agente te vuelve a mostrar la aprobación pendiente: el estado
quedó guardado en data/checkpoints.db (SqliteSaver).
"""
import argparse
import uuid

from langgraph.types import Command

from agente.estado import entrada_turno
from agente.grafo import aprobacion_pendiente, construir_grafo, respuesta_final
from config import DECISOR, MAX_PASOS


def pedir_decision(pendiente: dict) -> dict:
    print("\n⏸  El agente quiere ejecutar una acción que MODIFICA el sistema:")
    print(f"   herramienta: {pendiente['herramienta']}")
    for k, v in pendiente["argumentos"].items():
        print(f"   {k}: {v}")
    print(f"   motivo del agente: {pendiente['razon']}")
    while True:
        r = input("¿Aprobás? [s/n] (o 'salir' para dejarlo pendiente): ").strip().lower()
        if r in ("s", "n", "salir"):
            break
    if r == "salir":
        raise SystemExit("Queda pendiente. Retomá con el mismo --thread.")
    comentario = "" if r == "s" else input("Comentario para el usuario (opcional): ").strip()
    return {"aprobado": r == "s", "revisor": "consola", "comentario": comentario}


def resolver_pendientes(grafo, config):
    while (pendiente := aprobacion_pendiente(grafo, config)):
        grafo.invoke(Command(resume=pedir_decision(pendiente)), config)
    print(f"\n🤖 {respuesta_final(grafo, config)}\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--thread", default=f"chat-{uuid.uuid4().hex[:8]}")
    ap.add_argument("--usuario", default="cliente_12")
    args = ap.parse_args()
    config = {"configurable": {"thread_id": args.thread}}
    grafo = construir_grafo()
    print(f"thread_id: {args.thread} · decisor: {DECISOR} · máximo de pasos: {MAX_PASOS}  (Ctrl+C para salir)")

    if aprobacion_pendiente(grafo, config):
        print("Este thread tenía una aprobación pendiente.")
        resolver_pendientes(grafo, config)

    while True:
        try:
            texto = input("vos > ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not texto:
            continue
        grafo.invoke(entrada_turno(texto, args.usuario), config)
        resolver_pendientes(grafo, config)


if __name__ == "__main__":
    main()
