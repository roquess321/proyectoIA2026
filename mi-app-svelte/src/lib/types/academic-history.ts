export type AcademicStatus = "APROBADA" | "CURSO" | "PENDIENTE";

export interface PrerequisiteDetail {
  code: string;
  name: string;
  statusText: string;
  statusType: "approved" | "in_progress" | "pending";
}

export interface AcademicRecord {
  code: string;
  name: string;
  department: "MAT" | "FIS" | "MEC" | "ELE" | "HUM";
  departmentName: string;
  semester: string;
  grade: number | null;
  opportunity: string;
  credits: number;
  period: string;
  actaNumber: string;
  status: AcademicStatus;
  prerequisites: string[];
  unlocks: string[];
  aiInsight?: {
    text: string;
    projectedUnlock: string;
    probability: string;
  };
}

export interface HistoryStatsData {
  totalSubjects: number;
  approvedCount: number;
  approvedPercentage: number;
  inProgressCount: number;
  inProgressCredits: number;
  pendingCount: number;
  averageGrade: number;
  deltaCohort: string;
}

export interface CurriculumCourse {
  code: string;
  name: string;
  status: "APROBADA" | "CURSO" | "HABILITADA" | "BLOQUEADA";
  gradeText?: string;
  credits?: number;
  note?: string;
}

export interface SemesterCurriculumBlock {
  semesterName: string;
  credits: number;
  courses: CurriculumCourse[];
}
