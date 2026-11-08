import type {
  AcademicRecord,
  HistoryStatsData,
  SemesterCurriculumBlock,
  AcademicStatus,
} from "../types/academic-history";
import type { EstudianteSummary, NotaFinalData, InscripcionData } from "./scraper";
import {
  historyStats as mockHistoryStats,
  academicRecords as mockAcademicRecords,
  curriculumBlocks as mockCurriculumBlocks,
} from "../data/academic-history-mock";

export interface HistoryDataResult {
  stats: HistoryStatsData;
  records: AcademicRecord[];
  curriculumBlocks: SemesterCurriculumBlock[];
  isRealData: boolean;
  estudianteNombre?: string;
  cedula?: string;
  carrera?: string;
  totalActas: number;
}

interface UserLike {
  nombre?: string;
  cedula?: string;
  carrera?: string;
  isSynced?: boolean;
}

/**
 * Determina el departamento académico FIUNA en base al nombre de la asignatura.
 */
function inferirDepartamento(nombre: string): {
  dept: "MAT" | "FIS" | "MEC" | "ELE" | "HUM";
  deptName: string;
} {
  const n = nombre.toUpperCase();
  if (
    n.includes("CALCULO") ||
    n.includes("CÁLCULO") ||
    n.includes("ALGEBRA") ||
    n.includes("ÁLGEBRA") ||
    n.includes("GEOMETRIA") ||
    n.includes("GEOMETRÍA") ||
    n.includes("PROBABILIDAD") ||
    n.includes("NUMERICOS") ||
    n.includes("NUMÉRICOS") ||
    n.includes("MATEMATICA") ||
    n.includes("MATEMÁTICA")
  ) {
    return { dept: "MAT", deptName: "Ciencias Matemáticas" };
  }

  if (
    n.includes("FISICA") ||
    n.includes("FÍSICA") ||
    n.includes("ESTATICA") ||
    n.includes("ESTÁTICA") ||
    n.includes("DINAMICA") ||
    n.includes("DINÁMICA") ||
    n.includes("QUIMICA") ||
    n.includes("QUÍMICA") ||
    n.includes("CALOR")
  ) {
    return { dept: "FIS", deptName: "Física y Termodinámica" };
  }

  if (
    n.includes("MECANICA") ||
    n.includes("MECÁNICA") ||
    n.includes("MATERIALES") ||
    n.includes("DIBUJO") ||
    n.includes("ELEMENTOS") ||
    n.includes("ESTRUCTURAS") ||
    n.includes("HIDRAULICA") ||
    n.includes("MÁQUINAS")
  ) {
    return { dept: "MEC", deptName: "Ingeniería Mecánica & Aplicada" };
  }

  if (
    n.includes("HUMANIDADES") ||
    n.includes("ADMINISTRACION") ||
    n.includes("ADMINISTRACIÓN") ||
    n.includes("ECONOMIA") ||
    n.includes("ECONOMÍA") ||
    n.includes("SEGURIDAD") ||
    n.includes("AMBIENTAL") ||
    n.includes("CONTABILIDAD") ||
    n.includes("FINANZAS") ||
    n.includes("LEGISLACION") ||
    n.includes("LEGISLACIÓN")
  ) {
    return { dept: "HUM", deptName: "Humanidades y Gestión" };
  }

  return { dept: "ELE", deptName: "Ingeniería Eléctrica & Computación" };
}

/**
 * Deriva el código de cátedra normalizado.
 */
function generarCodigoMateria(nombre: string, index: number): string {
  const palabras = nombre.trim().toUpperCase().split(/\s+/);
  if (palabras.length === 1) {
    return palabras[0].slice(0, 3) + String(10 + index);
  }
  const prefix = palabras.map((p) => p[0]).join("").slice(0, 3);
  return `${prefix}${String(index + 1).padStart(2, "0")}`;
}

/**
 * Extrae el periodo lectivo a partir de la fecha de acta (DD/MM/AAAA o similar).
 */
function inferirPeriodo(fechaStr?: string): string {
  if (!fechaStr) return "2024-2";
  const partes = fechaStr.split(/[/ -]/);
  if (partes.length >= 3) {
    const anho = partes.find((p) => p.length === 4) || partes[2];
    const mes = parseInt(partes[1], 10) || 6;
    const ciclo = mes <= 7 ? "1" : "2";
    return `${anho}-${ciclo}`;
  }
  return fechaStr;
}

/**
 * Transforma los registros scrapeados oficiales de INSWEB (notas e inscripciones en SQLite)
 * a las estructuras de interfaz de la vista Historial y Malla Curricular.
 */
