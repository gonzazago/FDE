# 02 consulta politica

- thread_id: `demo-02_consulta_politica-b24190`
- decisor: `reglas` · máximo de pasos: 4

**Usuario (cliente_12):** ¿Cuál es la política de devoluciones?

**Traza de pasos**

```
paso 1: decidir -> buscar_documentos {"consulta": "¿Cuál es la política de devoluciones?"} | Pregunta sobre políticas: busco en los documentos.
ejecutar_herramienta -> buscar_documentos: {"consulta": "¿Cuál es la política de devoluciones?", "resultados": [{"fuente": "devoluciones", "texto": "Los clientes mayoristas pueden dev
paso 2: decidir -> responder {} | Ya tengo lo necesario para responder.
responder -> fin
```

**Agente:** Según la política de devoluciones: Los clientes mayoristas pueden devolver mercadería dentro de los 10 días corridos desde la entrega.
