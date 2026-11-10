# 01 consulta pedido

- thread_id: `demo-01_consulta_pedido-403822`
- decisor: `reglas` · máximo de pasos: 4

**Usuario (cliente_12):** ¿En qué estado está el pedido 1042?

**Traza de pasos**

```
paso 1: decidir -> consultar_pedido {"pedido_id": 1042} | El usuario menciona un pedido: primero consulto su estado.
ejecutar_herramienta -> consultar_pedido: {"encontrado": true, "id": 1042, "estado": "en preparación", "fecha_entrega": "2026-11-10", "total": 185400.0, "cliente_id": 12, "cliente": 
paso 2: decidir -> responder {} | Ya tengo lo necesario para responder.
responder -> fin
```

**Agente:** El pedido 1042 (Almacén Don Pepe) está en preparación, con entrega prevista el 2026-11-10.
