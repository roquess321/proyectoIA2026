import os
import httpx
from typing import List, Dict, Optional, Any
from .ml.predictor import predecir_aprobacion

GEMINI_API_BASE = "https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash-lite:generateContent"

SYSTEM_INSTRUCTION = """Eres el Copiloto Académico de FIUNA (Facultad de Ingeniería, Universidad Nacional de Asunción).
Tu rol es asistir a estudiantes de ingeniería con consultas académicas: planes de estudio, estrategias de exámenes, cálculos de notas, reglamentos, y muy especialmente predicciones de rendimiento académico con Inteligencia Artificial.

HERRAMIENTA DE PREDICCIÓN CON MACHINE LEARNING (1er Parcial):
Dispones de la herramienta 'predecir_probabilidad_aprobacion', impulsada por 3 modelos de Machine Learning entrenados con datos reales de la FIUNA:
1. Regresión Logística (modelo probabilístico lineal base con escalado)
2. Árbol de Decisión (modelo no lineal basado en reglas jerárquicas)
3. Random Forest (ensamble de 200 árboles de decisión)

REGLAS DE RESPUESTA:
- Responde siempre en español (Paraguay).
- Cuando el estudiante consulte sobre pronósticos, probabilidades o si va a aprobar/pasar una materia (o pregunte "¿apruebo?", "predecir notas", o analice parciales de Estática u otra materia), DEBES invocar la herramienta 'predecir_probabilidad_aprobacion'.
- Si las notas no están explícitas en el mensaje pero figuran en el contexto académico o del simulador, usa esos valores para invocar la herramienta. Si faltan datos indispensables, solicítalos amablemente.
- Al reportar la predicción, DEBES SIEMPRE mostrar de forma clara y explícita el porcentaje de probabilidad calculado por CADA UNO de los tres modelos (Regresión Logística, Árbol de Decisión y Random Forest), el promedio de consenso y un diagnóstico o recomendación académica constructiva.
- Mantén un tono profesional, motivador y cercano."""


ML_TOOLS_DECLARATION = [
    {
        "function_declarations": [
            {
                "name": "predecir_probabilidad_aprobacion",
                "description": (
                    "Ejecuta la inferencia de los 3 modelos de Machine Learning (Regresión Logística, "
                    "Árbol de Decisión y Random Forest) para predecir si el alumno aprueba la asignatura "
                    "y devolver las 3 probabilidades individuales calculadas."
                ),
                "parameters": {
                    "type": "OBJECT",
                    "properties": {
                        "materia": {
                            "type": "STRING",
                            "description": "Nombre de la materia (ejemplo: 'ESTATICA', 'CALCULO 1')."
                        },
                        "primer_parcial": {
                            "type": "NUMBER",
                            "description": "Puntaje obtenido en el Primer Parcial (0-100)."
                        },
                        "segundo_parcial": {
                            "type": "NUMBER",
                            "description": "Puntaje obtenido o proyectado en el Segundo Parcial (0-100)."
                        },
                        "tplab": {
                            "type": "NUMBER",
                            "description": "Puntaje obtenido o proyectado en Trabajo Práctico / Taller / Laboratorio (0-100)."
                        }
                    },
                    "required": ["primer_parcial", "segundo_parcial", "tplab"]
                }
            }
        ]
    }
]


def ejecutar_herramienta_local(nombre_funcion: str, args: Dict[str, Any]) -> Dict[str, Any]:
    """Ejecuta localmente la herramienta requerida por el modelo Gemini."""
    if nombre_funcion == "predecir_probabilidad_aprobacion":
        materia = str(args.get("materia", "ESTATICA"))
        p1 = float(args.get("primer_parcial", 0.0))
        p2 = float(args.get("segundo_parcial", 0.0))
        tplab = float(args.get("tplab", 0.0))
        return predecir_aprobacion(
            materia=materia,
            primer_parcial=p1,
            segundo_parcial=p2,
            tplab=tplab
        )
    return {"error": f"Herramienta desconocida: {nombre_funcion}"}


