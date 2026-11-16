# rag/ — la búsqueda de documentos

El RAG de la Pre-Entrega 3 (versión simplificada), con la misma estructura que `agente/` y
`servidor_mcp/`. Es independiente del agente: el agente solo ve la tool.

```
rag/
├── __init__.py
├── buscador.py       La búsqueda sobre docs/politicas/ (reemplazala por tu RAG real)
├── model/            Modelos pydantic: ConsultaDocumentos, Fragmento, ResultadoBusqueda
└── tools/
    └── read/         buscar_documentos (@tool): el RAG solo lee, no tiene write/
```

`agente/tools/read/` junta `buscar_documentos` con las tools de lectura del servidor MCP.

**Para usar tu RAG real:** cambiá la función `buscar` de `buscador.py` y devolvé un
`ResultadoBusqueda`. La tool, el grafo y la UI no cambian.
