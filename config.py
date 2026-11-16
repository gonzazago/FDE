"""Configuración del proyecto. Los valores se pueden cambiar en el archivo .env."""
import os
from pathlib import Path

RAIZ = Path(__file__).resolve().parent

# Carga .env (formato CLAVE=valor) sin dependencias extra
_env = RAIZ / ".env"
if _env.exists():
    for linea in _env.read_text(encoding="utf-8").splitlines():
        linea = linea.strip()
        if linea and not linea.startswith("#") and "=" in linea:
            clave, valor = linea.split("=", 1)
            os.environ.setdefault(clave.strip(), valor.strip().strip('"').strip("'"))

DATA = RAIZ / "data"
DB_CLIENTE = DATA / "distribuidora.db"          # sistema del cliente simulado
DB_CHECKPOINTS = DATA / "checkpoints.db"        # memoria del agente (thread_id)
DOCS_POLITICAS = RAIZ / "docs" / "politicas"    # documentos del RAG
SERVIDOR_MCP = RAIZ / "servidor_mcp" / "server.py"

MODELO = os.getenv("MODELO", "claude-sonnet-5-5")
MAX_PASOS = int(os.getenv("MAX_PASOS", "4"))    # tope del bucle decidir -> ejecutar
