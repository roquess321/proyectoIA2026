import os
import httpx
from typing import List, Dict

GEMINI_API_BASE = "https://generativelanguage.googleapis.com/v1beta/models/gemini-3.8-flash:generateContent"

SYSTEM_INSTRUCTION = """Eres el Copiloto Académico de FIUNA (Facultad de Ingeniería, Universidad Nacional de Asunción).
Tu rol es asistir a estudiantes de ingeniería con consultas académicas: planes de estudio, estrategias de exámenes, cálculos de notas, reglamentos y orientación general.

Reglas:
- Responde siempre en español (Paraguay).
- Sé conciso y directo; usa viñetas cuando sea apropiado.
- Cuando el estudiante pregunte sobre notas o habilitación, explica los cálculos paso a paso.
- No inventes datos específicos sobre profesores o cátedras si no tienes certeza.
- Si no puedes responder algo, indícalo honestamente.
- Mantén un tono profesional pero cercano."""


async def call_gemini(history: List[Dict[str, str]], new_message: str) -> str:
    """
    Envía la conversación (con memoria de mensajes previos) al modelo Gemini mediante su API REST.
    Mantiene la API Key resguardada estrictamente en el backend.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or api_key == "TU_CLAVE_GEMINI_AQUI":
        raise ValueError(
            "La clave GEMINI_API_KEY no está configurada en las variables de entorno del servidor. "
            "Asegúrate de definirla en el archivo .env del backend."
        )

    url = f"{GEMINI_API_BASE}?key={api_key}"

    # Construir contenido con historial previo + nuevo mensaje
    contents = []
    for msg in history:
        # Gemini espera roles 'user' o 'model'
        role = "model" if msg["role"] in ["model", "assistant"] else "user"
        contents.append({
            "role": role,
            "parts": [{"text": msg["content"]}]
        })

    # Añadir el mensaje actual
    contents.append({
        "role": "user",
        "parts": [{"text": new_message}]
    })

    payload = {
        "system_instruction": {
            "parts": [{"text": SYSTEM_INSTRUCTION}]
        },
        "contents": contents,
        "generationConfig": {
            "temperature": 0.7,
            "topP": 0.95,
            "topK": 40,
            "maxOutputTokens": 1024
        }
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(url, json=payload)
        if response.status_code != 200:
            raise RuntimeError(f"Error de la API Gemini ({response.status_code}): {response.text}")

        data = response.json()
        if "error" in data:
            raise RuntimeError(f"Gemini error: {data['error'].get('message', 'Desconocido')}")

        try:
            text = data["candidates"][0]["content"]["parts"][0]["text"]
            return text
        except (KeyError, IndexError):
            raise RuntimeError("La respuesta de Gemini no contiene texto válido.")
