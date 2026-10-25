export interface NavItem {
  path: string;
  href: string;
  icon: string;
  title: string;
  subtitle: string;
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
  latency = $state(48);
  pipelineStatus = $state("5 de 5 Fases Completadas");
  activeNav = $state("acceso-insweb");

  forceRescrape(): void {
    if (this.isRescraping) return;
    this.isRescraping = true;
    this.pipelineStatus = "Sincronizando con InsWeb...";

    setTimeout(() => {
      this.isRescraping = false;
      this.latency = Math.floor(Math.random() * (65 - 42 + 1)) + 42;
      this.pipelineStatus = "5 de 5 Fases Completadas (Recién)";
    }, 1200);
  }
}

export const academicState = new AcademicState();
