export interface SubjectSimulation {
  id: string;
  name: string;
  catedra: string;
  professor: string;
  p1: number | null;
  p1Max: number;
  p1Date: string;
  p1ClassAverage: number;
  p2: number | null;
  p2Max: number;
  hasLab: boolean;
  lab: number | null;
  labMax: number;
  labLabel?: string;
  labSessionsEvaluated: number;
  labPendingDeliveries: number;
  defaultP2: number;
  hasOfficialWeights: boolean;
  attendanceRate: number;
  attendedSessions: number;
  totalSessions: number;
  attendanceArticle: string;
  criticalTopic: string;
  historicalInsight: string;
}

export interface ChatMessage {
  id: string;
  sender: "user" | "assistant";
  text: string;
  timestamp: string;
  alertBox?: {
    text: string;
    type: "warning" | "info";
  };
  actionButton?: {
    label: string;
    targetP2: number;
  };
  recommendationCard?: {
    title: string;
    text: string;
    highlightPrimary?: string;
    highlightSecondary?: string;
  };
}
