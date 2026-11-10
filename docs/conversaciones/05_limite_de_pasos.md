# 05 limite de pasos

- thread_id: `demo-05_limite_de_pasos-eaa74b`
- decisor: `reglas` · máximo de pasos: 4

**Usuario (cliente_12):** ¿Qué dice la política sobre envíos a la Antártida?

**Traza de pasos**

```
paso 1: decidir -> buscar_documentos {"consulta": "¿Qué dice la política sobre envíos a la Antártida?"} | Pregunta sobre políticas: busco en los documentos.
ejecutar_herramienta -> buscar_documentos: {"consulta": "¿Qué dice la política sobre envíos a la Antártida?", "resultados": []}
paso 2: decidir -> buscar_documentos {"consulta": "¿Qué dice la política sobre envíos a la Antártida? cobertura zona destino"} | Pregunta sobre políticas: busco en los documentos con otros términos.
ejecutar_herramienta -> buscar_documentos: {"consulta": "¿Qué dice la política sobre envíos a la Antártida? cobertura zona destino", "resultados": []}
paso 3: decidir -> buscar_documentos {"consulta": "¿Qué dice la política sobre envíos a la Antártida? condiciones generales"} | Pregunta sobre políticas: busco en los documentos con otros términos.
ejecutar_herramienta -> buscar_documentos: {"consulta": "¿Qué dice la política sobre envíos a la Antártida? condiciones generales", "resultados": []}
paso 4: decidir -> buscar_documentos {"consulta": "¿Qué dice la política sobre envíos a la Antártida? condiciones generales"} | Pregunta sobre políticas: busco en los documentos con otros términos.
ejecutar_herramienta -> buscar_documentos: {"consulta": "¿Qué dice la política sobre envíos a la Antártida? condiciones generales", "resultados": []}
decidir -> LÍMITE de 4 pasos
responder -> fin
```

**Agente:** Llegué al máximo de 4 pasos sin resolver la consulta. Te derivo con una persona del equipo de atención.
