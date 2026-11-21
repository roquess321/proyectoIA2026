<script lang="ts">
	import { onMount } from 'svelte';
	import { academicState } from '../../academic-state.svelte';
	import { authState } from '../../auth-state.svelte';
	import { getEstudiante, type EstudianteSummary } from '../../services/scraper';
	import { buildSimulatorSubjects, type SimulatorData } from '../../services/simulator-data';
	import {
		getAvailableMLModels,
		getMLPrediction,
		getMLSequentialPrediction,
		retrainMLModels
	} from '../../services/gemini';
	import type {
		MLModelsCatalogResponse,
		MLPredictResponse,
		MLSequentialPredictResponse
	} from '../../services/types';
	import type { SubjectSimulation } from '../../types/simulator';
	import PredictiveHeader from './PredictiveHeader.svelte';
	import GaugeChart from './GaugeChart.svelte';
	import EvaluationMatrix from './EvaluationMatrix.svelte';
	import FinalExamScenarios from './FinalExamScenarios.svelte';
	import AiCopilotChat from './AiCopilotChat.svelte';

	let isLoading = $state(false);
	let studentData = $state<EstudianteSummary | null>(null);

	// Estado del motor ML / Deep Learning real del backend
	let mlCatalog = $state<MLModelsCatalogResponse | null>(null);
	let mlPrediction = $state<MLPredictResponse | null>(null);
	let mlSequential = $state<MLSequentialPredictResponse | null>(null);
	let mlLoading = $state(false);
	let mlOnline = $state(false);
	let mlRequestSeq = 0;

	// Estado de reentrenamiento por materia
	let isRetraining = $state(false);
	let retrainMessage = $state<string | null>(null);
	let retrainError = $state<string | null>(null);
	let lastRetrainDuration = $state<number | null>(null);
	let retrainVersion = $state(0);

	function slugifySubject(name: string): string {
		let s = name.trim().toLowerCase();
		const accents: Array<[string, string]> = [
			['á', 'a'],
			['é', 'e'],
			['í', 'i'],
			['ó', 'o'],
			['ú', 'u'],
			['ñ', 'n']
		];
		for (const [acc, raw] of accents) {
			s = s.replaceAll(acc, raw);
		}
		return s.replace(/[^a-z0-9]+/g, '_').replace(/^_+|_+$/g, '');
	}

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

	async function loadModelCatalog(): Promise<void> {
		try {
			mlCatalog = await getAvailableMLModels();
			mlOnline = true;
		} catch {
			mlOnline = false;
		}
	}

	onMount(() => {
		academicState.activeNav = 'agente-ia-pronosticos';
		void loadModelCatalog();
		if (user?.cedula) {
			void loadStudentData();
		}
	});

	$effect(() => {
		if (user?.cedula) {
			void loadStudentData();
		} else {
			studentData = null;
		}
	});

	let simData: SimulatorData = $derived(buildSimulatorSubjects(studentData, user));

	let selectedSubjectId = $state<string>('');
	let p2Value = $state<number>(60);
	let includeP2Projection = $state<boolean>(false);

	// Mantener sincronizada la materia seleccionada cuando cambien los datos o se carguen las materias reales
	$effect(() => {
		if (simData.subjects.length > 0) {
			const found = simData.subjects.find((s) => s.id === selectedSubjectId);
			if (!found) {
				const first = simData.subjects[0];
				selectedSubjectId = first.id;
				p2Value = first.defaultP2;
				includeP2Projection = first.hasOfficialWeights || first.p2 !== null;
			}
		}
	});

	let currentSubject: SubjectSimulation = $derived(
		simData.subjects.find((s) => s.id === selectedSubjectId) ?? simData.subjects[0]
	);

	let currentSubjectSlug = $derived(slugifySubject(currentSubject.name));

	let matchedClassicModel = $derived(
		mlCatalog?.primer_parcial?.find((m) => m.materia_slug === currentSubjectSlug) ??
			mlCatalog?.primer_parcial?.find((m) => m.materia_slug === 'estatica') ??
			mlCatalog?.primer_parcial?.[0] ??
			null
	);

	let matchedSeriesModel = $derived(
		mlCatalog?.series_temporales?.ensamble_clasico?.find(
			(m) => m.slug === currentSubjectSlug
		) ??
			mlCatalog?.series_temporales?.ensamble_clasico?.find((m) => m.slug === 'estatica') ??
			mlCatalog?.series_temporales?.ensamble_clasico?.[0] ??
			null
	);

	let matchedLstmModel = $derived(
		mlCatalog?.series_temporales?.red_neuronal_lstm?.find(
			(m) => m.slug === currentSubjectSlug
		) ??
			mlCatalog?.series_temporales?.red_neuronal_lstm?.find((m) => m.slug === 'estatica') ??
			mlCatalog?.series_temporales?.red_neuronal_lstm?.[0] ??
			null
	);

	let isSpecificModel = $derived(
		Boolean(
			mlCatalog &&
				(mlCatalog.primer_parcial?.some((m) => m.materia_slug === currentSubjectSlug) ||
					mlCatalog.series_temporales?.ensamble_clasico?.some(
						(m) => m.slug === currentSubjectSlug
					))
		)
	);

	let activeModelLabel = $derived(
		isSpecificModel
			? (matchedClassicModel?.materia_dataset ??
					matchedSeriesModel?.materia_dataset ??
					currentSubject.name)
			: 'estatica (modelo base)'
	);

	let activeModelsCount = $derived(mlCatalog?.modelos_activos?.length ?? null);
	let sampleCount = $derived(
		matchedClassicModel?.total_muestras ??
			matchedSeriesModel?.total_registros_entrenamiento ??
			null
	);
	let bestAuc = $derived(
		matchedSeriesModel?.metricas?.hito_3_proceso_completo?.auc_roc ??
			matchedClassicModel?.metricas?.random_forest?.auc_roc ??
			null
	);

	// Llamada reactiva con debounce de 250ms al motor real (completo 5 modelos o secuencial por hito)
	$effect(() => {
		const subj = currentSubject;
		const p2Proj = includeP2Projection;
		const p2Val = p2Value;
		const _retrainTrigger = retrainVersion;
		void _retrainTrigger;

		if (subj.p1 === null) {
			++mlRequestSeq;
			mlPrediction = null;
			mlSequential = null;
			mlLoading = false;
			return;
		}

		const p1_100 =
			subj.p1Max === 100
				? subj.p1
				: Math.max(0, Math.min(100, Math.round((subj.p1 / subj.p1Max) * 100)));

		const lab_100: number | null =
			subj.hasLab && subj.lab !== null
				? subj.labMax === 100
					? subj.lab
					: Math.max(0, Math.min(100, Math.round((subj.lab / subj.labMax) * 100)))
				: null;

		const hasP2 = p2Proj || subj.p2 !== null || subj.hasOfficialWeights;
		const rawP2 = subj.p2 !== null && !p2Proj ? subj.p2 : p2Val;
		const p2_100: number | null = hasP2
			? subj.p2Max === 100
				? rawP2
				: Math.max(0, Math.min(100, Math.round((rawP2 / subj.p2Max) * 100)))
			: null;

		const seq = ++mlRequestSeq;
		const timer = setTimeout(async () => {
			mlLoading = true;
			try {
				if (lab_100 !== null && p2_100 !== null) {
					const res = await getMLPrediction(subj.name, p1_100, p2_100, lab_100);
					if (seq === mlRequestSeq) {
						mlPrediction = res;
						mlSequential = null;
						mlOnline = true;
					}
				} else {
					const resSeq = await getMLSequentialPrediction(
						subj.name,
						p1_100,
						lab_100,
						p2_100
					);
					if (seq === mlRequestSeq) {
						mlSequential = resSeq;
						mlPrediction = null;
						mlOnline = true;
					}
				}
			} catch {
				if (seq === mlRequestSeq) {
					mlPrediction = null;
					mlSequential = null;
					mlOnline = false;
				}
			} finally {
				if (seq === mlRequestSeq) {
					mlLoading = false;
				}
			}
		}, 250);

		return () => {
			clearTimeout(timer);
		};
	});

	function handleSubjectChange(newId: string) {
		selectedSubjectId = newId;
		retrainMessage = null;
		retrainError = null;
		lastRetrainDuration = null;
		const found = simData.subjects.find((s) => s.id === newId);
		if (found) {
			p2Value = found.defaultP2;
			includeP2Projection = found.hasOfficialWeights || found.p2 !== null;
		}
	}

	async function handleRetrainCurrentSubject(): Promise<void> {
		if (isRetraining) return;
		isRetraining = true;
		retrainMessage = null;
		retrainError = null;
		try {
			const res = await retrainMLModels(currentSubject.name);
			retrainMessage = res.mensaje;
			lastRetrainDuration = res.duracion_seg;
			await loadModelCatalog();
			retrainVersion += 1;
		} catch (err: unknown) {
			retrainError =
				err instanceof Error ? err.message : 'No se pudo reentrenar el modelo para esta materia.';
		} finally {
			isRetraining = false;
		}
	}

	function handleSetP2(val: number) {
		p2Value = val;
		includeP2Projection = true;
	}

	function handleToggleP2Projection(enabled: boolean) {
		includeP2Projection = enabled;
	}

	// Solo calcular suma de proceso sobre 50 si la materia usa pesos oficiales 50/50
	let totalProcess = $derived(
		currentSubject.hasOfficialWeights &&
			currentSubject.p1 !== null &&
			currentSubject.lab !== null
			? currentSubject.p1 + p2Value + currentSubject.lab
			: null
	);

	let probability = $derived.by(() => {
		if (currentSubject.p1 === null) return null;
		if (mlPrediction) return Math.round(mlPrediction.resumen.probabilidad_promedio);
		if (mlSequential) return Math.round(mlSequential.probabilidad_aprobacion);
		if (totalProcess !== null) {
			return Math.max(10, Math.min(96, Math.round(15 + (totalProcess / 50) * 82)));
		}
		return null;
	});
