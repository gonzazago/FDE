# Atajos para correr el proyecto sin activar el entorno virtual.
# Uso:  make <comando>     ·     make help  muestra la lista

PY     := .venv/bin/python

# Si existe .env (ej. ANTHROPIC_API_KEY=...), se carga y se pasa a los comandos
ifneq (,$(wildcard .env))
include .env
export
endif
THREAD ?= chat-$(shell date +%s)

.DEFAULT_GOAL := help
.PHONY: help setup seed mcp demo chat grafo test reset clean

help: ## Muestra esta ayuda
	@echo "Comandos disponibles:"
	@grep -E '^[a-z]+:.*## ' $(MAKEFILE_LIST) | awk -F':.*## ' '{printf "  make %-7s %s\n", $$1, $$2}'
	@echo ""
	@echo "Ejemplo con thread propio:  make chat THREAD=mi-prueba"

setup: ## Crea el entorno, instala dependencias y la base (una sola vez)
	@bash setup.sh

$(PY):
	@echo "Falta preparar el proyecto. Corriendo make setup..."
	@bash setup.sh

seed: $(PY) ## Recrea la base del cliente con los datos originales
	@$(PY) sistema_cliente/seed.py

mcp: $(PY) ## Prueba el servidor MCP: lista herramientas y llama a una
	@$(PY) servidor_mcp/probar_cliente.py

demo: $(PY) ## Corre las 5 conversaciones de ejemplo (docs/conversaciones/)
	@$(PY) run_demo.py

chat: $(PY) ## Chat con el agente (THREAD=nombre para retomar una conversación)
	@$(PY) chat.py --thread $(THREAD)

grafo: $(PY) ## Exporta el diagrama del grafo a docs/grafo.mmd
	@$(PY) exportar_grafo.py

test: $(PY) ## Corre los tests
	@$(PY) -m pytest -q

reset: $(PY) ## Borra las conversaciones guardadas y recrea la base
	@rm -f data/checkpoints.db
	@$(PY) sistema_cliente/seed.py

clean: ## Borra el entorno virtual y los archivos generados
	@rm -rf .venv .pytest_cache data/*.db
	@find . -name __pycache__ -type d -prune -exec rm -rf {} +
	@echo "Limpio. Para volver a empezar: make setup"