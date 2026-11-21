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

export type ScraperStepId =
  | "handshake"
  | "inscripciones"
  | "calificaciones"
  | "persistencia";

export type ScraperStepStatus = "idle" | "running" | "done" | "error";

export interface ScraperStatusData {
  api_online: boolean;
  playwright_ready: boolean;
  insweb_url: string;
  insweb_reachable: boolean | null;
  insweb_latency_ms: number | null;
  insweb_status_code: number | null;
  sqlite_ready: boolean;
  estudiantes_count: number;
  active_jobs: number;
  student_synced: boolean | null;
  student_last_sync: string | null;
  student_inscripciones_count: number | null;
  student_parciales_count: number | null;
  student_notas_count: number | null;
}

export interface ScraperStreamProgressEvent {
  type: "progress";
  step: ScraperStepId;
  step_status: Exclude<ScraperStepStatus, "idle">;
  progress: number;
  message: string;
  meta?: Record<string, string | number | boolean | null>;
}

export interface ScraperStreamCompleteEvent {
  type: "complete";
  ok: true;
  cedula: string;
  message: string;
  inscripciones_count: number;
  parciales_count: number;
  notas_count: number;
  progress: number;
}

export interface ScraperStreamErrorEvent {
  type: "error";
  ok: false;
  detail: string;
  step?: ScraperStepId;
  step_status?: "error";
}

export type ScraperStreamEvent =
  | ScraperStreamProgressEvent
  | ScraperStreamCompleteEvent
  | ScraperStreamErrorEvent;

/**
 * Consulta la telemetría real del motor de scraping, conectividad a INSWEB y estado de SQLite.
 */
export async function getScraperStatus(
  cedula?: string | null,
  checkInsweb = true,
): Promise<ScraperStatusData> {
  const params = new URLSearchParams();
  params.set("check_insweb", checkInsweb ? "true" : "false");
  if (cedula && cedula.trim()) {
    params.set("cedula", cedula.trim());
  }

  const res = await fetch(`${API_BASE}/api/scraper/status?${params.toString()}`);
  if (!res.ok) {
    const errData = (await res
      .json()
      .catch(() => ({ detail: "No se pudo consultar el estado del scraper." }))) as {
      detail?: string;
    };
    throw new Error(
      errData.detail || `Error al consultar estado del scraper (${res.status})`,
    );
  }
  return (await res.json()) as ScraperStatusData;
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

export interface OfficialExamItem {
  id: string;
  asignatura: string;
  instancia: string;
  fecha: string;
  month: string;
  day: string;
  title: string;
  subtitle: string;
  days_remaining: number;
  time: string;
  urgency: "normal" | "critical" | "final";
}

export interface OfficialScheduleResponse {
  source: string;
  periodo: string | null;
  fuente: string;
  actualizado_en: string | null;
  archivo: string;
  examenes: OfficialExamItem[];
}

/**
 * Obtiene el calendario oficial de exámenes leído desde data/horarios_oficiales/.
 */
export async function getOfficialExamSchedule(
  cedula?: string | null,
): Promise<OfficialScheduleResponse> {
  const params = new URLSearchParams();
  if (cedula && cedula.trim()) {
    params.set("cedula", cedula.trim());
  }
  const query = params.toString();
  const url = query
    ? `${API_BASE}/api/horarios/examenes?${query}`
    : `${API_BASE}/api/horarios/examenes`;

  const res = await fetch(url);
  if (!res.ok) {
    throw new Error(`Error al consultar calendario oficial (${res.status})`);
  }
  return (await res.json()) as OfficialScheduleResponse;
}
