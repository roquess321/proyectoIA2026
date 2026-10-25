import type { StudentProfile, MetricCard, Course, ExamEvent } from '../types/academic';

export const studentProfile: StudentProfile = {
	nombre: 'Alejandro Gabriel Benítez Bogado',
	estado: 'Activo',
	matricula: '2021-0482',
	carrera: 'Ingeniería Electromecánica',
	plan: 'Plan 2013',
	semestre: '7mo Semestre',
	avatarUrl:
		'https://lh3.googleusercontent.com/aida-public/AB6AXuA8ZitLRoQXGL27Mkmxr1owEdulcIbP6K5AGhoHAnFh5Jfmqzstvf6KVros7nfczyJlSb1psjZQsI15AKUCfyzB_teYDyRlG_wT2DIrL5J2FZgNrbvQsUOCsO_jC6YA_UY1-5j8HthtMr6Yw-ZQHEa1DiLMuDcw50H9mtoerm8Dvwuey6LCW6IJOnFYCi4OihAqT_qjwfBc80osfyVse8sCzVp-V9FCyBEoHCTqv3p2UDc_yD3wpB7P'
};

export const metricCards: MetricCard[] = [
	{
		id: 'ppg',
		title: 'Promedio PPG',
		value: '4.12',
		total: '5.00',
		icon: 'analytics',
		footerType: 'badge',
		badgeText: '+0.18 vs. corte anterior',
		badgeIcon: 'trending_up'
	},
	{
		id: 'creditos',
		title: 'Créditos Carrera',
		value: '168',
		total: '235 cr',
		icon: 'donut_large',
		footerType: 'progress',
		progressPercent: 71.5,
		badgeText: '71.5% completado'
	},
	{
		id: 'malla',
		title: 'Malla Curricular',
		value: '34',
		unit: 'aprobadas',
		icon: 'fact_check',
		footerType: 'split',
		leftLabel: 'Faltantes: 14 materias',
		rightLabel: 'Malla 2013'
	},
	{
		id: 'carga',
		title: 'Carga Semestral',
		value: '5',
		unit: 'asignaturas',
		icon: 'layers',
		footerType: 'badge',
		badgeText: 'Ciclo 2024-2 (24 hs/sem)',
		badgeIcon: 'schedule'
	},
	{
		id: 'habilitaciones',
		title: 'Habilitaciones',
		value: '',
		icon: 'shield',
		footerType: 'alert',
		safeCount: 4,
		alertCount: 1,
		alertMessage: 'Atención en Máquinas T.'
	}
];

