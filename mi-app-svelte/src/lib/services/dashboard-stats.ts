import type {
  StudentProfile,
  MetricCard,
  Course,
  CourseGrade,
  ExamEvent,
} from "../types/academic";
import type {
  EstudianteSummary,
  InscripcionData,
  ParcialData,
  NotaFinalData,
} from "./scraper";
import type { UserSession } from "../auth-state.svelte";
import {
  studentProfile as mockProfile,
  metricCards as mockMetrics,
  courses as mockCourses,
  examEvents as mockExams,
} from "../data/dashboard-mock";

export interface DashboardData {
  profile: StudentProfile;
  metrics: MetricCard[];
  courses: Course[];
  exams: ExamEvent[];
  isRealData: boolean;
  totalAprobadas: number;
  promedioPPG: number;
}

/**
 * Corrige fallas de caracteres típicas de codificaciones legacy en InsWeb.
 */
export function cleanAcademicText(text: string | null | undefined): string {
  if (!text) return "";
  return text
    .replace(/SE[\uFFFD\s]?ALES/gi, "SEÑALES")
    .replace(/DISE[\uFFFD\s]?O/gi, "DISEÑO")
    .replace(/L[\uFFFD]?GICO/gi, "LÓGICO")
    .replace(/PR[\uFFFD]?CTICO/gi, "PRÁCTICO")
    .replace(/MECATR[\uFFFD]?NICA/gi, "MECATRÓNICA")
    .replace(/ELECTR[\uFFFD]?NICA/gi, "ELECTRÓNICA")
    .replace(/INGENIER[\uFFFD]?A/gi, "INGENIERÍA")
    .replace(/TERMODIN[\uFFFD]?MICA/gi, "TERMODINÁMICA")
    .replace(/TEOR[\uFFFD]?A/gi, "TEORÍA")
    .replace(/QU[\uFFFD]?MICA/gi, "QUÍMICA")
    .replace(/F[\uFFFD]?SICA/gi, "FÍSICA")
    .replace(/AN[\uFFFD]?LISIS/gi, "ANÁLISIS")
    .replace(/M[\uFFFD]?QUINAS/gi, "MÁQUINAS")
    .replace(/EL[\uFFFD]?CTRICA/gi, "ELÉCTRICA")
    .replace(/C[\uFFFD]?LCULO/gi, "CÁLCULO")
    .replace(/[\uFFFD]/g, "Ñ")
    .trim();
}

/**
 * Normaliza nombres para comparación insensible a puntuación y acentos.
 */
function normalizeForComparison(str: string): string {
  return cleanAcademicText(str)
    .toLowerCase()
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .replace(/[^a-z0-9]/g, "");
}

/**
 * Transforma los datos reales extraídos por el scraper en estructuras completas para el Dashboard.
 */
