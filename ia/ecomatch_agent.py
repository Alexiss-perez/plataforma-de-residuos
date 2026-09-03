"""
Agente EcoMatch — Script principal
===================================
Conecta el System Prompt + Tools + GLM 5.2 (Kostra / OpenAI-compatible) en un loop de conversación.

Uso:
    python ecomatch_agent.py            # modo interactivo (chat por terminal)
    python ecomatch_agent.py --test     # ejecuta casos de prueba automáticos

Requiere:
    pip install openai
    export KOSTRA_API_KEY="tu-api-key"
"""
import os
import sys
import json
import logging
from pathlib import Path
from datetime import datetime

from openai import OpenAI

# ── Cargar System Prompt desde archivo ──────────────────────────────────────
PROMPT_DIR = Path(__file__).parent / "prompts"
SYSTEM_PROMPT = (PROMPT_DIR / "system_prompt.md").read_text(encoding="utf-8")

WELCOME_MSG = (
    "👋 ¡Hola! Soy **EcoMatch**, tu agente de economía circular. ♻️\n\n"
    "Puedo ayudarte a:\n"
    "1. **Publicar residuos** que quieres que retiren de tu ubicación\n"
    "2. **Buscar receptores** cerca de ti (ONGs, plantas de reciclaje, pymes)\n"
    "3. **Coordinar el retiro** entre tú y el receptor\n\n"
    "Cuéntame: ¿qué residuo tienes y dónde estás ubicado?"
)

# ── Importar tools y guardrail ──────────────────────────────────────────────
sys.path.insert(0, str(Path(__file__).parent))
from tools import TOOLS_SCHEMA, ejecutar_tool
from guardrail import validar_respuesta

# ── Logging ─────────────────────────────────────────────────────────────────
LOG_DIR = Path(__file__).parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_DIR / "agent.log", encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger("ecomatch")

# ── Configuración del cliente (Kostra — OpenAI-compatible) ──────────────────
client = OpenAI(
    base_url="https://ai.kostra.cloud/v1",
    api_key=os.environ.get("KOSTRA_API_KEY", ""),
)

MODEL = "glm-5.2"  # GLM 5.2 — modelo asignado al agente
MAX_TOOL_ROUNDS = 5  # máximo de rondas de tool-calling por mensaje


def enviar_mensaje(messages: list) -> dict:
    """
    Envía los mensajes a GLM 5.2 con las herramientas disponibles.
    Si el modelo decide llamar una tool, se ejecuta y se reenvía el resultado.
    Pasa la respuesta final por el guardrail anti-alucinaciones.
    """
    for _ in range(MAX_TOOL_ROUNDS):
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            tools=TOOLS_SCHEMA,
            tool_choice="auto",
            temperature=0.3,  # baja temperatura = menos alucinaciones
            max_tokens=1024,
        )

        msg = response.choices[0].message

        # Si no hay tool calls, devolver la respuesta final
        if not msg.tool_calls:
            contenido = msg.content or ""

            # ── Guardrail: validar antes de devolver ─────────────────────
            validacion = validar_respuesta(contenido, messages)
            if not validacion["ok"]:
                logger.warning(f"GUARDRAIL bloqueó: {validacion['razon']}")
                contenido = validacion["mensaje_alternativo"]

            return {"content": contenido, "role": "assistant"}

        # Ejecutar cada tool call solicitado por el modelo
        messages.append({
            "role": "assistant",
            "content": msg.content,
            "tool_calls": [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {"name": tc.function.name, "arguments": tc.function.arguments},
                }
                for tc in msg.tool_calls
            ],
        })

        for tc in msg.tool_calls:
            tool_name = tc.function.name
            tool_args = json.loads(tc.function.arguments)

            logger.info(f"[TOOL] {tool_name}({tool_args})")
            print(f"  [TOOL] {tool_name}({tool_args})")

            result = ejecutar_tool(tool_name, tool_args)
            logger.info(f"[TOOL RESULT] {result[:200]}")
            print(f"  [TOOL RESULT] {result[:200]}...")

            messages.append({
                "role": "tool",
                "content": result,
                "tool_call_id": tc.id,
            })

    return {"content": "[Límite de tool calls alcanzado]", "role": "assistant"}


def chat_interactivo():
    """Loop de chat interactivo por terminal."""
    print("=" * 60)
    print("  EcoMatch Agent — GLM 5.2 (Kostra)")
    print("  Escribe 'salir' para terminar.")
    print("=" * 60)
    print(f"\n[EcoMatch] {WELCOME_MSG}")

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    while True:
        user_input = input("\n[Tú] > ").strip()
        if user_input.lower() in ("salir", "exit", "quit"):
            print("👋 ¡Hasta luego!")
            break
        if not user_input:
            continue

        messages.append({"role": "user", "content": user_input})
        logger.info(f"USER: {user_input}")

        print("\n[EcoMatch] ", end="", flush=True)
        result = enviar_mensaje(messages)
        print(result["content"])
        logger.info(f"AGENT: {result['content'][:200]}")

        messages.append({"role": "assistant", "content": result["content"]})


def ejecutar_test(test_file: str):
    """Ejecuta un caso de prueba desde un archivo JSON."""
    test_data = json.loads(Path(test_file).read_text(encoding="utf-8"))

    print(f"\n{'='*60}")
    print(f"  TEST: {test_data['nombre']}")
    print(f"  Descripción: {test_data['descripcion']}")
    print(f"{'='*60}")

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    for paso in test_data["pasos"]:
        user_msg = paso["user"]
        print(f"\n[Tú] > {user_msg}")

        messages.append({"role": "user", "content": user_msg})
        result = enviar_mensaje(messages)
        print(f"[EcoMatch] {result['content']}")

        messages.append({"role": "assistant", "content": result["content"]})

    print(f"\n{'─'*60}")
    print(f"  Resultado esperado: {test_data['resultado_esperado']}")
    print(f"{'─'*60}\n")


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        tests_dir = Path(__file__).parent / "tests"
        test_files = sorted(tests_dir.glob("*.json"))
        if not test_files:
            print("No hay archivos de test en ia/tests/")
            return
        for tf in test_files:
            ejecutar_test(str(tf))
    else:
        chat_interactivo()


if __name__ == "__main__":
    main()
