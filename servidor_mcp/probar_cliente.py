"""Script cliente que prueba el servidor MCP: lista las herramientas y llama a una.

Uso:  python servidor_mcp/probar_cliente.py
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from agente.mcp_cliente import listar_herramientas, llamar_herramienta  # noqa: E402

if __name__ == "__main__":
    print("Herramientas expuestas por el servidor:\n")
    for h in listar_herramientas():
        tipo = "lectura" if h.solo_lectura else "ESCRITURA (requiere aprobación)"
        params = ", ".join(h.esquema.get("properties", {}).keys())
        print(f"- {h.nombre}({params})  [{tipo}]")
        print(f"    {h.descripcion.splitlines()[0]}")
    print("\nLlamada de prueba: consultar_pedido(pedido_id=1042)")
    print(json.dumps(llamar_herramienta("consultar_pedido", {"pedido_id": 1042}), indent=2, ensure_ascii=False))
