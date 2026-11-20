import { pingBackendHealth } from "./services/gemini";
import {
  getScraperStatus,
  type ScraperStepId,
  type ScraperStepStatus,
  type ScraperStreamEvent,
} from "./services/scraper";

export interface NavItem {
  path: string;
  href: string;
  icon: string;
  title: string;
  subtitle: string;
}

export interface ScraperStepState {
  id: ScraperStepId;
  title: string;
  defaultDescription: string;
  description: string;
  status: ScraperStepStatus;
  badgeText: string;
}

export interface ScraperLogEntry {
  id: number;
  time: string;
  level: "info" | "success" | "warn" | "error";
  message: string;
}

export interface StudentRecordCounts {
  inscripciones: number;
  parciales: number;
  notas: number;
}

const STEP_ORDER: ScraperStepId[] = [
  "handshake",
  "inscripciones",
  "calificaciones",
  "persistencia",
];

function createInitialSteps(): ScraperStepState[] {
  return [
    {
      id: "handshake",
      title: "Handshake HTTPS insweb.ing.una.py",
      defaultDescription: "Validación de sesión con C.I. y PIN",
      description: "Validación de sesión con C.I. y PIN",
      status: "idle",
      badgeText: "En espera",
    },
    {
      id: "inscripciones",
      title: "Extracción de Inscripciones y Ficha",
      defaultDescription: "Lectura de carrera y materias vigentes",
      description: "Lectura de carrera y materias vigentes",
      status: "idle",
      badgeText: "En espera",
    },
    {
      id: "calificaciones",
      title: "Scraping de Calificaciones Históricas",
      defaultDescription: "Notas finales y parciales por periodo",
      description: "Notas finales y parciales por periodo",
      status: "idle",
      badgeText: "En espera",
    },
    {
      id: "persistencia",
      title: "Persistencia Relacional SQLite",
      defaultDescription: "Guardado normalizado en copilot.db",
      description: "Guardado normalizado en copilot.db",
      status: "idle",
      badgeText: "En espera",
    },
  ];
}

function nowTimeString(): string {
  return new Date().toLocaleTimeString("es-PY", {
    hour12: false,
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
  });
}

export const navItems: NavItem[] = [
  {
    path: "acceso-insweb",
    href: "/",
    icon: "sync_alt",
    title: "Acceso & InsWeb",
    subtitle: "Vinculación Oficial",
  },
  {
    path: "dashboard",
    href: "/dashboard",
    icon: "dashboard",
    title: "Dashboard",
    subtitle: "Panel Principal",
  },
  {
    path: "agente-ia-pronosticos",
    href: "/agente-ia-pronosticos",
    icon: "psychology",
    title: "Agente IA & Pronósticos",
    subtitle: "Simulador Predictivo",
  },
  {
    path: "historial-malla-curricular",
    href: "/historial-malla-curricular",
    icon: "account_tree",
    title: "Historial & Malla",
    subtitle: "Calificaciones & Correlativas",
  },
  {
    path: "feedback-ajustes-ia",
    href: "/dashboard#ajustes",
    icon: "tune",
    title: "Feedback & Ajustes IA",
    subtitle: "Afinación del Modelo",
  },
];

export class AcademicState {
  isRescraping = $state(false);
  isScrapingLive = $state(false);
  latency = $state<number | null>(null);
  backendOnline = $state<boolean | null>(null);
  playwrightReady = $state<boolean | null>(null);
  inswebReachable = $state<boolean | null>(null);
  inswebLatencyMs = $state<number | null>(null);
  sqliteReady = $state<boolean | null>(null);
  estudiantesCount = $state<number | null>(null);
  activeJobs = $state(0);
  studentCounts = $state<StudentRecordCounts | null>(null);
  progress = $state(0);
  lastCheckTime = $state<string | null>(null);
  pipelineStatus = $state("Listo (ejecución bajo demanda)");
  steps = $state<ScraperStepState[]>(createInitialSteps());
  logs = $state<ScraperLogEntry[]>([]);
  activeNav = $state("acceso-insweb");
  isMobileMenuOpen = $state(false);

  private logSeq = 0;

  toggleMobileMenu(): void {
    this.isMobileMenuOpen = !this.isMobileMenuOpen;
  }

  closeMobileMenu(): void {
    this.isMobileMenuOpen = false;
  }

  addLog(message: string, level: ScraperLogEntry["level"] = "info"): void {
    this.logSeq += 1;
    const entry: ScraperLogEntry = {
      id: this.logSeq,
      time: nowTimeString(),
      level,
      message,
    };
    const next = [...this.logs, entry];
    this.logs = next.length > 80 ? next.slice(next.length - 80) : next;
  }

  clearLogs(): void {
    this.logs = [];
  }

  resetPipelineForRun(cedula: string): void {
    this.isScrapingLive = true;
    this.progress = 5;
    this.pipelineStatus = "Iniciando scraper Headless Chromium...";
    this.steps = createInitialSteps().map((step) =>
      step.id === "handshake"
        ? {
            ...step,
            status: "running",
            description: "Iniciando navegador Playwright y conectando...",
            badgeText: "Ejecutando",
          }
        : {
            ...step,
            status: "idle",
            badgeText: "Pendiente",
          },
    );
    this.addLog(
      `Iniciando sincronización en vivo para C.I. ${cedula} (SSE)...`,
      "info",
    );
  }

