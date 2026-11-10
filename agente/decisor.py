"""Cerebro del agente: elige la próxima acción y redacta la respuesta final.

Dos implementaciones con la misma interfaz:
  - DecisorLLM:    Claude con salida estructurada (Pydantic). Es el que se usa en el caso real.
  - DecisorReglas: determinístico, sin API key. Sirve para demos, tests y para que el
                   grafo se pueda probar aislado del modelo.
"""
import json
import re

from langchain_core.exceptions import OutputParserException
from langchain_core.messages import HumanMessage

from pydantic import BaseModel, Field, ValidationError

from agente.estado import Decision, EstadoAgente
from agente.mcp_cliente import listar_herramientas
from config import MAX_PASOS, MODELO

RE_PEDIDO = re.compile(r"pedido\s*(?:n[°º.]?\s*)?#?(\d{3,6})", re.I)
RE_CLIENTE = re.compile(r"cliente\s*(?:n[°º.]?\s*)?#?(\d{1,6})", re.I)
RE_FECHA = re.compile(r"(\d{4}-\d{2}-\d{2})")
PALABRAS_REPROGRAMAR = ("reprogram", "cambiar la fecha", "cambiá la fecha", "mover la entrega", "posterg", "pospon")
PALABRAS_POLITICA = ("política", "politica", "devol", "puedo", "plazo", "envío", "envio", "pago", "condicion")
REFORMULACIONES = ["", " cobertura zona destino", " condiciones generales"]


def ultimo_mensaje_usuario(estado: EstadoAgente) -> str:
    for m in reversed(estado["mensajes"]):
        if isinstance(m, HumanMessage):
            return m.content
    return ""


def _usadas(estado, nombre):
    return [r for r in estado["resultados"] if r["herramienta"] == nombre]


# --------------------------------------------------------------------------------------
class DecisorReglas:
    def decidir(self, estado: EstadoAgente) -> Decision:
        texto = ultimo_mensaje_usuario(estado)
        bajo = texto.lower()
        pedido = RE_PEDIDO.search(texto)
        cliente = RE_CLIENTE.search(texto)
        fecha = RE_FECHA.search(texto)
        reprogramar = any(p in bajo for p in PALABRAS_REPROGRAMAR)
        politica = any(p in bajo for p in PALABRAS_POLITICA) and not reprogramar

        if politica:
            busquedas = _usadas(estado, "buscar_documentos")
            if not any(b["salida"]["resultados"] for b in busquedas):
                extra = REFORMULACIONES[min(len(busquedas), len(REFORMULACIONES) - 1)]
                return Decision(accion="buscar_documentos", argumentos={"consulta": texto + extra},
                                razon="Pregunta sobre políticas: busco en los documentos"
                                      + (" con otros términos" if busquedas else "") + ".")
        if pedido and not _usadas(estado, "consultar_pedido"):
            return Decision(accion="usar_herramienta", herramienta="consultar_pedido",
                            argumentos={"pedido_id": int(pedido.group(1))},
                            razon="El usuario menciona un pedido: primero consulto su estado.")
        if cliente and not _usadas(estado, "listar_pedidos_cliente"):
            return Decision(accion="usar_herramienta", herramienta="listar_pedidos_cliente",
                            argumentos={"cliente_id": int(cliente.group(1))},
                            razon="El usuario pide los pedidos de un cliente.")
        if reprogramar and pedido and fecha and not _usadas(estado, "reprogramar_entrega"):
            motivo = texto.split("porque", 1)[1].strip(" .") if "porque" in bajo else "Pedido del cliente por chat"
            return Decision(accion="usar_herramienta", herramienta="reprogramar_entrega",
                            argumentos={"pedido_id": int(pedido.group(1)), "nueva_fecha": fecha.group(1),
                                        "motivo": motivo[:200]},
                            razon="El usuario pide cambiar la fecha de entrega: es una escritura.")
        return Decision(accion="responder", razon="Ya tengo lo necesario para responder.")

    def responder(self, estado: EstadoAgente, limite: bool) -> str:
        partes = []
        escribio = any(r["herramienta"] == "reprogramar_entrega" and r["salida"].get("ok")
                       for r in estado["resultados"])
        for r in estado["resultados"]:
            h, a, s = r["herramienta"], r["argumentos"], r["salida"]
            if s.get("rechazado"):
                partes.append(f"No ejecuté {h} sobre el pedido {a.get('pedido_id')}: la acción fue rechazada"
                              f" por {s.get('revisor', 'el revisor')}"
                              + (f" ({s['comentario']})." if s.get("comentario") else "."))
            elif "error" in s and s.get("ok") is not True:
                partes.append(f"No pude completar {h}: {s['error']}")
            elif h == "consultar_pedido" and escribio:
                continue  # si ya se modificó el pedido, alcanza con contar el cambio
            elif h == "consultar_pedido":
                partes.append(f"El pedido {s['id']} ({s['cliente']}) está {s['estado']}, con entrega "
                              f"prevista el {s['fecha_entrega']}." if s.get("encontrado")
                              else f"No encontré el pedido {a['pedido_id']}.")
            elif h == "listar_pedidos_cliente":
                items = "; ".join(f"{p['id']} ({p['estado']}, {p['fecha_entrega']})" for p in s["pedidos"])
                partes.append(f"Pedidos del cliente {s['cliente_id']}: {items or 'ninguno'}.")
            elif h == "reprogramar_entrega":
                partes.append(f"Listo: reprogramé la entrega del pedido {s['pedido_id']} del "
                              f"{s['fecha_anterior']} al {s['fecha_nueva']}." if s.get("ok")
                              else f"No pude reprogramar: {s.get('error')}")
            elif h == "buscar_documentos" and s["resultados"]:
                top = s["resultados"][0]
                partes.append(f"Según la política de {top['fuente']}: {top['texto']}")
        if limite:
            partes.append(f"Llegué al máximo de {MAX_PASOS} pasos sin resolver la consulta. "
                          "Te derivo con una persona del equipo de atención.")
        if not partes:
            partes.append("No encontré información para responder eso.")
        return " ".join(dict.fromkeys(partes))


