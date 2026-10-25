export interface StudentProfile {
	nombre: string;
	estado: string;
	matricula: string;
	carrera: string;
	plan: string;
	semestre: string;
	avatarUrl: string;
}

export interface MetricCard {
	id: string;
	title: string;
	value: string | number;
	total?: string | number;
	unit?: string;
	icon: string;
	footerType: 'badge' | 'progress' | 'split' | 'alert';
	badgeText?: string;
	badgeIcon?: string;
	progressPercent?: number;
	leftLabel?: string;
	rightLabel?: string;
	safeCount?: number;
	alertCount?: number;
	alertMessage?: string;
}

export interface CourseGrade {
	label: string;
	value: string;
	max?: string;
	subtext: string;
	highlight?: boolean;
	isPending?: boolean;
	isApproved?: boolean;
}

export interface Course {
	id: string;
	code: string;
	name: string;
	professor: string;
	status: 'habilitado' | 'en_curso' | 'excelencia' | 'alerta' | 'favorable';
	statusBadge: {
		text: string;
		type: 'secondary' | 'neutral' | 'highest' | 'error';
		icon?: string;
		dot?: boolean;
	};
	grades: CourseGrade[];
	aiPrognosis: {
		text: string;
		highlightText: string;
		isCritical?: boolean;
	};
	accumulatedScore: string;
	hasAlertBorder?: boolean;
	actionLink?: {
		label: string;
		path: string;
	};
}

export interface ExamEvent {
	id: string;
	month: string;
	day: string;
	title: string;
	subtitle: string;
	daysRemaining: number;
	time: string;
	urgency: 'normal' | 'critical' | 'final';
}
