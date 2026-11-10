#!/usr/bin/env bash
# Prepara el proyecto de cero:
#   1. busca un Python 3.10 o superior instalado en la compu
#   2. crea el entorno virtual .venv con ese Python (si el que hay es viejo, lo rehace)
#   3. instala las dependencias de requirements.txt
#   4. crea la base del sistema del cliente
#
# Uso:  ./setup.sh      (o:  make setup)
set -euo pipefail
cd "$(dirname "$0")"

VERSION_MINIMA=10   # 3.10

es_compatible() {   # devuelve 0 si el Python que recibe es 3.10 o superior
  "$1" -c "import sys; sys.exit(0 if sys.version_info >= (3, $VERSION_MINIMA) else 1)" 2>/dev/null
}

# 1. Buscar Python
PYTHON=""
for candidato in python3.13 python3.12 python3.11 python3.10 \
                 /opt/homebrew/bin/python3.12 /opt/homebrew/bin/python3.13 \
                 /usr/local/bin/python3.12 /usr/local/bin/python3.13 python3 python; do
  if command -v "$candidato" >/dev/null 2>&1 && es_compatible "$candidato"; then
    PYTHON="$(command -v "$candidato")"
    break
  fi
done

if [ -z "$PYTHON" ]; then
  echo "✗ No encontré Python 3.10 o superior."
  echo "  En Mac:  brew install python@3.12   (o bajalo de https://www.python.org/downloads/)"
  echo "  Después cerrá y abrí la terminal, y corré de nuevo: make setup"
  exit 1
fi
echo "✓ Uso $("$PYTHON" --version) ($PYTHON)"

# 2. Entorno virtual
if [ -d .venv ] && ! es_compatible .venv/bin/python; then
  echo "• El .venv existente usa un Python viejo: lo borro y lo creo de nuevo"
  rm -rf .venv
fi
if [ ! -d .venv ]; then
  echo "• Creando entorno virtual en .venv"
  "$PYTHON" -m venv .venv
fi

# 3. Dependencias
echo "• Instalando dependencias (puede tardar un par de minutos la primera vez)"
.venv/bin/python -m pip install --quiet --upgrade pip
.venv/bin/python -m pip install --quiet -r requirements.txt

# 4. Base del cliente
.venv/bin/python sistema_cliente/seed.py

echo ""
echo "✓ Listo. Probá:  make demo   ·   make chat   ·   make help"
