# data/ — bases generadas

Acá el proyecto guarda sus bases SQLite. No se suben al repo (están en `.gitignore`).

- `distribuidora.db`: el sistema del cliente simulado (lo crea `make setup` o `make seed`).
- `checkpoints.db`: la memoria del agente, una conversación por `thread_id` (`make reset` la borra).
