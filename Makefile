# Atajos del proyecto. No hace falta activar el entorno virtual.
# Uso:  make <comando>     ·     make help  muestra la lista

PY := .venv/bin/python
# marca: se rehace cuando cambia requirements.txt
DEPS := .venv/.dependencias

.DEFAULT_GOAL := help
.PHONY: help setup ui demo mcp grafo seed reset clean

help: ## Muestra esta ayuda
	@echo "Comandos disponibles:"
	@grep -E '^[a-z]+:.*## ' $(MAKEFILE_LIST) | awk -F':.*## ' '{printf "  make %-6s %s\n", $$1, $$2}'

setup: ## Prepara todo: entorno, dependencias y base del cliente (una sola vez)
	@bash setup.sh

$(PY):
	@echo "Falta preparar el proyecto. Corriendo make setup..."
	@bash setup.sh

$(DEPS): requirements.txt | $(PY)
	@echo "requirements.txt cambió: instalando dependencias..."
	@$(PY) -m pip install --quiet -r requirements.txt
	@touch $(DEPS)

ui: $(DEPS) ## Abre la UI web: chat + eventos en vivo + grafo (http://localhost:8000)
	@$(PY) ui/server.py

demo: $(DEPS) ## Corre las 5 conversaciones de ejemplo (docs/conversaciones/)
	@$(PY) run_demo.py

mcp: $(DEPS) ## Prueba el servidor MCP: lista herramientas y llama a una
	@$(PY) servidor_mcp/probar_cliente.py

grafo: $(DEPS) ## Exporta el diagrama del grafo a docs/grafo.mmd
	@$(PY) exportar_grafo.py

seed: $(DEPS) ## Recrea la base del cliente con los datos originales
	@$(PY) sistema_cliente/seed.py

reset: $(DEPS) ## Borra la memoria del agente y recrea la base
	@rm -f data/checkpoints.db*
	@$(PY) sistema_cliente/seed.py

clean: ## Borra el entorno virtual y los archivos generados
	@rm -rf .venv data/*.db*
	@find . -name __pycache__ -type d -prune -exec rm -rf {} +
	@echo "Limpio. Para volver a empezar: make setup"
