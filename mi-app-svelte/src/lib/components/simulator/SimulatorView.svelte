<script lang="ts">
	import { onMount } from 'svelte';
	import { academicState } from '../../academic-state.svelte';
	import { authState } from '../../auth-state.svelte';
	import { getEstudiante, type EstudianteSummary } from '../../services/scraper';
	import { buildSimulatorSubjects, type SimulatorData } from '../../services/simulator-data';
	import type { SubjectSimulation } from '../../types/simulator';
	import PredictiveHeader from './PredictiveHeader.svelte';
	import GaugeChart from './GaugeChart.svelte';
	import EvaluationMatrix from './EvaluationMatrix.svelte';
	import FinalExamScenarios from './FinalExamScenarios.svelte';
	import AiCopilotChat from './AiCopilotChat.svelte';

	let isLoading = $state(false);
	let studentData = $state<EstudianteSummary | null>(null);

	const user = $derived(authState.user);

	async function loadStudentData(): Promise<void> {
		if (!user?.cedula) {
			studentData = null;
			return;
		}

		isLoading = true;
		try {
			studentData = await getEstudiante(user.cedula);
		} catch (err: unknown) {
			console.warn('No se pudieron obtener materias para el simulador:', err);
			studentData = null;
		} finally {
			isLoading = false;
		}
	}

	onMount(() => {
		academicState.activeNav = 'agente-ia-pronosticos';
		if (user?.cedula) {
			loadStudentData();
		}
	});

	$effect(() => {
		if (user?.cedula) {
			loadStudentData();
		} else {
			studentData = null;
		}
	});

	let simData: SimulatorData = $derived(buildSimulatorSubjects(studentData, user));

	let selectedSubjectId = $state<string>('');
	let p2Value = $state<number>(14);

	// Mantener sincronizada la materia seleccionada cuando cambien los datos o se carguen las materias reales
	$effect(() => {
		if (simData.subjects.length > 0) {
			const found = simData.subjects.find((s) => s.id === selectedSubjectId);
			if (!found) {
				selectedSubjectId = simData.subjects[0].id;
				p2Value = simData.subjects[0].defaultP2;
			}
		}
	});

	let currentSubject: SubjectSimulation = $derived(
		simData.subjects.find((s) => s.id === selectedSubjectId) ?? simData.subjects[0]
	);

	function handleSubjectChange(newId: string) {
		selectedSubjectId = newId;
		const found = simData.subjects.find((s) => s.id === newId);
		if (found) {
			p2Value = found.defaultP2;
		}
	}

	function handleSetP2(val: number) {
		p2Value = val;
	}

	// Cálculos predictivos derivados en tiempo real
	let totalProcess = $derived(currentSubject.p1 + p2Value + currentSubject.lab);

	let probability = $derived(
		Math.max(10, Math.min(96, Math.round(15 + (totalProcess / 50) * 82)))
	);
</script>

<svelte:head>
	<title>Simulador Predictivo &amp; Agente IA - FIUNA Academic AI Suite</title>
</svelte:head>

