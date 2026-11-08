const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";

export interface ScraperSyncRequest {
  cedula: string;
  pin: string;
}

export interface ScraperSyncResponse {
  ok: boolean;
  message: string;
  cedula: string;
  inscripciones_count: number;
  parciales_count: number;
  notas_count: number;
}

export interface InscripcionData {
  carrera?: string;
  asignatura: string;
  semestre?: string;
  estado?: string;
}

export interface ParcialData {
  asignatura: string;
  tipo_examen: string;
  puntaje?: number;
  periodo?: string;
}

export interface NotaFinalData {
  asignatura: string;
  nota?: number;
  nota_literal?: string;
  fecha?: string;
  nro_acta?: string;
  tipo?: string;
  aprobado: boolean;
}

export interface EstudianteSummary {
  cedula: string;
  fecha_actualizacion?: string;
  inscripciones: InscripcionData[];
  parciales: ParcialData[];
  notas: NotaFinalData[];
}

/**
 * Invoca al backend FastAPI para iniciar la extracción en vivo desde INSWEB con Playwright en modo silencioso.
 */
export async function syncInsweb(
  cedula: string,
  pin: string,
): Promise<ScraperSyncResponse> {
  const res = await fetch(`${API_BASE}/api/scraper/sync`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ cedula, pin }),
  });

  if (!res.ok) {
    const errData = await res
      .json()
      .catch(() => ({ detail: "Error de red o servidor no disponible" }));
    throw new Error(
      errData.detail || `Error al sincronizar con INSWEB (${res.status})`,
    );
  }

  return (await res.json()) as ScraperSyncResponse;
}

/**
 * Obtiene el resumen consolidado de los datos académicos guardados en SQLite.
 */
export async function getEstudiante(
  cedula: string,
): Promise<EstudianteSummary> {
  const res = await fetch(
    `${API_BASE}/api/estudiantes/${encodeURIComponent(cedula)}`,
  );
  if (!res.ok) {
    const errData = await res
      .json()
      .catch(() => ({ detail: "Estudiante no encontrado" }));
    throw new Error(
      errData.detail || `Error al consultar estudiante (${res.status})`,
    );
  }
  return (await res.json()) as EstudianteSummary;
}