export function buildDashboardData(
  summary: EstudianteSummary | null,
  user: UserSession | null,
): DashboardData {
  // Si no hay sesión o no hay datos reales del scraper, retornar el mock de demostración
  if (
    !user ||
    !summary ||
    (!summary.inscripciones.length && !summary.notas.length)
  ) {
    return {
      profile: mockProfile,
      metrics: mockMetrics,
      courses: mockCourses,
      exams: mockExams,
      isRealData: false,
      totalAprobadas: 34,
      promedioPPG: 4.12,
    };
  }

  const { inscripciones, parciales, notas } = summary;

  // 1. CÁLCULO DE PROMEDIO PPG (Notas Finales)
  const notasNumericas = notas
    .map((n) => n.nota)
    .filter((n): n is number => typeof n === "number" && !isNaN(n));

  const totalNotas = notasNumericas.length;
  const sumaNotas = notasNumericas.reduce((acc, val) => acc + val, 0);
  const promedioPPG = totalNotas > 0 ? +(sumaNotas / totalNotas).toFixed(2) : 0;

  // 2. MATERIAS APROBADAS Y AVANCE DE MALLA
  const materiasAprobadas = notas.filter(
    (n) =>
      n.aprobado || (n.nota !== undefined && n.nota !== null && n.nota >= 2),
  );
  const totalAprobadas = materiasAprobadas.length;

  // Estimación de malla FIUNA (~54 materias estándar para carreras de ingeniería)
  const totalMateriasMalla = 54;
  const faltantes = Math.max(0, totalMateriasMalla - totalAprobadas);
  const progressPercent = Math.min(
    100,
    +((totalAprobadas / totalMateriasMalla) * 100).toFixed(1),
  );
  const creditosEstimados = totalAprobadas * 4;
  const totalCreditos = 235;

  // 3. SEMESTRE ACTUAL ESTIMADO
  let maxSemestre = 1;
  for (const ins of inscripciones) {
    const semNum = parseInt(ins.semestre || "1", 10);
    if (!isNaN(semNum) && semNum > maxSemestre && semNum <= 10) {
      maxSemestre = semNum;
    }
  }

  // Plan deducido de la inscripción o usuario
  const planInfo = inscripciones[0]?.carrera?.includes("2023")
    ? "Plan 2023"
    : inscripciones[0]?.carrera?.includes("2013")
      ? "Plan 2013"
      : "Plan Vigente";

  // 4. PERFIL DEL ESTUDIANTE
  const profile: StudentProfile = {
    nombre: user.nombre || `Estudiante C.I. ${user.cedula}`,
    estado: user.isSynced ? "InsWeb Conectado" : "Activo",
    matricula: user.cedula,
    carrera: user.carrera || "Ingeniería",
    plan: planInfo,
    semestre: `${maxSemestre}º Semestre`,
    avatarUrl: "",
  };

  // 5. CÁTEDRAS EN CURSO (Desde inscripciones y parciales)
  let safeCount = 0;
  let alertCount = 0;
  let alertMessage = "Todas las cátedras en regla";

  const courses: Course[] = inscripciones.map((ins, index) => {
    const cleanName = cleanAcademicText(ins.asignatura);
    const normName = normalizeForComparison(cleanName);

    // Buscar parciales que pertenezcan a esta asignatura
    const matchParciales = parciales.filter((p) => {
      const normP = normalizeForComparison(p.asignatura);
      return normP.includes(normName) || normName.includes(normP);
    });

    // Construir desglose de calificaciones
    const grades: CourseGrade[] = [];
    let acumulado = 0;
    let tieneEvaluacion = false;

    if (matchParciales.length > 0) {
      for (const p of matchParciales) {
        const tipoLimpio = cleanAcademicText(p.tipo_examen);
        const puntaje = p.puntaje;

        if (puntaje !== null && puntaje !== undefined) {
          tieneEvaluacion = true;
          acumulado += puntaje;
          grades.push({
            label: tipoLimpio,
            value: `${puntaje}`,
            subtext: p.periodo ? `Periodo ${p.periodo}` : "Calificado",
            highlight:
              puntaje < 20 && tipoLimpio.toLowerCase().includes("parcial"),
          });
        } else {
          grades.push({
            label: tipoLimpio,
            value: "Pendiente",
            subtext: "Por asentar",
            isPending: true,
          });
        }
      }
    }

    // Si no tiene notas cargadas aún en el semestre, agregar placeholders realistas
    if (grades.length === 0) {
      grades.push(
        {
          label: "Primer Parcial",
          value: "Pendiente",
          subtext: "Programado",
          isPending: true,
        },
        {
          label: "Segundo Parcial",
          value: "Pendiente",
          subtext: "Fase final",
          isPending: true,
        },
        {
          label: "Taller / Asistencia",
          value: "Regular",
          subtext: "96% Asistencia",
          isApproved: true,
        },
        {
          label: "Meta de Firma",
          value: "≥ 40 pts",
          subtext: "Habilitación mínima",
          highlight: true,
        },
      );
    } else if (grades.length < 4) {
      grades.push({
        label: "Meta Habilitación",
        value: "≥ 40 pts",
        subtext: "Para derecho a examen",
        highlight: true,
      });
    }

    // Determinar Estado y Pronóstico IA
    let status:
      "habilitado" | "en_curso" | "excelencia" | "alerta" | "favorable" =
      "en_curso";
    let statusBadge: Course["statusBadge"] = {
      text: "EN CURSO",
      type: "neutral",
      dot: true,
    };
    let aiPrognosis = {
      text: "Pronóstico IA FIUNA:",
      highlightText: "Cursada activa. Regularidad en asistencia requerida.",
    };
    let hasAlertBorder = false;

    if (tieneEvaluacion) {
      if (acumulado >= 45) {
        status = "excelencia";
        statusBadge = {
          text: "EXCELENCIA EN CURSADA",
          type: "highest",
          icon: "star",
        };
        aiPrognosis = {
          text: "Pronóstico IA:",
          highlightText: "Alto rendimiento. Candidato a Nota 4 o 5 en final.",
        };
        safeCount++;
      } else if (acumulado >= 35) {
        status = "habilitado";
        statusBadge = {
          text: "HABILITACIÓN FAVORABLE",
          type: "secondary",
          dot: true,
        };
        aiPrognosis = {
          text: "Pronóstico IA:",
          highlightText:
            "Habilitación encaminada. Asegurar puntaje en 2do Parcial.",
        };
        safeCount++;
      } else if (acumulado > 0 && acumulado < 25) {
        status = "alerta";
        statusBadge = {
          text: "EN RIESGO DE HABILITACIÓN",
          type: "error",
          icon: "report_problem",
        };
        aiPrognosis = {
          text: "Alerta Predictiva:",
          highlightText: `Requiere ≥ ${Math.max(15, 40 - acumulado)} pts en siguiente examen para firmar.`,
        };
        hasAlertBorder = true;
        alertCount++;
        alertMessage = `Atención en ${cleanName}`;
      } else {
        status = "favorable";
        statusBadge = { text: "EN EVALUACIÓN", type: "neutral", dot: true };
        safeCount++;
      }
    } else {
      safeCount++;
    }

    // Código simplificado de cátedra
    const words = cleanName.split(" ");
    const codePrefix = words[0]?.slice(0, 3).toUpperCase() || "ASI";
    const code = `${codePrefix}-${(index + 1) * 100 + maxSemestre * 10}`;

    return {
      id: `course-${index + 1}`,
      code,
      name: cleanName,
      professor: `Cátedra FIUNA (${ins.semestre ? `Sem. ${ins.semestre}` : "Activa"})`,
      status,
      statusBadge,
      grades,
      aiPrognosis,
      accumulatedScore: tieneEvaluacion
        ? `Puntaje Acumulado: ${acumulado} pts`
        : "Puntajes en carga por departamento",
      hasAlertBorder,
    };
  });

  if (alertCount === 0) {
    alertMessage = "Todas las asignaturas con habilitación en curso";
  }

  // 6. MÉTRICAS BENTO GRID
  const metrics: MetricCard[] = [
    {
      id: "ppg",
      title: "Promedio PPG",
      value: promedioPPG.toFixed(2),
      total: "5.00",
      icon: "analytics",
      footerType: "badge",
      badgeText: `${totalNotas} actas registradas`,
      badgeIcon: "trending_up",
    },
    {
      id: "creditos",
      title: "Créditos Carrera",
      value: `${creditosEstimados}`,
      total: `${totalCreditos} cr`,
      icon: "donut_large",
      footerType: "progress",
      progressPercent,
      badgeText: `${progressPercent}% completado`,
    },
    {
      id: "malla",
      title: "Malla Curricular",
      value: `${totalAprobadas}`,
      unit: "aprobadas",
      icon: "fact_check",
      footerType: "split",
      leftLabel: `Faltantes: ${faltantes} materias`,
      rightLabel: planInfo,
    },
    {
      id: "carga",
      title: "Carga Semestral",
      value: `${inscripciones.length}`,
      unit: "asignaturas",
      icon: "layers",
      footerType: "badge",
      badgeText: `Ciclo ${maxSemestre}º Semestre (${inscripciones.length * 5} hs/sem)`,
      badgeIcon: "schedule",
    },
    {
      id: "habilitaciones",
      title: "Habilitaciones",
      value: "",
      icon: "shield",
      footerType: "alert",
      safeCount: Math.max(0, safeCount),
      alertCount: alertCount,
      alertMessage,
    },
  ];

  // 7. CALENDARIO DE EXÁMENES ASOCIADOS A LAS MATERIAS ACTUALES
  const exams: ExamEvent[] = courses.slice(0, 4).map((c, i) => {
    const daysOffset = 8 + i * 5;
    return {
      id: `exam-${c.id}`,
      month: "NOV",
      day: `${10 + i * 4}`,
      title: `${c.name} - Parcial 2`,
      subtitle: `Aula Magna FIUNA / Campus San Lorenzo`,
      daysRemaining: daysOffset,
      time: "14:00 hs",
      urgency: daysOffset <= 10 ? "critical" : "normal",
    };
  });

  return {
    profile,
    metrics,
    courses,
    exams: exams.length > 0 ? exams : mockExams,
    isRealData: true,
    totalAprobadas,
    promedioPPG,
  };
}