export function buildHistoryData(
  studentData: EstudianteSummary | null,
  user: UserLike | null,
): HistoryDataResult {
  // Fallback a mock si no hay datos oficiales
  if (
    !studentData ||
    (!studentData.notas?.length && !studentData.inscripciones?.length)
  ) {
    return {
      stats: mockHistoryStats,
      records: mockAcademicRecords,
      curriculumBlocks: mockCurriculumBlocks,
      isRealData: false,
      totalActas: 0,
    };
  }

  const notas = studentData.notas || [];
  const inscripciones = studentData.inscripciones || [];

  // 1. Mapeo de notas finales oficiales
  const records: AcademicRecord[] = [];
  const materiasAprobadasSet = new Set<string>();
  const materiasNotasMap = new Map<string, number>();

  notas.forEach((nota, idx) => {
    const nombreNorm = nota.asignatura.trim();
    const esAprobada = Boolean(nota.aprobado && nota.nota && nota.nota >= 2);
    if (esAprobada) {
      materiasAprobadasSet.add(nombreNorm.toUpperCase());
    }
    if (nota.nota !== undefined && nota.nota !== null) {
      materiasNotasMap.set(nombreNorm.toUpperCase(), nota.nota);
    }

    const { dept, deptName } = inferirDepartamento(nombreNorm);
    const code = generarCodigoMateria(nombreNorm, idx);
    const period = inferirPeriodo(nota.fecha);
    const status: AcademicStatus = esAprobada ? "APROBADA" : "PENDIENTE";

    const creditos = 5; // Créditos promedio por asignatura en FIUNA

    records.push({
      code,
      name: nombreNorm,
      department: dept,
      departmentName: deptName,
      semester: `Acta ${nota.nro_acta || (idx + 1)}`,
      grade: typeof nota.nota === "number" ? nota.nota : null,
      opportunity: nota.tipo || (nota.nota === 1 ? "Extraordinaria" : "1ra Convocatoria"),
      credits: creditos,
      period,
      actaNumber: nota.nro_acta ? `#${nota.nro_acta}` : `Acta ${idx + 1}`,
      status,
      prerequisites: ["Plan de Correlativas FIUNA"],
      unlocks: ["Asignaturas de Ciclos Posteriores"],
      aiInsight: {
        text: esAprobada
          ? `Asignatura oficial aprobada con Nota ${nota.nota} según Acta InsWeb #${nota.nro_acta || "S/N"}.`
          : `Asignatura con registro de examen rendido (${nota.nota_literal || "Pendiente"}).`,
        projectedUnlock: esAprobada ? `Convalidada en ${period}` : "Pendiente de Regularización",
        probability: esAprobada ? "100%" : "En proceso",
      },
    });
  });

  // 2. Mapeo de asignaturas en curso activas
  inscripciones.forEach((ins, idx) => {
    const nombreNorm = ins.asignatura.trim();
    const { dept, deptName } = inferirDepartamento(nombreNorm);
    const code = generarCodigoMateria(nombreNorm, 50 + idx);
    const semestreStr = ins.semestre ? `${ins.semestre}° Sem` : "En Curso";

    records.unshift({
      code,
      name: nombreNorm,
      department: dept,
      departmentName: deptName,
      semester: semestreStr,
      grade: null,
      opportunity: "Cursando Ciclo Actual",
      credits: 5,
      period: "2024-2",
      actaNumber: "En Proceso",
      status: "CURSO",
      prerequisites: ["Habilitación previa en sistema"],
      unlocks: ["Siguiente semestre de la malla"],
      aiInsight: {
        text: `Materia matriculada en el ciclo lectivo activo (${ins.carrera || "Ingeniería"}).`,
        projectedUnlock: "Próximo Periodo Ordinario",
        probability: "En desarrollo",
      },
    });
  });

  // 3. Cálculo de métricas académicas oficiales
  const totalMallaCarrera = 54; // Carga total típica de un plan de ingeniería FIUNA
  const notasNumericas = notas
    .map((n) => n.nota)
    .filter((n): n is number => typeof n === "number" && n >= 1 && n <= 5);

  const sumaNotas = notasNumericas.reduce((acc, curr) => acc + curr, 0);
  const promedioPPG = notasNumericas.length > 0 ? Number((sumaNotas / notasNumericas.length).toFixed(2)) : 0.0;

  const approvedCount = materiasAprobadasSet.size;
  const inProgressCount = inscripciones.length;
  const approvedPercentage = Number(
    ((approvedCount / totalMallaCarrera) * 100).toFixed(1),
  );
  const pendingCount = Math.max(0, totalMallaCarrera - approvedCount - inProgressCount);
  const inProgressCredits = inProgressCount * 5;

  const deltaNum = (promedioPPG - 3.2).toFixed(2);
  const deltaCohort = `${Number(deltaNum) >= 0 ? "+" : ""}${deltaNum} vs Cohorte Histórica FIUNA`;

  const stats: HistoryStatsData = {
    totalSubjects: totalMallaCarrera,
    approvedCount,
    approvedPercentage,
    inProgressCount,
    inProgressCredits,
    pendingCount,
    averageGrade: promedioPPG,
    deltaCohort,
  };

  // 4. Adaptación de la malla curricular con los datos reales
  const curriculumBlocks: SemesterCurriculumBlock[] = mockCurriculumBlocks.map(
    (block) => {
      const updatedCourses = block.courses.map((course) => {
        const cNameUpper = course.name.toUpperCase();
        // Buscar si esta materia de la malla coincide con las notas o inscripciones reales
        const notaEncontrada = notas.find((n) =>
          n.asignatura.toUpperCase().includes(cNameUpper) ||
          cNameUpper.includes(n.asignatura.toUpperCase()),
        );

        if (notaEncontrada && notaEncontrada.aprobado && notaEncontrada.nota && notaEncontrada.nota >= 2) {
          return {
            ...course,
            status: "APROBADA" as const,
            gradeText: `Aprobada • Nota ${notaEncontrada.nota}`,
          };
        }

        const enCurso = inscripciones.find((i) =>
          i.asignatura.toUpperCase().includes(cNameUpper) ||
          cNameUpper.includes(i.asignatura.toUpperCase()),
        );

        if (enCurso) {
          return {
            ...course,
            status: "CURSO" as const,
            gradeText: "En curso • Periodo Activo",
          };
        }

        return course;
      });

      return {
        ...block,
        courses: updatedCourses,
      };
    },
  );

  return {
    stats,
    records,
    curriculumBlocks,
    isRealData: true,
    estudianteNombre: user?.nombre || studentData.cedula,
    cedula: studentData.cedula,
    carrera: user?.carrera || inscripciones[0]?.carrera || "Ingeniería",
    totalActas: notas.length,
  };
}