</script>

<svelte:head>
	<title>Simulador Predictivo &amp; Agente IA - FIUNA Academic AI Suite</title>
</svelte:head>

<div class="flex flex-col w-full gap-space-lg pb-20 sm:pb-24">
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
				<span class="w-2 h-2 rounded-full {mlOnline ? 'bg-emerald-500 animate-pulse' : 'bg-amber-500'}"></span>
				Gemini + 5 Modelos ML/LSTM
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
		{bestAuc}
		{sampleCount}
		{activeModelsCount}
		isBackendLive={mlOnline}
		{activeModelLabel}
		{isSpecificModel}
		{isRetraining}
		{retrainMessage}
		{retrainError}
		{lastRetrainDuration}
		classicMetadata={matchedClassicModel}
		seriesMetadata={matchedSeriesModel}
		lstmMetadata={matchedLstmModel}
		onRetrain={handleRetrainCurrentSubject}
	/>

	<!-- Primary Workspace: Paneles Predictivos en Ancho Completo -->
	<div class="flex flex-col gap-space-lg">
		<!-- Top Live Gauge & Real ML+LSTM Consensus -->
		<GaugeChart
			{probability}
			{totalProcess}
			subject={currentSubject}
			{p2Value}
			{includeP2Projection}
			{mlPrediction}
			{mlSequential}
			{mlLoading}
		/>

		<!-- Parametric Evaluation Matrix & Slider -->
		<EvaluationMatrix
			subject={currentSubject}
			{p2Value}
			{includeP2Projection}
			onP2Change={handleSetP2}
			onToggleP2Projection={handleToggleP2Projection}
		/>

		<!-- Simulated Final Exam Scenarios / Diagnóstico Secuencial -->
		<FinalExamScenarios
			subject={currentSubject}
			{totalProcess}
			{p2Value}
			{mlPrediction}
			{mlSequential}
		/>
	</div>

	<!-- Burbuja Flotante del Copiloto Académico IA -->
	<AiCopilotChat
		subject={currentSubject}
		quickPrompts={simData.quickPrompts}
		onSetP2={handleSetP2}
		onSwitchSubject={handleSubjectChange}
	/>
</div>
