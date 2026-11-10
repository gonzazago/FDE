# 03 accion aprobada

- thread_id: `demo-03_accion_aprobada-fd97e3`
- decisor: `reglas` · máximo de pasos: 4

**Usuario (cliente_12):** Reprogramá la entrega del pedido 1042 para el 2026-11-20 porque no hay nadie en el local esa semana

**Pausa para aprobación humana**

- herramienta: `reprogramar_entrega`
- parámetros: `{'pedido_id': 1042, 'nueva_fecha': '2026-11-20', 'motivo': 'no hay nadie en el local esa semana'}`
- decisión: APROBADA por ana.supervisora

**Traza de pasos**

```
paso 1: decidir -> consultar_pedido {"pedido_id": 1042} | El usuario menciona un pedido: primero consulto su estado.
ejecutar_herramienta -> consultar_pedido: {"encontrado": true, "id": 1042, "estado": "en preparación", "fecha_entrega": "2026-11-10", "total": 185400.0, "cliente_id": 12, "cliente": 
paso 2: decidir -> reprogramar_entrega {"pedido_id": 1042, "nueva_fecha": "2026-11-20", "motivo": "no hay nadie en el local esa semana"} | El usuario pide cambiar la fecha de entrega: es una escritura.
pedir_aprobacion -> APROBADA por ana.supervisora
ejecutar_herramienta -> reprogramar_entrega: {"ok": true, "pedido_id": 1042, "fecha_anterior": "2026-11-10", "fecha_nueva": "2026-11-20"}
paso 3: decidir -> responder {} | Ya tengo lo necesario para responder.
responder -> fin
```

**Agente:** Listo: reprogramé la entrega del pedido 1042 del 2026-11-10 al 2026-11-20.
