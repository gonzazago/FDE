"""Exporta el diagrama del grafo en Mermaid a docs/grafo.mmd (no llama al LLM)."""
from langgraph.checkpoint.memory import InMemorySaver

from agente.grafo import construir_grafo
from config import RAIZ

mermaid = construir_grafo(checkpointer=InMemorySaver()).get_graph().draw_mermaid()
(RAIZ / "docs" / "grafo.mmd").write_text(mermaid, encoding="utf-8")
print(mermaid)