export const courses: Course[] = [
	{
		id: 'mec-324',
		code: 'MEC-324',
		name: 'Termodinámica Aplicada',
		professor: 'Prof. Ing. Canese',
		status: 'habilitado',
		statusBadge: {
			text: 'HABILITADO PARA FINAL',
			type: 'secondary',
			dot: true
		},
		grades: [
			{ label: 'Parcial 1', value: '18', max: '20', subtext: '90% Ponderado' },
			{ label: 'Parcial 2', value: '16', max: '20', subtext: '80% Ponderado' },
			{ label: 'Laboratorio', value: '9', max: '10', subtext: 'Reglamentario' },
			{ label: 'Taller Máquinas', value: 'Aprobado', subtext: '100% Asistencia', isApproved: true }
		],
		aiPrognosis: {
			text: 'Pronóstico IA FIUNA:',
			highlightText: 'Calificación Proyectada 4 (Muy Bueno)'
		},
		accumulatedScore: 'Puntaje Acumulado: 43 / 50 pts'
	},
	{
		id: 'civ-412',
		code: 'CIV-412',
		name: 'Resistencia de Materiales II',
		professor: 'Prof. Ing. Galeano',
		status: 'en_curso',
		statusBadge: {
			text: 'EN CURSO',
			type: 'neutral',
			dot: true
		},
		grades: [
			{ label: 'Parcial 1', value: '12', max: '20', subtext: '60% Mínimo' },
			{ label: 'Parcial 2', value: 'Pendiente', subtext: 'Faltan 8 días', isPending: true },
			{ label: 'Laboratorio', value: '8', max: '10', subtext: '80% Aprobatorio' },
			{ label: 'Meta de Habilitación', value: '≥ 14 pts', subtext: 'En 2do Parcial', highlight: true }
		],
		aiPrognosis: {
			text: 'Pronóstico IA:',
			highlightText: 'Requiere 14 en P2 para asegurar habilitación'
		},
		accumulatedScore: 'Puntaje Actual: 20 / 30 pts'
	},
	{
		id: 'ele-341',
		code: 'ELE-341',
		name: 'Circuitos Magnéticos y Transformadores',
		professor: 'Prof. Ing. González',
		status: 'excelencia',
		statusBadge: {
			text: 'HABILITADO CON EXCELENCIA',
			type: 'highest',
			icon: 'star'
		},
		grades: [
			{ label: 'Parcial 1', value: '19', max: '20', subtext: '95% Sobresaliente' },
			{ label: 'Parcial 2', value: '17', max: '20', subtext: '85% Óptimo' },
			{ label: 'Laboratorio Ensayos', value: '10', max: '10', subtext: 'Puntaje Perfecto' },
			{ label: 'Proyección Final', value: 'Nota 5', subtext: '92% Probabilidad', highlight: true }
		],
		aiPrognosis: {
			text: 'Pronóstico IA:',
			highlightText: 'Candidato a Nota 5 (Sobresaliente FIUNA)'
		},
		accumulatedScore: 'Puntaje Acumulado: 46 / 50 pts'
	},
	{
		id: 'mec-431',
		code: 'MEC-431',
		name: 'Máquinas Térmicas I',
		professor: 'Prof. Ing. Martínez',
		status: 'alerta',
		hasAlertBorder: true,
		statusBadge: {
			text: 'ALERTA DE RIESGO',
			type: 'error',
			icon: 'report_problem'
		},
		grades: [
			{ label: 'Parcial 1', value: '09', max: '20', subtext: 'Bajo Umbral (45%)', highlight: true },
			{ label: 'Parcial 2', value: 'Pendiente', subtext: '12 Noviembre', isPending: true },
			{ label: 'Requisito P2', value: '≥ 15 / 20', subtext: 'Para no recursar', highlight: true },
			{ label: 'Acción Sugerida', value: 'Simular Plan', subtext: '', isPending: false }
		],
		actionLink: {
			label: 'Simular Plan',
			path: 'agente-ia-pronosticos'
		},
		aiPrognosis: {
			text: 'Pronóstico Crítico:',
			highlightText: 'Requiere 75% en P2 para habilitar derecho a examen final',
			isCritical: true
		},
		accumulatedScore: 'Puntaje Actual: 09 / 20 pts'
	},
	{
		id: 'ind-215',
		code: 'IND-215',
		name: 'Economía y Gestión en Ingeniería',
		professor: 'Prof. Lic. Duarte',
		status: 'favorable',
		statusBadge: {
			text: 'EN CURSO FAVORABLE',
			type: 'neutral',
			dot: true
		},
		grades: [
			{ label: 'Parcial 1', value: '15', max: '20', subtext: '75% Conforme' },
			{ label: 'Trabajos Prácticos', value: '95%', subtext: 'Entrega Completa' },
			{ label: 'Parcial 2', value: 'Pendiente', subtext: '25 Noviembre', isPending: true },
			{ label: 'Condición', value: 'Segura', subtext: 'Requiere ≥ 9 pts', highlight: true }
		],
		aiPrognosis: {
			text: 'Pronóstico IA:',
			highlightText: 'Proyección aprobatoria holgada (Calificación esperada 4 o 5)'
		},
		accumulatedScore: 'Puntaje Estimado: 85% global'
	}
];

export const examEvents: ExamEvent[] = [
	{
		id: 'exam-1',
		month: 'NOV',
		day: '04',
		title: 'Resistencia Materiales II',
		subtitle: '2do Parcial • Aula E-12',
		daysRemaining: 8,
		time: '08:00 hs',
		urgency: 'normal'
	},
	{
		id: 'exam-2',
		month: 'NOV',
		day: '12',
		title: 'Máquinas Térmicas I',
		subtitle: '2do Parcial • Aula M-04',
		daysRemaining: 16,
		time: '14:00 hs',
		urgency: 'critical'
	},
	{
		id: 'exam-3',
		month: 'NOV',
		day: '25',
		title: 'Economía y Gestión',
		subtitle: '2do Parcial • Salón Central',
		daysRemaining: 29,
		time: '16:00 hs',
		urgency: 'normal'
	},
	{
		id: 'exam-4',
		month: 'DIC',
		day: '09',
		title: '1er Periodo Finales',
		subtitle: 'Termodinámica Aplicada',
		daysRemaining: 43,
		time: '08:00 hs',
		urgency: 'final'
	}
];
