<script lang="ts">
	import type { SubjectSimulation } from '../../types/simulator';

	export interface Props {
		subjects: SubjectSimulation[];
		selectedSubjectId: string;
		onSubjectChange: (id: string) => void;
		bestAuc?: number | null;
		sampleCount?: number | null;
		activeModelsCount?: number | null;
		isBackendLive?: boolean;
	}

	let {
		subjects,
		selectedSubjectId,
		onSubjectChange,
		bestAuc = null,
		sampleCount = null,
		activeModelsCount = null,
		isBackendLive = false
	}: Props = $props();

	let aucDisplay = $derived(
		bestAuc !== null && bestAuc !== undefined ? `${(bestAuc * 100).toFixed(1)}%` : '98.2%'
	);
	let samplesDisplay = $derived(sampleCount ?? 1798);
	let modelsDisplay = $derived(activeModelsCount ?? 5);
</script>

<div class="grid grid-cols-12 gap-space-md">
	<!-- Left Status & Subject Selector Banner -->
	<div
		class="col-span-12 lg:col-span-8 flex flex-col md:flex-row items-start md:items-center justify-between p-space-md bg-surface-container-lowest rounded-xl shadow-sm gap-space-md"
	>
		<div class="flex items-center gap-space-md">
			<div
				class="w-12 h-12 rounded-lg bg-primary-container text-secondary-fixed dark:text-[#b1c7f0] flex items-center justify-center shrink-0 shadow-sm"
			>
				<span class="material-symbols-outlined text-2xl">analytics</span>
			</div>
			<div class="flex flex-col">
				<div class="flex items-center gap-space-xs">
					<span
						class="font-label-sm text-label-sm uppercase tracking-wider text-secondary font-semibold"
					>
						Simulador Neural FIUNA
					</span>
					<span class="inline-block w-1.5 h-1.5 rounded-full bg-secondary"></span>
					<span class="font-code-num text-code-num text-outline">
						Reglamento Académico Art. 47
					</span>
				</div>
				<h1 class="font-headline-sm text-headline-sm text-on-surface font-bold tracking-tight">
					Pronóstico Cuantitativo de Habilitación &amp; Rendimiento
				</h1>
			</div>
		</div>

		<div class="flex items-center gap-space-sm w-full md:w-auto">
			<label class="sr-only" for="subjectSelect">Seleccionar Cátedra</label>
			<div class="relative w-full md:w-80">
				<select
					id="subjectSelect"
					class="w-full bg-surface-container-low text-on-surface font-label-md text-label-md py-2.5 pl-3 pr-8 rounded-lg appearance-none focus:outline-none focus:ring-2 focus:ring-secondary cursor-pointer shadow-sm transition-colors border border-outline-variant/30"
					value={selectedSubjectId}
					onchange={(e) => onSubjectChange(e.currentTarget.value)}
				>
					{#each subjects as subject (subject.id)}
						<option value={subject.id}>
							{subject.name} ({subject.catedra} - {subject.professor})
						</option>
					{/each}
				</select>
				<span
					class="material-symbols-outlined absolute right-2.5 top-1/2 -translate-y-1/2 pointer-events-none text-on-surface-variant text-base"
				>
					expand_more
				</span>
			</div>
		</div>
	</div>

	<!-- Quick Vital Cohort Card (Métricas reales desde GET /api/ml/models) -->
	<div
		class="col-span-12 lg:col-span-4 bg-surface-container-lowest p-space-md rounded-xl shadow-sm flex items-center justify-between"
	>
		<div class="flex flex-col">
			<div class="flex items-center gap-1.5">
				<span class="font-label-sm text-label-sm uppercase tracking-wider text-on-surface-variant">
					AUC-ROC Validado (GB H3)
				</span>
				<span
					class="w-2 h-2 rounded-full {isBackendLive ? 'bg-emerald-500' : 'bg-amber-500'}"
					title={isBackendLive ? 'Conectado al catálogo /api/ml/models' : 'Valores validados del modelo guardado'}
				></span>
			</div>
			<div class="flex items-baseline gap-space-xs">
				<span class="font-headline-md text-headline-md font-bold text-primary font-code-num">
					{aucDisplay}
				</span>
				<span class="font-code-num text-code-num text-secondary font-semibold">
					N={samplesDisplay} registros
				</span>
			</div>
			<span class="font-body-sm text-body-sm text-outline mt-0.5">
				{modelsDisplay} modelos activos (ML Clásico + LSTM)
			</span>
		</div>
		<div
			class="w-11 h-11 rounded-lg bg-surface-container-high flex items-center justify-center text-primary"
		>
			<span class="material-symbols-outlined text-2xl">model_training</span>
		</div>
	</div>
</div>
