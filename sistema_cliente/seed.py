"""Crea el "sistema del cliente" simulado: una base SQLite con datos ficticios.

Caso: Distribuidora Los Andes (ficticia), soporte de pedidos mayoristas.
En la Pre-Entrega 5 esta base se reemplaza por el sistema legacy real,
sin cambiar el contrato del servidor MCP.

Uso:  python sistema_cliente/seed.py
"""
import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from config import DB_CLIENTE  # noqa: E402

CLIENTES = [
    (12, "Almacén Don Pepe", "Mendoza"),
    (27, "Kiosco La Esquina", "San Juan"),
    (31, "Supermercado Andino", "San Luis"),
]

PEDIDOS = [
    # id, cliente_id, estado, fecha_entrega, total
    (1042, 12, "en preparación", "2026-11-10", 185400.0),
    (1043, 12, "despachado", "2026-11-06", 92300.0),
    (1050, 27, "entregado", "2026-10-28", 40150.0),
    (1061, 31, "pendiente de pago", "2026-11-15", 512000.0),
]


def crear(db_path: Path = DB_CLIENTE) -> Path:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    if db_path.exists():
        db_path.unlink()
    con = sqlite3.connect(db_path)
    con.executescript(
        """
        CREATE TABLE clientes (id INTEGER PRIMARY KEY, nombre TEXT, provincia TEXT);
        CREATE TABLE pedidos (
            id INTEGER PRIMARY KEY, cliente_id INTEGER REFERENCES clientes(id),
            estado TEXT, fecha_entrega TEXT, total REAL);
        CREATE TABLE auditoria (
            id INTEGER PRIMARY KEY AUTOINCREMENT, pedido_id INTEGER,
            accion TEXT, detalle TEXT, creado TEXT DEFAULT CURRENT_TIMESTAMP);
        """
    )
    con.executemany("INSERT INTO clientes VALUES (?,?,?)", CLIENTES)
    con.executemany("INSERT INTO pedidos VALUES (?,?,?,?,?)", PEDIDOS)
    con.commit()
    con.close()
    return db_path


if __name__ == "__main__":
    print(f"Base creada en {crear()}")
