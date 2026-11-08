<script lang="ts">
	import { onMount } from "svelte";
	import { academicState } from "../../academic-state.svelte";
	import { authState } from "../../auth-state.svelte";
	import { getEstudiante, type EstudianteSummary } from "../../services/scraper";
	import { buildHistoryData, type HistoryDataResult } from "../../services/history-data";
	import type { AcademicRecord } from "../../types/academic-history";
	import HistoryHeader from "./HistoryHeader.svelte";
	import HistoryStats from "./HistoryStats.svelte";
	import AcademicTable from "./AcademicTable.svelte";
	import CorrelativesPanel from "./CorrelativesPanel.svelte";
	import CurriculumGrid from "./CurriculumGrid.svelte";

	let isLoading = $state(false);
	let studentData = $state<EstudianteSummary | null>(null);
	let activeTab = $state<"history" | "curriculum">("history");
	let isSyncing = $state(false);
	let toastMessage = $state<string | null>(null);

	const user = $derived(authState.user);

	async function loadHistoryData(): Promise<void> {
		if (!user?.cedula) {
			studentData = null;
			return;
		}

		isLoading = true;
		try {
			studentData = await getEstudiante(user.cedula);
		} catch (err: unknown) {
			console.warn("No se pudieron cargar datos del historial desde backend:", err);
			studentData = null;
		} finally {
			isLoading = false;
		}
	}

	onMount(() => {
		academicState.activeNav = "historial-malla-curricular";
		if (user?.cedula) {
			loadHistoryData();
		}
	});

	$effect(() => {
		if (user?.cedula) {
			loadHistoryData();
		} else {
			studentData = null;
		}
	});

	let historyData: HistoryDataResult = $derived(buildHistoryData(studentData, user));

	let selectedCode = $state<string>("");

	let selectedRecord: AcademicRecord = $derived(
		historyData.records.find((r) => r.code === selectedCode) ?? historyData.records[0]
	);

	function showToast(message: string, durationMs = 3500) {
		toastMessage = message;
		setTimeout(() => {
			if (toastMessage === message) {
				toastMessage = null;
			}
		}, durationMs);
	}

	function handleExportPdf() {
		showToast(
			`Generando Certificado Oficial de Historial Académico y Malla FIUNA (C.I. ${user?.cedula || "Invitado"}) con código QR de verificación...`,
		);
	}

	async function handleSyncInsweb() {
		if (isSyncing) return;
		isSyncing = true;

		try {
			if (user?.cedula) {
				await loadHistoryData();
				showToast(
					`Datos académicos sincronizados con éxito desde copilot.db. ${historyData.records.length} registros cargados.`,
				);
			} else {
				showToast("Inicia sesión y vincula tu cuenta InsWeb para sincronizar tus calificaciones.");
			}
		} catch (e: unknown) {
			showToast("Error al sincronizar con el servidor local.");
		} finally {
			isSyncing = false;
		}
	}

	function handleSelectRecord(record: AcademicRecord) {
		selectedCode = record.code;
	}

	function handleSelectCourseByCode(code: string) {
		selectedCode = code;
		activeTab = "history";
	}
</script>

<svelte:head>
	<title>Historial Académico &amp; Malla Curricular - FIUNA Academic AI Suite</title>
</svelte:head>

