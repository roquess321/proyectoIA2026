import type {
	GeminiChatMessage,
	FastApiChatResponse,
	FastApiHistoryResponse,
	FastApiSessionSummary,
	MLPredictResponse
} from './types';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

/**
 * Envía un mensaje al backend orquestador FastAPI (el cual interactúa con Gemini y guarda en BD).
 * No expone ninguna API Key en el cliente.
 *
 * @param messageInput  Texto del mensaje o array de mensajes históricos (se extrae el último user message).
 * @param sessionId     ID opcional de sesión existente para mantener continuidad en la base de datos.
 * @returns             Objeto con la respuesta del modelo y el ID de sesión.
 */
export async function chat(
	messageInput: GeminiChatMessage[] | string,
	sessionId?: string | null,
	cedula?: string | null
): Promise<{ reply: string; sessionId: string }> {
	let messageText = '';

	if (typeof messageInput === 'string') {
		messageText = messageInput;
	} else if (Array.isArray(messageInput) && messageInput.length > 0) {
		// Buscar el último mensaje del usuario
		const lastUserMsg = [...messageInput].reverse().find((m) => m.role === 'user');
		messageText = lastUserMsg ? lastUserMsg.content : messageInput[messageInput.length - 1].content;
	} else {
		throw new Error('El mensaje no puede estar vacío.');
	}

	const url = `${API_BASE}/api/chat`;

	let response: Response;
	try {
		response = await fetch(url, {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify({
				message: messageText,
				session_id: sessionId || undefined,
				cedula: cedula || undefined
			})
		});
	} catch (networkError) {
		throw new Error(
			'No se pudo conectar con el servidor backend FastAPI (http://localhost:8000). ' +
			'Asegúrate de haber iniciado el backend con "uv run uvicorn backend.main:app --reload".'
		);
	}

	if (!response.ok) {
		const errorText = await response.text();
		throw new Error(`Error del servidor backend (${response.status}): ${errorText}`);
	}

	const data: FastApiChatResponse = await response.json();

	if (!data.reply) {
		throw new Error('La respuesta del servidor no contiene texto.');
	}

	return {
		reply: data.reply,
		sessionId: data.session_id
	};
}

/**
 * Obtiene el historial completo de una sesión persistido en la base de datos SQLite.
 */
export async function getChatHistory(sessionId: string): Promise<FastApiHistoryResponse> {
	const response = await fetch(`${API_BASE}/api/chat/history/${sessionId}`);
	if (!response.ok) {
		throw new Error(`No se pudo cargar el historial de la sesión ${sessionId}`);
	}
	return response.json();
}

/**
 * Lista todas las sesiones de chat almacenadas en la base de datos.
 */
export async function listChatSessions(): Promise<FastApiSessionSummary[]> {
	const response = await fetch(`${API_BASE}/api/chat/sessions`);
	if (!response.ok) {
		throw new Error('No se pudieron obtener las sesiones de chat.');
	}
	return response.json();
}

/**
 * Consulta la predicción de Machine Learning directamente al backend.
 * Evalúa los 3 modelos del primer parcial: Regresión Logística, Árbol de Decisión y Random Forest.
 */
export async function getMLPrediction(
	materia: string,
	primerParcial: number,
	segundoParcial: number,
	tplab: number
): Promise<MLPredictResponse> {
	const response = await fetch(`${API_BASE}/api/ml/predict`, {
		method: 'POST',
		headers: { 'Content-Type': 'application/json' },
		body: JSON.stringify({
			materia,
			primer_parcial: primerParcial,
			segundo_parcial: segundoParcial,
			tplab
		})
	});

	if (!response.ok) {
		const err = await response.text();
		throw new Error(`Error en predicción ML (${response.status}): ${err}`);
	}

	return response.json();
}

/**
 * Obtiene la lista de modelos de Machine Learning cargados y disponibles en el servidor.
 */
export async function getAvailableMLModels(): Promise<{
	primer_parcial: Array<Record<string, unknown>>;
	segundo_parcial: Array<Record<string, unknown>>;
	modelos_activos: string[];
	variables_requeridas: string[];
}> {
	const response = await fetch(`${API_BASE}/api/ml/models`);
	if (!response.ok) {
		throw new Error('No se pudo obtener el catálogo de modelos ML.');
	}
	return response.json();
}

