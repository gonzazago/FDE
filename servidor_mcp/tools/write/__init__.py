"""Tools de ESCRITURA del servidor: modifican el sistema (read_only_hint=False).
El agente las pausa y pide aprobación humana antes de ejecutarlas."""
from servidor_mcp.tools.write.reprogramar_entrega import reprogramar_entrega

ESCRITURA = [reprogramar_entrega]
