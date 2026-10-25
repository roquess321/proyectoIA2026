/**
 * Tipos para el servicio de IA.
 * Separados del modelo de dominio (simulator.ts) para desacoplar la capa de transporte.
 * A futuro, este archivo también contendrá tipos para predicciones ML.
 */

/** Mensaje individual en la conversación con el LLM */
export interface GeminiChatMessage {
	role: 'user' | 'model';
	content: string;
}

/** Estructura que devuelve la API de Gemini (subset relevante) */
export interface GeminiApiResponse {
	candidates?: Array<{
		content?: {
			parts?: Array<{
				text?: string;
			}>;
		};
	}>;
	error?: {
		message: string;
		code: number;
	};
}

/**
 * Placeholder para futuras predicciones ML.
 * Cuando se integren modelos de predicción, se extenderá esta interfaz.
 */
export interface PredictionInput {
	subjectId: string;
	p1: number;
	p2: number;
	lab: number;
	attendanceRate: number;
}

export interface PredictionResult {
	probability: number;
	requiredFinalScore: number;
	recommendation: string;
}
