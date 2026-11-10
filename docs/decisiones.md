# Decisiones y trade-offs

## ¿Por qué un agente y no un flujo fijo?

Las consultas de soporte llegan en lenguaje natural y piden cosas distintas. A veces es un
pedido puntual, a veces una política y a veces un cambio sobre el sistema. Además, el orden
de los pasos depende de lo que se va encontrando: antes de reprogramar hay que consultar el
pedido, y si una búsqueda no trae resultados conviene reformularla. Un flujo fijo obligaría
a escribir una rama por cada combinación. El agente decide el próximo paso en función del
estado, dentro de un grafo que limita qué puede hacer.

## ¿Qué acciones exigen aprobación y por qué?

Toda herramienta MCP que **no** esté marcada como `read_only_hint=True`. En este caso es
`reprogramar_entrega`, que modifica la fecha y genera un compromiso logístico con el cliente.
Un error ahí tiene costo real: camiones, personal del depósito o un cliente sin mercadería.
Las consultas (`consultar_pedido`, `listar_pedidos_cliente`, `buscar_documentos`) no cambian
nada y corren sin pausa. La regla vive en las anotaciones del servidor y no en el grafo, así
que una herramienta de escritura nueva queda protegida por defecto.

## ¿Cómo elegimos el límite de pasos?

Una consulta típica se resuelve en 2 o 3 decisiones: consultar, (aprobar y) ejecutar, y
responder. Elegimos `MAX_PASOS = 4` para dejar una reformulación de búsqueda de margen sin
permitir bucles largos. Cada paso del decisor con LLM es una llamada al modelo, así que el
límite también acota el costo y la latencia por consulta. Al llegar al máximo, el agente no
falla: responde que no pudo resolverlo y deriva a una persona. El valor se puede cambiar con
la variable de entorno `MAX_PASOS`.

## Otros trade-offs

- **Una sesión MCP por llamada.** Es más simple y robusto, aunque agrega latencia de arranque.
  En producción usaríamos una sesión persistente o un transporte HTTP.
- **Estado con referencias.** Guardamos los resultados de las herramientas de este turno, no
  documentos completos. `resultados` y `traza` se reinician en cada turno.
- **Decisor de reglas.** Permite testear el grafo sin depender del modelo, aunque no
  generaliza. El caso real usa `DecisorLLM`.
