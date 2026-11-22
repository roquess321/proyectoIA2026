const STORAGE_KEY = 'fiunai_api_base_override';
const DEFAULT_API_BASE = (import.meta.env.VITE_API_URL || 'http://localhost:8000').replace(
	/\/+$/,
	''
);

function normalizeBaseUrl(raw: string): string | null {
	const trimmed = raw.trim().replace(/\/+$/, '');
	if (!trimmed) return null;
	try {
		const parsed = new URL(trimmed);
		if (parsed.protocol !== 'https:' && parsed.protocol !== 'http:') return null;
		return `${parsed.protocol}//${parsed.host}${parsed.pathname}`.replace(/\/+$/, '');
	} catch {
		return null;
	}
}

/**
 * Resuelve la URL base del backend FastAPI priorizando `?api=<URL>` (guardada en localStorage),
 * luego la configuración persistida en navegador y finalmente `VITE_API_URL`.
 */
export function getApiBase(): string {
	if (typeof window !== 'undefined') {
		const params = new URLSearchParams(window.location.search);
		const apiParam = params.get('api');
		if (apiParam !== null) {
			if (apiParam.trim().toLowerCase() === 'reset') {
				window.localStorage.removeItem(STORAGE_KEY);
			} else {
				const valid = normalizeBaseUrl(apiParam);
				if (valid) {
					window.localStorage.setItem(STORAGE_KEY, valid);
					return valid;
				}
			}
		}
		const stored = window.localStorage.getItem(STORAGE_KEY);
		if (stored) {
			const valid = normalizeBaseUrl(stored);
			if (valid) return valid;
		}
	}
	return DEFAULT_API_BASE;
}
