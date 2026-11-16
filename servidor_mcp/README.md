# servidor_mcp/ — el servidor MCP propio

Expone el sistema del cliente **y el RAG** como herramientas que cualquier agente MCP puede usar.
Tiene la misma estructura que `agente/`.

```
servidor_mcp/
├── __init__.py
├── server.py            Arma el servidor: publica las tools de read/ y write/ y el resource
├── db.py                Acceso a la base SQLite del cliente
├── buscador.py          El RAG: búsqueda sobre docs/politicas/ (reemplazala por tu RAG real)
├── probar_cliente.py    Script que lista las tools y llama a una (make mcp)
├── model/               Modelos pydantic: Pedido, ResultadoBusqueda, ResultadoReprogramacion…
└── tools/
    ├── read/            buscar_documentos (RAG), consultar_pedido, listar_pedidos_cliente
    └── write/           reprogramar_entrega                        (escritura)
```

Cada tool es un archivo con una función tipada: sus parámetros (`Annotated[..., Field(...)]`) y
su docstring pasan a ser el contrato que ve el modelo. `server.py` las publica con la anotación
`read_only_hint` según la carpeta; el agente pide aprobación humana para toda tool que no sea
de solo lectura.

**Para sumar una tool:** creá su archivo en `tools/read/` o `tools/write/` y agregala a la lista
del `__init__.py` de esa carpeta.

El agente lanza este servidor por **stdio**, no hace falta levantarlo a mano.

**Para usar tu RAG real:** cambiá la función `buscar` de `buscador.py` y devolvé un `ResultadoBusqueda`. La tool, el agente y la UI no cambian.
