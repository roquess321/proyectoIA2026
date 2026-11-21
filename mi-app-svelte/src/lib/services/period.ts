export interface AcademicPeriodInfo {
	year: number;
	cycle: 1 | 2;
	code: string;
	label: string;
	shortLabel: string;
}

/**
 * Calcula el periodo lectivo FIUNA vigente a partir de la fecha actual.
 * Enero–Julio -> Primer Ciclo (YYYY-1); Agosto–Diciembre -> Segundo Ciclo (YYYY-2).
 */
export function getCurrentAcademicPeriod(date: Date = new Date()): AcademicPeriodInfo {
	const year = date.getFullYear();
	const month = date.getMonth() + 1;
	const cycle: 1 | 2 = month <= 7 ? 1 : 2;
	const code = `${year}-${cycle}`;
	const cycleLong = cycle === 1 ? 'Primer Ciclo' : 'Segundo Ciclo';
	const cycleShort = cycle === 1 ? '1er Ciclo' : '2do Ciclo';
	return {
		year,
		cycle,
		code,
		label: `Periodo ${code} (${cycleLong})`,
		shortLabel: `${code} (${cycleShort})`
	};
}

/**
 * Formatea un código de periodo ("2026-2", "2026_C2", "Proyectado") para etiquetas de UI.
 */
export function formatPeriodLabel(period: string): string {
	const trimmed = period.trim();
	const match = trimmed.match(/^(\d{4})[-_]C?([12])$/i);
	if (match) {
		const [, year, cycle] = match;
		return `${year}-${cycle} (${cycle === '1' ? '1er Ciclo' : '2do Ciclo'})`;
	}
	return trimmed;
}

/**
 * Normaliza un código de periodo InsWeb ("2026_C2" -> "2026-2") o retorna el actual si no hay datos.
 */
export function inferCurrentPeriodFromParciales(
	parciales?: Array<{ periodo?: string }>
): string {
	const fallback = getCurrentAcademicPeriod().code;
	if (!parciales || parciales.length === 0) return fallback;

	const normalized: Array<{ raw: string; rank: number }> = [];
	for (const p of parciales) {
		const raw = p.periodo?.trim() ?? '';
		const match = raw.match(/^(\d{4})[-_]C?(\d+)$/i);
		if (match) {
			const year = parseInt(match[1], 10);
			const cycle = parseInt(match[2], 10);
			normalized.push({ raw: `${year}-${cycle}`, rank: year * 10 + cycle });
		}
	}

	if (normalized.length === 0) return fallback;
	normalized.sort((a, b) => b.rank - a.rank);
	return normalized[0].raw;
}
