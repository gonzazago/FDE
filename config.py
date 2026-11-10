"""Configuración central del proyecto (se puede sobreescribir con variables de entorno)."""
import os
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
DATA = RAIZ / "data"
DB_CLIENTE = Path(os.getenv("DB_CLIENTE", DATA / "distribuidora.db"))
DB_CHECKPOINTS = Path(os.getenv("DB_CHECKPOINTS", DATA / "checkpoints.db"))
DOCS_POLITICAS = RAIZ / "docs" / "politicas"
SERVIDOR_MCP = RAIZ / "servidor_mcp" / "server.py"

# Límite del bucle decidir -> ejecutar. Ver docs/decisiones.md
MAX_PASOS = int(os.getenv("MAX_PASOS", "4"))

# "llm" usa Claude vía langchain-anthropic; "reglas" es un decisor determinístico
# para correr el proyecto sin API key (demos, tests, CI).
DECISOR = os.getenv("DECISOR", "llm" if os.getenv("ANTHROPIC_API_KEY") else "reglas")
MODELO = os.getenv("MODELO", "claude-sonnet-5-5")