  applyStreamEvent(event: ScraperStreamEvent): void {
    if (event.type === "progress") {
      this.progress = Math.max(0, Math.min(100, event.progress));
      this.pipelineStatus = event.message.replace(/^[^\w[¿¡]+/, "").trim();

      const targetIdx = STEP_ORDER.indexOf(event.step);
      this.steps = this.steps.map((step, idx) => {
        if (idx < targetIdx && step.status !== "error") {
          return {
            ...step,
            status: "done",
            badgeText: "Completado",
          };
        }
        if (step.id === event.step) {
          const cleanMsg = event.message
            .replace(/^[\s🌐🚀✅🔍🔄⚠️❌💾↳]+/, "")
            .replace(/^\[(Scraper|Pipeline)\]\s*/i, "")
            .trim();
          const badge =
            event.step_status === "done"
              ? "Completado"
              : event.step_status === "error"
                ? "Error"
                : "Ejecutando";
          return {
            ...step,
            status: event.step_status,
            description: cleanMsg || step.defaultDescription,
            badgeText: badge,
          };
        }
        return step;
      });

      const level: ScraperLogEntry["level"] =
        event.step_status === "error"
          ? "error"
          : event.message.includes("⚠️")
            ? "warn"
            : event.step_status === "done" || event.message.includes("✅")
              ? "success"
              : "info";
      this.addLog(event.message, level);
      return;
    }

    if (event.type === "complete") {
      this.progress = 100;
      this.isScrapingLive = false;
      this.pipelineStatus = "Sincronización Completada";
      this.studentCounts = {
        inscripciones: event.inscripciones_count,
        parciales: event.parciales_count,
        notas: event.notas_count,
      };
      this.steps = this.steps.map((step) => ({
        ...step,
        status: "done",
        badgeText: "Completado",
      }));
      this.addLog(
        `Sincronización finalizada: ${event.inscripciones_count} inscripciones, ${event.parciales_count} parciales, ${event.notas_count} notas finales.`,
        "success",
      );
      return;
    }

    if (event.type === "error") {
      this.isScrapingLive = false;
      this.pipelineStatus = "Error en extracción";
      const failedStepId: ScraperStepId =
        event.step ??
        this.steps.find((s) => s.status === "running")?.id ??
        "handshake";

      this.steps = this.steps.map((step) => {
        if (step.id === failedStepId) {
          return {
            ...step,
            status: "error",
            description: event.detail || "Fallo inesperado durante la fase.",
            badgeText: "Error",
          };
        }
        if (step.status === "running") {
          return {
            ...step,
            status: "idle",
            badgeText: "Detenido",
          };
        }
        return step;
      });
      this.addLog(`Error: ${event.detail}`, "error");
    }
  }

  async forceRescrape(cedula?: string | null): Promise<void> {
    if (this.isRescraping) return;
    this.isRescraping = true;

    if (!this.isScrapingLive) {
      this.pipelineStatus = "Verificando conexión y telemetría...";
    }

    const [health, statusResult] = await Promise.all([
      pingBackendHealth(),
      getScraperStatus(cedula, true).catch(() => null),
    ]);

    this.isRescraping = false;
    this.backendOnline = health.online;
    this.latency = health.latencyMs;
    this.lastCheckTime = nowTimeString();

    if (statusResult) {
      this.playwrightReady = statusResult.playwright_ready;
      this.inswebReachable = statusResult.insweb_reachable;
      this.inswebLatencyMs = statusResult.insweb_latency_ms;
      this.sqliteReady = statusResult.sqlite_ready;
      this.estudiantesCount = statusResult.estudiantes_count;
      this.activeJobs = statusResult.active_jobs;

      if (
        statusResult.student_inscripciones_count !== null &&
        statusResult.student_parciales_count !== null &&
        statusResult.student_notas_count !== null
      ) {
        this.studentCounts = {
          inscripciones: statusResult.student_inscripciones_count,
          parciales: statusResult.student_parciales_count,
          notas: statusResult.student_notas_count,
        };
      } else {
        this.studentCounts = null;
      }

      const inswebTxt =
        statusResult.insweb_reachable === true
          ? `InsWeb OK (${statusResult.insweb_latency_ms ?? "--"} ms)`
          : "InsWeb sin respuesta";
      const sqliteTxt = statusResult.sqlite_ready
        ? `SQLite OK (${statusResult.estudiantes_count} perfiles)`
        : "SQLite error";

      this.addLog(
        `Diagnóstico: FastAPI OK (${health.latencyMs ?? "--"} ms) • ${inswebTxt} • ${sqliteTxt}`,
        statusResult.insweb_reachable === false ? "warn" : "info",
      );

      if (!this.isScrapingLive) {
        this.pipelineStatus =
          statusResult.insweb_reachable === false
            ? "InsWeb sin respuesta (FastAPI online)"
            : statusResult.playwright_ready
              ? "Sistema listo (ejecución bajo demanda)"
              : "Playwright no disponible";
      }
    } else {
      this.playwrightReady = null;
      this.inswebReachable = null;
      this.inswebLatencyMs = null;
      this.sqliteReady = false;
      this.activeJobs = 0;
      this.addLog(
        health.online
          ? "FastAPI respondió, pero falló /api/scraper/status."
          : "No se pudo conectar con el servidor backend FastAPI (puerto 8000).",
        "error",
      );
      if (!this.isScrapingLive) {
        this.pipelineStatus = health.online
          ? "Estado de telemetría no disponible"
          : "Backend FastAPI desconectado";
      }
    }
  }
}

export const academicState = new AcademicState();