# --------------------------------------------------------------------------------------
PROMPT_SISTEMA = """Sos el agente de soporte de pedidos de la Distribuidora Los Andes.
En cada paso elegís UNA acción:
- buscar_documentos: para preguntas sobre políticas (argumentos: {{"consulta": str}}).
- usar_herramienta: para consultar o modificar el sistema (herramienta = nombre exacto).
- responder: cuando ya tenés lo necesario, o si falta un dato que solo el usuario puede dar.

Herramientas MCP disponibles:
{herramientas}

Reglas:
- Antes de modificar un pedido, consultalo.
- No inventes números de pedido, fechas ni argumentos que el usuario no dio.
- Si una búsqueda no trae resultados, podés reformular una vez; si sigue sin resultados, respondé.
- Las herramientas de ESCRITURA pasan por aprobación humana: igual elegilas cuando correspondan.
Llevás {pasos} de {max_pasos} pasos."""


class DecisionLLM(BaseModel):
    """Esquema que ve el modelo. Los argumentos van como JSON en texto porque las
    salidas estructuradas estrictas no admiten objetos de claves libres."""

    accion: str = Field(description="buscar_documentos | usar_herramienta | responder")
    herramienta: str | None = Field(None, description="Nombre exacto de la herramienta MCP, o null")
    argumentos_json: str = Field("{}", description='Argumentos como objeto JSON, ej. {"pedido_id": 1042}')
    razon: str = Field(description="Por qué se eligió esta acción, en una oración")


class DecisorLLM:
    def __init__(self, modelo: str = MODELO):
        from langchain_anthropic import ChatAnthropic

        self.llm = ChatAnthropic(model=modelo, temperature=0, max_tokens=1024)
        self.estructurado = self.llm.with_structured_output(DecisionLLM, method="json_schema")

    def _contexto(self, estado: EstadoAgente) -> str:
        return json.dumps({"usuario": estado["usuario"], "consulta": ultimo_mensaje_usuario(estado),
                           "resultados_de_este_turno": estado["resultados"]}, ensure_ascii=False, default=str)

    def decidir(self, estado: EstadoAgente) -> Decision:
        herramientas = "\n".join(
            f"- {h.nombre} [{'lectura' if h.solo_lectura else 'ESCRITURA'}]: {h.descripcion} "
            f"Parámetros: {json.dumps(h.esquema.get('properties', {}), ensure_ascii=False)}"
            for h in listar_herramientas())
        sistema = PROMPT_SISTEMA.format(herramientas=herramientas, pasos=estado["pasos"], max_pasos=MAX_PASOS)
        try:
            crudo = self.estructurado.invoke([("system", sistema), ("human", self._contexto(estado))])
            # segunda validación: el esquema "real" del grafo (Literal de acciones, dict de argumentos)
            d = Decision(accion=crudo.accion, herramienta=crudo.herramienta,
                         argumentos=json.loads(crudo.argumentos_json or "{}"), razon=crudo.razon)
        except (ValidationError, ValueError, OutputParserException) as e:  # salida fuera de esquema -> no rompemos el grafo
            return Decision(accion="responder", razon=f"Decisión inválida del modelo: {e.__class__.__name__}")
        nombres = {h.nombre for h in listar_herramientas()}
        if d.accion == "usar_herramienta" and d.herramienta not in nombres:
            return Decision(accion="responder", razon=f"El modelo pidió una herramienta inexistente: {d.herramienta}")
        return d

    def responder(self, estado: EstadoAgente, limite: bool) -> str:
        instruccion = ("Redactá la respuesta final al usuario en español rioplatense, breve y concreta. "
                       "Contá qué se hizo o por qué no se hizo. Usá solo los resultados dados.")
        if limite:
            instruccion += f" Se alcanzó el máximo de {MAX_PASOS} pasos: avisalo y ofrecé derivar a una persona."
        return self.llm.invoke([("system", instruccion), ("human", self._contexto(estado))]).content


def crear_decisor(tipo: str):
    return DecisorLLM() if tipo == "llm" else DecisorReglas()
