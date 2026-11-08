<script lang="ts">
	import { onMount } from "svelte";
	import { academicState } from "../../academic-state.svelte";
	import { authState } from "../../auth-state.svelte";
	import { getEstudiante, type EstudianteSummary } from "../../services/scraper";
	import { buildDashboardData, type DashboardData } from "../../services/dashboard-stats";
	import StatusBanner from "./StatusBanner.svelte";
	import StatCards from "./StatCards.svelte";
	import CourseTracker from "./CourseTracker.svelte";
	import ExamCalendar from "./ExamCalendar.svelte";
	import AiCopilotCard from "./AiCopilotCard.svelte";
	import NoticeCard from "./NoticeCard.svelte";

	let isLoading = $state(false);
	let loadError = $state<string | null>(null);
	let studentData = $state<EstudianteSummary | null>(null);

	const user = $derived(authState.user);

	async function loadStudentStats(): Promise<void> {
		if (!user?.cedula) {
			studentData = null;
			return;
		}

		isLoading = true;
		loadError = null;
		try {
			studentData = await getEstudiante(user.cedula);
		} catch (err: unknown) {
			console.warn("No se pudieron cargar estadísticas académicas desde backend:", err);
			studentData = null;
			loadError = err instanceof Error ? err.message : "Error al conectar con la base de datos";
		} finally {
			isLoading = false;
		}
	}

	onMount(() => {
		academicState.activeNav = "dashboard";
		if (user?.cedula) {
			loadStudentStats();
		}
	});

	$effect(() => {
		// Reaccionar cuando cambie la cédula o el estado de sesión
		if (user?.cedula) {
			loadStudentStats();
		} else {
			studentData = null;
		}
	});

	let dashboard: DashboardData = $derived(buildDashboardData(studentData, user));
</script>

<svelte:head>
	<title>Dashboard Académico - FIUNA Academic AI Suite</title>
</svelte:head>

