"""Exporta el diagrama del grafo en Mermaid a docs/grafo.mmd (y lo imprime)."""
from langgraph.checkpoint.memory import InMemorySaver

from agente.decisor import DecisorReglas
from agente.grafo import construir_grafo
from config import RAIZ

if __name__ == "__main__":
    grafo = construir_grafo(decisor=DecisorReglas(), checkpointer=InMemorySaver())
    mermaid = grafo.get_graph().draw_mermaid()
    (RAIZ / "docs" / "grafo.mmd").write_text(mermaid, encoding="utf-8")
    print(mermaid)