<div class="flex flex-col w-full gap-space-lg">
	<!-- Banner Informativo del Estado de la Base de Datos -->
	{#if isLoading}
		<div
			class="p-space-sm rounded-xl bg-surface-container-low border border-primary/20 flex items-center justify-between text-on-surface-variant font-label-sm text-label-sm animate-pulse"
		>
			<div class="flex items-center gap-2">
				<span class="material-symbols-outlined text-primary text-base animate-spin">sync</span>
				<span>Cargando materias inscritas y parciales del estudiante desde SQLite...</span>
			</div>
			<span class="font-code-num text-xs bg-surface-container px-2 py-0.5 rounded font-semibold text-primary">
				copilot.db
			</span>
		</div>
	{:else if simData.isRealData}
		<div
			class="p-space-md rounded-xl bg-surface-container-lowest border border-emerald-500/30 shadow-sm flex flex-col sm:flex-row sm:items-center justify-between gap-space-md"
		>
			<div class="flex items-center gap-space-sm">
				<div
					class="w-10 h-10 rounded-lg bg-emerald-500/10 flex items-center justify-center text-emerald-600 dark:text-emerald-400 shrink-0"
				>
					<span class="material-symbols-outlined text-xl">database</span>
				</div>
				<div class="flex flex-col">
					<div class="flex items-center gap-2">
						<span class="font-label-md text-label-md font-bold text-on-surface">
							Simulador Conectado a Datos Reales
						</span>
						<span
							class="px-2 py-0.5 rounded bg-emerald-500/15 text-emerald-700 dark:text-emerald-300 font-code-num text-xs font-semibold"
						>
							C.I. {user?.cedula}
						</span>
					</div>
					<span class="font-body-sm text-body-sm text-on-surface-variant">
						Analizando {simData.subjects.length} cátedras en curso oficiales. El Agente IA Copilot responderá con base en tu historial académico.
					</span>
				</div>
			</div>

			<span class="px-3 py-1 rounded-full bg-surface-container text-xs font-semibold text-secondary flex items-center gap-1 self-start sm:self-auto">
				<span class="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
				Gemini 3.5 Flash-Lite + SQLite
			</span>
		</div>
	{:else}
		<div
			class="p-space-md rounded-xl bg-surface-container-lowest border border-amber-500/30 shadow-sm flex flex-col sm:flex-row sm:items-center justify-between gap-space-md"
		>
			<div class="flex items-center gap-space-sm">
				<div
					class="w-10 h-10 rounded-lg bg-amber-500/10 flex items-center justify-center text-amber-500 shrink-0"
				>
					<span class="material-symbols-outlined text-xl">vpn_key_alert</span>
				</div>
				<div class="flex flex-col">
					<span class="font-label-md text-label-md font-bold text-on-surface">
						Modo Demostración Activo (Simulación Teórica)
					</span>
					<span class="font-body-sm text-body-sm text-on-surface-variant">
						Inicia sesión y sincroniza tus datos para simular con tus cátedras y parciales reales.
					</span>
				</div>
			</div>
			<a
				href="/"
				class="px-space-md py-2 bg-primary text-on-primary rounded font-label-md text-label-md font-semibold hover:bg-primary-container transition-colors shrink-0 flex items-center gap-1 self-start sm:self-auto"
			>
				<span class="material-symbols-outlined text-base">sync_alt</span>
				Iniciar Sesión
			</a>
		</div>
	{/if}

	<!-- Top Predictive Status & Metric Header -->
	<PredictiveHeader
		subjects={simData.subjects}
		{selectedSubjectId}
		onSubjectChange={handleSubjectChange}
	/>

	<!-- Primary Workspace: 2-Column Split Layout -->
	<div class="grid grid-cols-12 gap-space-lg items-start">
		<!-- LEFT COLUMN: Predictive Engine & Matrix (60% ~ 7 cols desktop) -->
		<div class="col-span-12 xl:col-span-7 flex flex-col gap-space-lg">
			<!-- Top Live Gauge & Mathematical Probability -->
			<GaugeChart {probability} {totalProcess} />

			<!-- Parametric Evaluation Matrix & Slider -->
			<EvaluationMatrix
				subject={currentSubject}
				{p2Value}
				onP2Change={handleSetP2}
			/>

			<!-- Simulated Final Exam Scenarios (1 al 5) -->
			<FinalExamScenarios
				subject={currentSubject}
				{totalProcess}
				{p2Value}
			/>
		</div>

		<!-- RIGHT COLUMN: AI Copilot Academic Conversational Agent (40% ~ 5 cols desktop) -->
		<AiCopilotChat
			subject={currentSubject}
			quickPrompts={simData.quickPrompts}
			onSetP2={handleSetP2}
			onSwitchSubject={handleSubjectChange}
		/>
	</div>
</div>
