"""El motor: el modelo de Claude con las tools enlazadas (bind_tools)."""
from functools import lru_cache

from langchain.chat_models import init_chat_model
from langchain_core.messages import AIMessage, SystemMessage

from config import MODELO
from agente.tools import TODAS

SISTEMA = """Sos el agente de soporte de pedidos de la Distribuidora Los Andes.
Respondé en español rioplatense, breve y concreto.
- Usá buscar_documentos para preguntas sobre políticas y las herramientas del sistema para datos de pedidos.
- Antes de modificar un pedido, consultalo.
- No inventes números de pedido, fechas ni datos que el usuario no dio: si falta algo, pedíselo.
- Las herramientas que modifican el sistema pasan por aprobación humana: igual usalas cuando corresponda.
- Si una acción fue rechazada, no la reintentes: contale al usuario que no se hizo y por qué."""


@lru_cache(maxsize=1)
def tools() -> list:
    return TODAS


@lru_cache(maxsize=1)
def tools_por_nombre() -> dict:
    return {t.name: t for t in tools()}


@lru_cache(maxsize=1)
def modelo_con_tools():
    modelo = init_chat_model(MODELO)  # "claude-..." -> ChatAnthropic, toma ANTHROPIC_API_KEY
    return modelo.bind_tools(tools())


def decidir(mensajes: list) -> AIMessage:
    """El modelo ve la conversación y responde con texto o pide tools (tool_calls)."""
    return modelo_con_tools().invoke([SystemMessage(SISTEMA), *mensajes])


def cerrar_por_limite(mensajes: list, max_pasos: int) -> AIMessage:
    """Respuesta final cuando se agotan los pasos: sin pedir más tools."""
    aviso = (f"\nSe alcanzó el máximo de {max_pasos} pasos. No llames más herramientas: "
             "resumí lo que averiguaste, avisá que no se pudo terminar y ofrecé derivar a una persona.")
    msg = modelo_con_tools().invoke([SystemMessage(SISTEMA + aviso), *mensajes])
    # Se descartan los tool_calls que pudiera traer: así el historial queda válido
    return AIMessage(content=msg.text or "Llegué al máximo de pasos sin terminar. Te derivo con una persona.")
