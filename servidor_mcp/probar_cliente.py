"""Script cliente que prueba el servidor MCP: lista las herramientas y llama a una.

Uso:  make mcp   (o: python servidor_mcp/probar_cliente.py)
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from agente.tools.mcp_cliente import herramientas_mcp  # noqa: E402

if __name__ == "__main__":
    lecturas = {t.name for t in herramientas_mcp(solo_lectura=True)}
    tools = {t.name: t for t in herramientas_mcp()}
    print("Herramientas expuestas por el servidor:\n")
    for t in tools.values():
        tipo = "lectura" if t.name in lecturas else "ESCRITURA (requiere aprobación)"
        print(f"- {t.name}({', '.join(t.args)})  [{tipo}]")
        print(f"    {t.description.splitlines()[0]}")
    print("\nLlamada de prueba: consultar_pedido(pedido_id=1042)")
    print(json.dumps(tools["consultar_pedido"].invoke({"pedido_id": 1042}), indent=2, ensure_ascii=False))