<div class="flex flex-col w-full gap-space-lg">
	<!-- Banner de Estado Académico y Datos del Alumno -->
	<StatusBanner profile={dashboard.profile} />

	{#if isLoading}
		<div
			class="p-space-sm rounded-xl bg-surface-container-low border border-primary/20 flex items-center justify-between text-on-surface-variant font-label-sm text-label-sm animate-pulse"
		>
			<div class="flex items-center gap-2">
				<span class="material-symbols-outlined text-primary text-base animate-spin">sync</span>
				<span>Consultando récords académicos y evaluaciones en base de datos SQLite...</span>
			</div>
			<span class="font-code-num text-xs bg-surface-container px-2 py-0.5 rounded font-semibold text-primary">
				copilot.db
			</span>
		</div>
	{/if}

	{#if !authState.isLoggedIn}
		<!-- Alerta: Modo Demostración -->
		<div
			class="rounded-xl p-space-md bg-surface-container-lowest border border-amber-500/30 shadow-sm flex flex-col sm:flex-row sm:items-center justify-between gap-space-md"
		>
			<div class="flex items-center gap-space-sm">
				<div class="w-10 h-10 rounded-lg bg-amber-500/10 flex items-center justify-center text-amber-500 shrink-0">
					<span class="material-symbols-outlined text-xl">vpn_key_alert</span>
				</div>
				<div class="flex flex-col">
					<span class="font-label-md text-label-md font-bold text-on-surface">
						Modo Demostración Activo (Datos Simulados)
					</span>
					<span class="font-body-sm text-body-sm text-on-surface-variant">
						Inicia sesión con tu cuenta y vincula tu C.I. para ver tus estadísticas reales extraídas de InsWeb.
					</span>
				</div>
			</div>
			<a
				href="/"
				class="px-space-md py-2 bg-primary text-on-primary rounded font-label-md text-label-md font-semibold hover:bg-primary-container transition-colors shrink-0 flex items-center gap-1 self-start sm:self-auto"
				onclick={() => (academicState.activeNav = "acceso-insweb")}
			>
				<span class="material-symbols-outlined text-base">sync_alt</span>
				Iniciar Sesión
			</a>
		</div>
	{:else if user && !user.isSynced}
		<!-- Alerta: Cuenta local activa pero sin sincronizar con InsWeb -->
		<div
			class="rounded-xl p-space-md bg-surface-container-lowest border border-amber-500/40 shadow-sm flex flex-col sm:flex-row sm:items-center justify-between gap-space-md"
		>
			<div class="flex items-center gap-space-sm">
				<div class="w-10 h-10 rounded-lg bg-amber-500/10 flex items-center justify-center text-amber-500 shrink-0">
					<span class="material-symbols-outlined text-xl">pending_actions</span>
				</div>
				<div class="flex flex-col">
					<span class="font-label-md text-label-md font-bold text-on-surface">
						Pendiente de Vinculación InsWeb
					</span>
					<span class="font-body-sm text-body-sm text-on-surface-variant">
						Tu cuenta local está registrada. Ingresa tu PIN de InsWeb en el portal de acceso para extraer tus calificaciones y materias oficiales.
					</span>
				</div>
			</div>
			<a
				href="/"
				class="px-space-md py-2 bg-primary text-on-primary rounded font-label-md text-label-md font-semibold hover:bg-primary-container transition-colors shrink-0 flex items-center gap-1 self-start sm:self-auto"
				onclick={() => (academicState.activeNav = "acceso-insweb")}
			>
				<span class="material-symbols-outlined text-base">cloud_sync</span>
				Vincular InsWeb
			</a>
		</div>
	{:else if dashboard.isRealData}
		<!-- Badge Informativo de Datos Reales Sincronizados -->
		<div
			class="rounded-xl p-space-md bg-surface-container-lowest border border-emerald-500/30 shadow-sm flex flex-col sm:flex-row sm:items-center justify-between gap-space-md"
		>
			<div class="flex items-center gap-space-sm">
				<div class="w-10 h-10 rounded-lg bg-emerald-500/10 flex items-center justify-center text-emerald-600 dark:text-emerald-400 shrink-0">
					<span class="material-symbols-outlined text-xl">verified</span>
				</div>
				<div class="flex flex-col">
					<div class="flex items-center gap-2">
						<span class="font-label-md text-label-md font-bold text-on-surface">
							Récord Académico Oficial Sincronizado
						</span>
						<span class="px-2 py-0.5 rounded bg-emerald-500/15 text-emerald-700 dark:text-emerald-300 font-code-num text-xs font-semibold">
							C.I. {user?.cedula}
						</span>
					</div>
					<span class="font-body-sm text-body-sm text-on-surface-variant">
						{dashboard.totalAprobadas} materias aprobadas registradas • Promedio general PPG: <strong class="text-on-surface">{dashboard.promedioPPG}</strong> • {dashboard.courses.length} asignaturas matriculadas
					</span>
				</div>
			</div>

			<div class="flex items-center gap-2 self-start sm:self-auto">
				<button
					type="button"
					class="px-3 py-1.5 rounded-lg border border-outline-variant hover:bg-surface-container text-on-surface font-label-sm text-label-sm flex items-center gap-1 transition-colors"
					onclick={() => loadStudentStats()}
					title="Actualizar datos desde la base de datos"
				>
					<span class="material-symbols-outlined text-base {isLoading ? 'animate-spin' : ''}">refresh</span>
					Actualizar
				</button>
				<a
					href="/"
					class="px-3 py-1.5 rounded-lg bg-surface-container-low hover:bg-surface-container text-primary font-label-sm text-label-sm flex items-center gap-1 transition-colors font-semibold"
					onclick={() => (academicState.activeNav = "acceso-insweb")}
				>
					<span class="material-symbols-outlined text-base">sync</span>
					Re-sincronizar InsWeb
				</a>
			</div>
		</div>
	{/if}

	<!-- Bento Grid de Métricas Clave (PPG, Créditos, Malla, Carga, Habilitaciones) -->
	<StatCards metrics={dashboard.metrics} />

	<!-- Grilla Principal: Seguimiento de Cátedras en Curso y Calendario -->
	<div class="grid grid-cols-1 lg:grid-cols-12 gap-space-lg items-start">
		<!-- Izquierda: Cátedras Matriculadas Reales / En Curso (8 Cols) -->
		<div class="lg:col-span-8">
			<CourseTracker courses={dashboard.courses} />
		</div>

		<!-- Derecha: Calendario de Evaluaciones, Copiloto IA y Avisos (4 Cols) -->
		<div class="lg:col-span-4 flex flex-col gap-space-md">
			<ExamCalendar exams={dashboard.exams} />
			<AiCopilotCard />
			<NoticeCard />
		</div>
	</div>
</div>
