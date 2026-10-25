import type { GeminiChatMessage, GeminiApiResponse } from './types';

const GEMINI_API_BASE =
	'https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash-lite:generateContent';

/**
 * System prompt que contextualiza al LLM como asistente académico FIUNA.
 * Se inyecta al inicio de cada conversación para dar coherencia a las respuestas.
 */
const SYSTEM_INSTRUCTION = `Eres el Copiloto Académico de FIUNA (Facultad de Ingeniería, Universidad Nacional de Asunción).
Tu rol es asistir a estudiantes de ingeniería con consultas académicas: planes de estudio, estrategias de exámenes, cálculos de notas, reglamentos y orientación general.

Reglas:
- Responde siempre en español (Paraguay).
- Sé conciso y directo; usa viñetas cuando sea apropiado.
- Cuando el estudiante pregunte sobre notas o habilitación, explica los cálculos paso a paso.
- No inventes datos específicos sobre profesores o cátedras si no tienes certeza.
- Si no puedes responder algo, indícalo honestamente.
- Mantén un tono profesional pero cercano.`;

/**
 * Envía un array de mensajes al modelo Gemini y devuelve la respuesta de texto.
 * Usa únicamente `fetch` nativo — sin dependencias externas.
 *
 * @param messages  Historial completo de la conversación (user / model).
 * @returns         Texto plano con la respuesta del modelo.
 * @throws          Error si la API key no está configurada o la petición falla.
 */
export async function chat(messages: GeminiChatMessage[]): Promise<string> {
	const apiKey = import.meta.env.VITE_GEMINI_API_KEY as string | undefined;

	if (!apiKey || apiKey === 'TU_CLAVE_GEMINI_AQUI') {
		throw new Error(
			'La clave API de Gemini no está configurada. ' +
			'Añade tu clave en el archivo .env como VITE_GEMINI_API_KEY=tu_clave'
		);
	}

	const url = `${GEMINI_API_BASE}?key=${apiKey}`;
	const body = {
		system_instruction: {
			parts: [{ text: SYSTEM_INSTRUCTION }]
		},
		contents: messages.map((msg) => ({
			role: msg.role,
			parts: [{ text: msg.content }]
		})),
		generationConfig: {
			temperature: 0.7,
			topP: 0.95,
			topK: 40,
			maxOutputTokens: 1024
		}
	};

	const response = await fetch(url, {
		method: 'POST',
		headers: { 'Content-Type': 'application/json' },
		body: JSON.stringify(body)
	});

	if (!response.ok) {
		const errorText = await response.text();
		throw new Error(`Error de la API Gemini (${response.status}): ${errorText}`);
	}

	const data: GeminiApiResponse = await response.json();

	if (data.error) {
		throw new Error(`Gemini error: ${data.error.message}`);
	}

	const text = data.candidates?.[0]?.content?.parts?.[0]?.text;

	if (!text) {
		throw new Error('La respuesta de Gemini no contiene texto.');
	}

	return text;
}

/**
 * Placeholder para futuras predicciones ML.
 * Cuando se integre un modelo de predicción, esta función convertirá
 * el payload en un prompt estructurado y reutilizará `chat()`.
 *
 * @example
 * // Futuro uso:
 * // const result = await predict({ subjectId: 'mec-431', p1: 9, p2: 14, lab: 8.5, attendanceRate: 82 });
 */
// export async function predict(input: PredictionInput): Promise<PredictionResult> {
//   const prompt = `Dado un alumno con P1=${input.p1}, P2=${input.p2}, Lab=${input.lab}...`;
//   const response = await chat([{ role: 'user', content: prompt }]);
//   // Parsear respuesta estructurada...
//   return { probability: 0, requiredFinalScore: 0, recommendation: response };
// }
