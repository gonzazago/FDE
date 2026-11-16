# agente/ — el cerebro

Todo lo que el agente es y puede hacer.

```
agente/
├── llm.py        El motor: Claude con las tools enlazadas (bind_tools) y el prompt de sistema
├── grafo.py      El grafo de LangGraph: nodos, aristas, aprobación humana y memoria
├── models/       Modelos pydantic: estado, aprobaciones, resultados de las tools
└── tools/        Las tools, separadas en lectura y escritura
```

| Archivo | Qué hace |
|---|---|
| `llm.py` | Crea el modelo con `init_chat_model` y le enlaza las tools con `bind_tools`. Claude ve la conversación y responde con texto o pide tools (`tool_calls`). |
| `grafo.py` | Define los nodos `decidir`, `pedir_aprobacion` y `responder`, y **un nodo por cada tool** (se crean solos desde `tools/`). También el límite de pasos y la memoria (`SqliteSaver`). |

## El grafo

```
inicio → decidir ─┬→ <tool de lectura> ──────────────→ decidir  (bucle)
                  ├→ pedir_aprobacion → <tool de escritura> → decidir
                  └→ responder → fin
```

`decidir` llama al modelo. Si pide una tool de lectura, va directo al nodo de esa tool. Si
pide una de escritura, pasa antes por `pedir_aprobacion`, que pausa con `interrupt` hasta que
una persona responda. Cada nodo de tool ejecuta sus llamadas y devuelve un `ToolMessage`; si
la persona rechazó, devuelve el rechazo en lugar de ejecutar. Si el modelo pide varias tools
distintas a la vez, sus nodos corren en paralelo.
