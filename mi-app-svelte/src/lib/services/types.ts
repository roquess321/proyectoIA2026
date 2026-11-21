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

/** Respuesta del endpoint POST /api/chat del backend FastAPI */
export interface FastApiChatResponse {
	reply: string;
	session_id: string;
}

/** Respuesta del endpoint GET /api/chat/history/{session_id} */
export interface FastApiHistoryResponse {
	session_id: string;
	title: string;
	messages: Array<{
		role: 'user' | 'model';
		content: string;
		created_at?: string;
	}>;
}

/** Resumen de sesión del endpoint GET /api/chat/sessions */
export interface FastApiSessionSummary {
	id: string;
	title: string;
	created_at: string;
	updated_at: string;
	message_count: number;
}

/**
 * Modelos y tipos para predicciones de Machine Learning (1er y 2do Parcial)
 */
export interface MLModelProbability {
	nombre: string;
	probabilidad: number;
	prediccion: 'Aprueba' | 'No Aprueba';
	descripcion: string;
}

export interface MLTemporalAnalysisSummary {
	tendencia?: string;
	estado_trayectoria?: string;
	puntos_acumulados_promedio?: number;
	proyeccion_siguiente_evaluacion?: Record<string, unknown>;
	comparativa?: {
		probabilidad_promedio?: number;
		diferencia_porcentual?: number;
		nivel_acuerdo?: string;
		analisis_comparativo?: string;
	};
}

export interface MLPredictResponse {
	materia: string;
	materia_modelo: string;
	parcial_origen: string;
	inputs: {
		primer_parcial: number;
		segundo_parcial: number;
		tplab: number;
	};
	probabilidades: {
		regresion_logistica: MLModelProbability;
		arbol_decision: MLModelProbability;
		random_forest: MLModelProbability;
		ensamble_temporal_gb?: MLModelProbability;
		red_neuronal_lstm?: MLModelProbability;
		[key: string]: MLModelProbability | undefined;
	};
	resumen: {
		probabilidad_promedio: number;
		diagnostico: string;
		recomendacion: string;
		probabilidad_modelos_clasicos?: number | null;
		probabilidad_modelos_temporales?: number | null;
		analisis_serie_temporal?: MLTemporalAnalysisSummary | null;
	};
}

export interface MLSequentialModelEntry {
	modelo: string;
	probabilidad: number;
	prediccion: string;
	tipo_algoritmo: string;
	auc_roc_historico?: number;
}

export interface MLSequentialComparativa {
	ensamble_clasico: MLSequentialModelEntry;
	red_neuronal_lstm: MLSequentialModelEntry;
	consenso: {
		probabilidad_promedio: number;
		diferencia_porcentual: number;
		nivel_acuerdo: string;
		analisis_comparativo: string;
	};
}

export interface MLSequentialPredictResponse {
	materia: string;
	materia_slug: string;
	etapa_temporal: number;
	hito: string;
	evaluaciones_registradas: {
		primer_parcial: number;
		tplab: number | null;
		segundo_parcial: number | null;
	};
	probabilidad_aprobacion: number;
	estado_trayectoria: string;
	tendencia: string;
	puntos_acumulados_promedio: number;
	proyeccion_siguiente_evaluacion: {
		tplab_objetivo?: number;
		segundo_parcial_objetivo?: number;
		segundo_parcial_minimo_firma?: number;
		segundo_parcial_recomendado_aprobacion?: number;
		nota_proceso_estimada?: number;
		firma_alcanzada?: boolean;
		meta_puntos_proceso?: number;
	};
	diagnostico: string;
	recomendacion: string;
	comparativa_modelos?: MLSequentialComparativa | null;
}

export interface MLModelMetricsEntry {
	accuracy?: number;
	auc_roc?: number;
	precision?: number;
	recall?: number;
	f1?: number;
	f1_score?: number;
}

export interface MLClassicMetadataItem {
	materia?: string;
	materia_slug?: string;
	materia_dataset?: string;
	fallback_global?: boolean;
	parcial_origen?: string;
	total_muestras?: number;
	tasa_aprobacion_real?: number;
	variables?: string[];
	metricas?: Record<string, MLModelMetricsEntry>;
}

export interface MLSeriesMetadataItem {
	materia?: string;
	slug?: string;
	materia_dataset?: string;
	fallback_global?: boolean;
	tipo_modelo?: string;
	total_registros_entrenamiento?: number;
	metricas?: {
		hito_1_primer_parcial?: MLModelMetricsEntry;
		hito_2_tp_taller?: MLModelMetricsEntry;
		hito_3_proceso_completo?: MLModelMetricsEntry;
	};
}

export interface MLLstmMetadataItem {
	materia?: string;
	slug?: string;
	materia_dataset?: string;
	fallback_global?: boolean;
	tipo_arquitectura?: string;
	total_estudiantes_entrenamiento?: number;
	total_estudiantes_test?: number;
	metricas_por_hito?: {
		hito_1_primer_parcial?: MLModelMetricsEntry;
		hito_2_tp_taller?: MLModelMetricsEntry;
		hito_3_proceso_completo?: MLModelMetricsEntry;
	};
}

export interface MLModelsCatalogResponse {
	primer_parcial: MLClassicMetadataItem[];
	segundo_parcial: Array<Record<string, unknown>>;
	series_temporales: {
		ensamble_clasico: MLSeriesMetadataItem[];
		red_neuronal_lstm: MLLstmMetadataItem[];
	};
	modelos_activos: string[];
	variables_requeridas: {
		estatico: string[];
		serie_temporal: string[];
	};
}

export interface MLRetrainResponse {
	ok: boolean;
	materia: string;
	materia_slug: string;
	materia_dataset: string;
	fallback_global: boolean;
	total_muestras: number;
	duracion_seg: number;
	metricas: {
		clasicos?: Record<string, MLModelMetricsEntry>;
		serie_temporal_auc_h3?: number;
		lstm_auc_h3?: number;
		random_forest_auc?: number;
	};
	mensaje: string;
}

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