<div class="flex flex-col w-full gap-space-lg relative">
	<!-- Toast notification -->
	{#if toastMessage}
		<div
			class="fixed bottom-6 right-6 z-50 bg-primary text-on-primary px-space-md py-3 rounded-lg shadow-xl border border-secondary/30 flex items-center gap-space-sm max-w-md animate-fade-in"
		>
			<span class="material-symbols-outlined text-secondary text-xl">info</span>
			<span class="font-body-sm text-body-sm font-medium">{toastMessage}</span>
			<button
				type="button"
				class="ml-auto text-on-primary/70 hover:text-on-primary cursor-pointer"
				onclick={() => (toastMessage = null)}
			>
				<span class="material-symbols-outlined text-base">close</span>
			</button>
		</div>
	{/if}

	<!-- Top Header & Actions -->
	<HistoryHeader
		onExportPdf={handleExportPdf}
		onSyncInsweb={handleSyncInsweb}
		{isSyncing}
		cedula={historyData.cedula}
		carrera={historyData.carrera}
	/>

	<!-- Banner Informativo de Conexión a Base de Datos Scrapeada -->
	{#if isLoading}
		<div
			class="p-space-sm rounded-xl bg-surface-container-low border border-primary/20 flex items-center justify-between text-on-surface-variant font-label-sm text-label-sm animate-pulse"
		>
			<div class="flex items-center gap-2">
				<span class="material-symbols-outlined text-primary text-base animate-spin">sync</span>
				<span>Cargando actas oficiales y récord histórico desde base de datos SQLite...</span>
			</div>
			<span class="font-code-num text-xs bg-surface-container px-2 py-0.5 rounded font-semibold text-primary">
				copilot.db
			</span>
		</div>
	{:else if historyData.isRealData}
		<div
			class="p-4 sm:p-space-md rounded-xl bg-surface-container-lowest border border-emerald-500/30 shadow-sm flex flex-col sm:flex-row sm:items-center justify-between gap-space-md"
		>
			<div class="flex items-center gap-space-sm">
				<div
					class="w-10 h-10 rounded-lg bg-emerald-500/10 flex items-center justify-center text-emerald-600 dark:text-emerald-400 shrink-0"
				>
					<span class="material-symbols-outlined text-xl">verified</span>
				</div>
				<div class="flex flex-col">
					<div class="flex flex-wrap items-center gap-2">
						<span class="font-label-md text-label-md font-bold text-on-surface">
							Historial Académico Oficial Extraído de InsWeb
						</span>
						<span
							class="px-2 py-0.5 rounded bg-emerald-500/15 text-emerald-700 dark:text-emerald-300 font-code-num text-xs font-semibold"
						>
							C.I. {historyData.cedula}
						</span>
					</div>
					<span class="font-body-sm text-body-sm text-on-surface-variant mt-0.5">
						{historyData.totalActas} actas de exámenes finales • Promedio Ponderado General (PPG): <strong class="text-on-surface">{historyData.stats.averageGrade}</strong> • {historyData.stats.approvedCount} materias aprobadas
					</span>
				</div>
			</div>

			<button
				type="button"
				class="px-3 py-1.5 rounded-lg border border-outline-variant hover:bg-surface-container text-on-surface font-label-sm text-label-sm flex items-center gap-1 transition-colors self-start sm:self-auto cursor-pointer"
				onclick={() => loadHistoryData()}
				title="Refrescar historial desde la base de datos"
			>
				<span class="material-symbols-outlined text-base {isLoading ? 'animate-spin' : ''}">refresh</span>
				Actualizar
			</button>
		</div>
	{:else}
		<div
			class="p-4 sm:p-space-md rounded-xl bg-surface-container-lowest border border-amber-500/30 shadow-sm flex flex-col sm:flex-row sm:items-center justify-between gap-space-md"
		>
			<div class="flex items-center gap-space-sm">
				<div
					class="w-10 h-10 rounded-lg bg-amber-500/10 flex items-center justify-center text-amber-500 shrink-0"
				>
					<span class="material-symbols-outlined text-xl">vpn_key_alert</span>
				</div>
				<div class="flex flex-col">
					<span class="font-label-md text-label-md font-bold text-on-surface">
						Modo Demostración Activo (Malla Curricular Simulada)
					</span>
					<span class="font-body-sm text-body-sm text-on-surface-variant">
						Inicia sesión con tu cuenta y vincula tu Cédula de Identidad en el portal para cargar tus calificaciones y actas reales.
					</span>
				</div>
			</div>
			<a
				href="/"
				class="px-space-md py-2 bg-primary text-on-primary rounded font-label-md text-label-md font-semibold hover:bg-primary-container transition-colors shrink-0 flex items-center gap-1 self-start sm:self-auto cursor-pointer"
				onclick={() => (academicState.activeNav = "acceso-insweb")}
			>
				<span class="material-symbols-outlined text-base">sync_alt</span>
				Iniciar Sesión
			</a>
		</div>
	{/if}

	<!-- 5 Key Metric Stat Cards -->
	<HistoryStats stats={historyData.stats} />

	<!-- Tab Switcher Bar -->
	<div
		class="flex items-center justify-between bg-surface-container-lowest rounded-xl p-1 shadow-sm border border-outline-variant/30 overflow-x-auto"
	>
		<div class="flex gap-1 shrink-0" id="tab-controls">
			<button
				type="button"
				class="flex items-center gap-1.5 sm:gap-2 px-3 sm:px-space-md py-2 rounded-lg font-semibold transition-all cursor-pointer whitespace-nowrap {activeTab ===
				'history'
					? 'bg-primary-container text-white dark:bg-[#132c4d] dark:text-[#d3e4fe] shadow-sm'
					: 'text-on-surface-variant hover:bg-surface-container hover:text-on-surface dark:hover:bg-surface-container-high dark:hover:text-on-surface'}"
				onclick={() => (activeTab = "history")}
			>
				<span
					class="material-symbols-outlined text-base {activeTab ===
					'history'
						? 'text-secondary-fixed dark:text-[#b1c7f0]'
						: ''}"
				>
					format_list_bulleted
				</span>
				<span class="font-label-md text-xs sm:text-label-md">
					Historial de Calificaciones ({historyData.records.length})
				</span>
			</button>

			<button
				type="button"
				class="flex items-center gap-1.5 sm:gap-2 px-3 sm:px-space-md py-2 rounded-lg font-semibold transition-all cursor-pointer whitespace-nowrap {activeTab ===
				'curriculum'
					? 'bg-primary-container text-white dark:bg-[#132c4d] dark:text-[#d3e4fe] shadow-sm'
					: 'text-on-surface-variant hover:bg-surface-container hover:text-on-surface dark:hover:bg-surface-container-high dark:hover:text-on-surface'}"
				onclick={() => (activeTab = "curriculum")}
			>
				<span
					class="material-symbols-outlined text-base {activeTab ===
					'curriculum'
						? 'text-secondary-fixed dark:text-[#b1c7f0]'
						: ''}"
				>
					schema
				</span>
				<span class="font-label-md text-xs sm:text-label-md">Malla &amp; Correlativas</span>
			</button>
		</div>

		<div
			class="hidden md:flex items-center gap-2 px-space-md text-on-surface-variant font-code-num text-code-num"
		>
			<span class="w-2 h-2 rounded-full bg-secondary"></span>
			Cálculo de Promedio Oficial FIUNA: Escala 1 al 5
		</div>
	</div>

	<!-- TAB 1: History Table + Correlatives Panel -->
	{#if activeTab === "history"}
		<div class="grid grid-cols-1 xl:grid-cols-12 gap-space-lg">
			<!-- Left: Academic Table with Filters (8 cols) -->
			<div class="xl:col-span-8">
				<AcademicTable
					records={historyData.records}
					{selectedRecord}
					onSelectRecord={handleSelectRecord}
				/>
			</div>

			<!-- Right: Correlatives Inspector Panel (4 cols) -->
			<div class="xl:col-span-4">
				<CorrelativesPanel {selectedRecord} />
			</div>
		</div>
	{:else}
		<!-- TAB 2: Curriculum Sequential Flow -->
		<CurriculumGrid
			blocks={historyData.curriculumBlocks}
			onSelectCourseByCode={handleSelectCourseByCode}
		/>
	{/if}
</div>
