# agente/model/ — la forma de los datos

Modelos pydantic: validan lo que entra y sale del grafo y documentan cada campo.

| Archivo | Qué define |
|---|---|
| `estado.py` | **`EstadoAgente`**: lo que viaja de nodo en nodo (`mensajes`, `usuario`, `pasos`, `pendiente_aprobacion`, `aprobaciones`, `limite`, `traza`). `entrada_turno()` arma el input de un turno nuevo. |
| `aprobacion.py` | **`SolicitudAprobacion`** (lo que se le muestra a la persona al pausar) y **`DecisionAprobacion`** (lo que ella responde: `aprobado`, `revisor`, `comentario`). |
| `herramientas.py` | Lo que ve el modelo si una tool se rechaza (`Rechazo`) o falla (`ErrorHerramienta`). Los modelos de los datos (pedidos, búsqueda) viven en `servidor_mcp/model/`. |

`mensajes` usa el reducer `add_messages` y `traza` uno propio: así cada nodo solo agrega lo
suyo y varias tools en paralelo no se pisan.
