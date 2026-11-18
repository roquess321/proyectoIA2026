import os
import httpx
from typing import List, Dict, Optional, Any
from .ml import predecir_aprobacion, predecir_serie_temporal

GEMINI_API_BASE = "https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash-lite:generateContent"

SYSTEM_INSTRUCTION = """Eres el Copiloto Académico de FIUNA (Facultad de Ingeniería, Universidad Nacional de Asunción).
Tu rol es asistir a estudiantes de ingeniería con consultas académicas: planes de estudio, estrategias de exámenes, cálculos de notas, reglamentos, y muy especialmente predicciones de rendimiento académico con Inteligencia Artificial.

HERRAMIENTAS DE PREDICCIÓN CON INTELIGENCIA ARTIFICIAL:
1. 'predecir_probabilidad_aprobacion' (EVALUACIÓN INTEGRAL - TODOS LOS EXÁMENES REALIZADOS):
   - Úsala cuando el estudiante cuente con las 3 notas de proceso (1er Parcial, 2do Parcial y TPLab).
   - Infiere simultáneamente con 5 modelos de IA:
     a) 3 Modelos Clásicos: Regresión Logística, Árbol de Decisión y Random Forest (200 estimadores).
     b) 2 Modelos de Serie Temporal: Ensamble Temporal Dinámico (Gradient Boosting) y Red Neuronal Recurrente LSTM (PyTorch Deep Learning con compuertas de memoria).
   - AL REPORTAR, DEBES SIEMPRE PRESENTAR:
     * El porcentaje individual de los 3 modelos clásicos.
     * El análisis de la Serie Temporal y la Red Neuronal Recurrente LSTM (explicando la tendencia temporal, velocidad de mejora o fatiga acumulada a lo largo del semestre).
     * El consenso global ponderado de todos los modelos y recomendaciones específicas para el examen final.

2. 'analizar_serie_temporal_aprobacion' (PREDICCIÓN PROGRESIVA EN CURSO):
   - Úsala cuando el estudiante esté cursando y solo tenga rendido el 1er Parcial (o 1er Parcial + TP), o pregunte específicamente por su evolución secuencial o qué puntajes necesita en las siguientes evaluaciones para firmar.
   - Informa: probabilidad temprana, etapa temporal, tendencia, comparación entre Ensamble y LSTM, y metas numéricas para los exámenes restantes.

REGLAS DE RESPUESTA:
- Responde siempre en español (Paraguay).
- Cuando el estudiante pregunte si va a aprobar o cómo va su rendimiento, DEBES invocar la herramienta correspondiente sin dudar.
- Si las notas figuran en el contexto oficial del alumno, extrae esos datos automáticamente para invocar la herramienta.
- Mantén un tono técnico, profesional, constructivo y cercano."""


ML_TOOLS_DECLARATION = [
    {
        "function_declarations": [
            {
                "name": "analizar_serie_temporal_aprobacion",
                "description": (
                    "Modelo de Serie Temporal Dinámica: analiza la probabilidad de aprobación progresiva a medida "
                    "que el alumno avanza en el semestre. Permite predecir en cualquier momento después del Primer Parcial "
                    "(Hito 1: solo 1er Parcial; Hito 2: 1er Parcial + TP/Taller; Hito 3: proceso completo). "
                    "Calcula la tendencia temporal y proyecta las notas necesarias en las siguientes evaluaciones para firmar."
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
                        "tplab": {
                            "type": "NUMBER",
                            "description": "Puntaje obtenido en TP / Taller / Laboratorio (0-100). Opcional si aún no se entregó."
                        },
                        "segundo_parcial": {
                            "type": "NUMBER",
                            "description": "Puntaje obtenido en el Segundo Parcial (0-100). Opcional si aún no se rindió."
                        }
                    },
                    "required": ["primer_parcial"]
                }
            },
            {
                "name": "predecir_probabilidad_aprobacion",
                "description": (
                    "Ejecuta la inferencia de los 3 modelos clásicos (Regresión Logística, "
                    "Árbol de Decisión y Random Forest) para predecir si el alumno aprueba la asignatura "
                    "con el conjunto completo de evaluaciones de proceso."
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
    if nombre_funcion == "analizar_serie_temporal_aprobacion":
        materia = str(args.get("materia", "ESTATICA"))
        p1 = float(args.get("primer_parcial", 0.0))
        tplab = float(args["tplab"]) if args.get("tplab") is not None else None
        p2 = float(args["segundo_parcial"]) if args.get("segundo_parcial") is not None else None
        return predecir_serie_temporal(
            materia=materia,
            primer_parcial=p1,
            tplab=tplab,
            segundo_parcial=p2,
        )

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