async def call_gemini(
    history: List[Dict[str, str]],
    new_message: str,
    student_context: Optional[str] = None,
) -> str:
    """
    Envía la conversación (con memoria de mensajes previos) al modelo Gemini mediante su API REST.
    Soporta Function Calling nativo para la herramienta de predicción con los 3 modelos de ML.
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

    full_system_prompt = SYSTEM_INSTRUCTION
    if student_context:
        full_system_prompt += f"\n\n--- INFORMACIÓN DE LA BASE DE DATOS DEL ALUMNO (FIUNA) ---\n{student_context}"

    payload = {
        "system_instruction": {
            "parts": [{"text": full_system_prompt}]
        },
        "contents": contents,
        "tools": ML_TOOLS_DECLARATION,
        "generationConfig": {
            "temperature": 0.5,
            "topP": 0.95,
            "topK": 40,
            "maxOutputTokens": 1024
        }
    }

    async with httpx.AsyncClient(timeout=35.0) as client:
        response = await client.post(url, json=payload)
        if response.status_code != 200:
            raise RuntimeError(f"Error de la API Gemini ({response.status_code}): {response.text}")

        data = response.json()
        if "error" in data:
            raise RuntimeError(f"Gemini error: {data['error'].get('message', 'Desconocido')}")

        candidate = data.get("candidates", [{}])[0]
        content_obj = candidate.get("content", {})
        parts = content_obj.get("parts", [])

        if not parts:
            raise RuntimeError("La respuesta de Gemini no contiene partes válidas.")

        # Verificar si el modelo solicitó una llamada a función (Function Calling)
        function_call_part = next((p for p in parts if "functionCall" in p), None)
        if function_call_part:
            fn_call = function_call_part["functionCall"]
            fn_name = fn_call.get("name")
            fn_args = fn_call.get("args", {})

            # 1. Ejecutar localmente el cálculo de ML
            fn_result = ejecutar_herramienta_local(fn_name, fn_args)

            # 2. Re-enviar turno a Gemini preservando la estructura y thoughtSignature
            contents.append({
                "role": "model",
                "parts": [function_call_part]
            })
            contents.append({
                "role": "user",
                "parts": [{
                    "functionResponse": {
                        "name": fn_name,
                        "response": {
                            "output": fn_result
                        }
                    }
                }]
            })

            second_payload = {
                "system_instruction": {
                    "parts": [{"text": full_system_prompt}]
                },
                "contents": contents,
                "tools": ML_TOOLS_DECLARATION,
                "generationConfig": {
                    "temperature": 0.5,
                    "maxOutputTokens": 1024
                }
            }

            second_resp = await client.post(url, json=second_payload)
            if second_resp.status_code != 200:
                # Si por alguna razón la 2da llamada falla, devolvemos formato directo con las probabilidades
                resumen = fn_result.get("resumen", {})
                probs = fn_result.get("probabilidades", {})
                return (
                    f"### Pronóstico de Aprobación ({fn_args.get('materia', 'ESTATICA')}):\n\n"
                    f"- **Regresión Logística:** {probs.get('regresion_logistica', {}).get('probabilidad', 'N/A')}%\n"
                    f"- **Árbol de Decisión:** {probs.get('arbol_decision', {}).get('probabilidad', 'N/A')}%\n"
                    f"- **Random Forest:** {probs.get('random_forest', {}).get('probabilidad', 'N/A')}%\n\n"
                    f"**Probabilidad Promedio:** {resumen.get('probabilidad_promedio', 'N/A')}%\n"
                    f"**Diagnóstico:** {resumen.get('diagnostico', '')}\n\n"
                    f"{resumen.get('recomendacion', '')}"
                )

            data2 = second_resp.json()
            try:
                text_part = data2["candidates"][0]["content"]["parts"][0]["text"]
                return text_part
            except (KeyError, IndexError):
                raise RuntimeError("La respuesta final de Gemini tras la ejecución de la herramienta fue vacía.")

        # Si respondió con texto directo
        try:
            return parts[0]["text"]
        except (KeyError, IndexError):
            raise RuntimeError("La respuesta de Gemini no contiene texto válido.")
