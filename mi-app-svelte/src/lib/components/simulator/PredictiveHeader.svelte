<script lang="ts">
	import type {
		MLClassicMetadataItem,
		MLLstmMetadataItem,
		MLModelMetricsEntry,
		MLSeriesMetadataItem
	} from '../../services/types';
	import type { SubjectSimulation } from '../../types/simulator';

	export interface Props {
		subjects: SubjectSimulation[];
		selectedSubjectId: string;
		onSubjectChange: (id: string) => void;
		bestAuc?: number | null;
		sampleCount?: number | null;
		activeModelsCount?: number | null;
		isBackendLive?: boolean;
		activeModelLabel?: string;
		isSpecificModel?: boolean;
		isRetraining?: boolean;
		retrainMessage?: string | null;
		retrainError?: string | null;
		lastRetrainDuration?: number | null;
		classicMetadata?: MLClassicMetadataItem | null;
		seriesMetadata?: MLSeriesMetadataItem | null;
		lstmMetadata?: MLLstmMetadataItem | null;
		onRetrain?: () => void;
	}

	let {
		subjects,
		selectedSubjectId,
		onSubjectChange,
		bestAuc = null,
		sampleCount = null,
		activeModelsCount = null,
		isBackendLive = false,
		activeModelLabel = 'estatica (base)',
		isSpecificModel = false,
		isRetraining = false,
		retrainMessage = null,
		retrainError = null,
		lastRetrainDuration = null,
		classicMetadata = null,
		seriesMetadata = null,
		lstmMetadata = null,
		onRetrain
	}: Props = $props();

	let showTrainingMetrics = $state(false);

	let aucDisplay = $derived(
		bestAuc !== null && bestAuc !== undefined ? `${(bestAuc * 100).toFixed(1)}%` : '98.2%'
	);
	let samplesDisplay = $derived(sampleCount ?? 1798);
	let modelsDisplay = $derived(activeModelsCount ?? 5);

	function fmtPct(val: number | undefined | null): string {
		if (val === undefined || val === null || Number.isNaN(val)) return '--';
		return `${(val * 100).toFixed(1)}%`;
	}

	interface ClassicRow {
		key: string;
		label: string;
		metrics: MLModelMetricsEntry | undefined;
	}

	let classicRows = $derived<ClassicRow[]>([
		{
			key: 'regresion_logistica',
			label: 'Regresión Logística',
			metrics: classicMetadata?.metricas?.regresion_logistica
		},
		{
			key: 'arbol_decision',
			label: 'Árbol de Decisión',
			metrics: classicMetadata?.metricas?.arbol_decision
		},
		{
			key: 'random_forest',
			label: 'Random Forest',
			metrics: classicMetadata?.metricas?.random_forest
		}
	]);

	let approvalRateDisplay = $derived(
		classicMetadata?.tasa_aprobacion_real !== undefined
			? fmtPct(classicMetadata.tasa_aprobacion_real)
			: '--'
	);
</script>

<div class="grid grid-cols-12 gap-space-md">
	<!-- Left Status & Subject Selector Banner -->
	<div
		class="col-span-12 lg:col-span-7 flex flex-col md:flex-row items-start md:items-center justify-between p-space-md bg-surface-container-lowest rounded-xl shadow-sm gap-space-md"
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

	<!-- Quick Vital Cohort Card + Retrain & Toggle Metrics Buttons -->
	<div
		class="col-span-12 lg:col-span-5 bg-surface-container-lowest p-space-md rounded-xl shadow-sm flex flex-col justify-between gap-space-sm"
	>
		<div class="flex items-center justify-between gap-space-sm">
			<div class="flex flex-col min-w-0">
				<div class="flex items-center gap-1.5 flex-wrap">
					<span class="font-label-sm text-label-sm uppercase tracking-wider text-on-surface-variant">
						AUC-ROC Validado (GB H3)
					</span>
					<span
						class="w-2 h-2 rounded-full {isBackendLive ? 'bg-emerald-500' : 'bg-amber-500'}"
						title={isBackendLive ? 'Conectado al catálogo /api/ml/models' : 'Valores validados del modelo guardado'}
					></span>
					<span
						class="px-1.5 py-0.5 rounded font-label-sm text-[10px] font-semibold uppercase {isSpecificModel
							? 'bg-emerald-500/15 text-emerald-700 dark:text-emerald-300'
							: 'bg-amber-500/15 text-amber-700 dark:text-amber-300'}"
					>
						{isSpecificModel ? 'Modelo específico' : 'Base: estatica'}
					</span>
				</div>
				<div class="flex items-baseline gap-space-xs mt-0.5">
					<span class="font-headline-md text-headline-md font-bold text-primary font-code-num">
						{aucDisplay}
					</span>
					<span class="font-code-num text-code-num text-secondary font-semibold">
						N={samplesDisplay} registros
					</span>
				</div>
				<span class="font-body-sm text-body-sm text-outline truncate mt-0.5" title={activeModelLabel}>
					{modelsDisplay} modelos activos • {activeModelLabel}
				</span>
			</div>

			<div class="flex flex-col items-end gap-1.5 shrink-0">
				{#if onRetrain}
					<button
						type="button"
						disabled={isRetraining}
						onclick={onRetrain}
						class="w-full px-3 py-1.5 rounded-lg bg-primary hover:bg-primary-container disabled:opacity-60 text-on-primary font-label-sm text-label-sm font-semibold flex items-center justify-center gap-1.5 shadow-sm transition-all active:scale-95 cursor-pointer"
						title="Reentrenar los 5 modelos ML y LSTM con los datos históricos de la materia seleccionada"
					>
						<span
							class="material-symbols-outlined text-base {isRetraining ? 'animate-spin' : ''}"
						>
							{isRetraining ? 'autorenew' : 'model_training'}
						</span>
						<span>{isRetraining ? 'Reentrenando...' : 'Reentrenar materia'}</span>
					</button>
				{/if}

				<button
					type="button"
					onclick={() => (showTrainingMetrics = !showTrainingMetrics)}
					class="w-full px-2.5 py-1 rounded-lg bg-surface-container-low hover:bg-surface-container text-on-surface-variant hover:text-on-surface border border-outline-variant/30 font-label-sm text-xs font-semibold flex items-center justify-center gap-1 transition-colors cursor-pointer"
					aria-expanded={showTrainingMetrics}
				>
					<span class="material-symbols-outlined text-sm text-secondary">monitoring</span>
					<span>{showTrainingMetrics ? 'Ocultar métricas' : 'Ver métricas'}</span>
					<span class="material-symbols-outlined text-sm">
						{showTrainingMetrics ? 'expand_less' : 'expand_more'}
					</span>
				</button>
			</div>
		</div>

		{#if retrainMessage}
			<div
				class="px-2.5 py-1.5 rounded-lg bg-emerald-500/10 border border-emerald-500/30 text-emerald-800 dark:text-emerald-300 font-body-sm text-xs flex items-center gap-1.5"
			>
				<span class="material-symbols-outlined text-sm shrink-0">check_circle</span>
				<span class="truncate" title={retrainMessage}>{retrainMessage}</span>
			</div>
		{:else if retrainError}
			<div
				class="px-2.5 py-1.5 rounded-lg bg-error/10 border border-error/30 text-error font-body-sm text-xs flex items-center gap-1.5"
			>
				<span class="material-symbols-outlined text-sm shrink-0">error</span>
				<span class="truncate" title={retrainError}>{retrainError}</span>
			</div>
		{/if}
	</div>

	<!-- Panel Desplegable de Métricas del Último Entrenamiento -->
	{#if showTrainingMetrics}
		<div
			class="col-span-12 bg-surface-container-lowest p-space-md rounded-xl shadow-sm border border-outline-variant/30 flex flex-col gap-space-md"
		>
			<div class="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-space-xs border-b border-outline-variant/20">
				<div class="flex items-center gap-2">
					<span class="material-symbols-outlined text-primary text-xl">assessment</span>
					<div>
						<h3 class="font-label-md text-label-md font-bold text-on-surface">
							Métricas de Validación del Último Entrenamiento ({activeModelLabel})
						</h3>
						<p class="font-body-sm text-xs text-on-surface-variant">
							Evaluadas sobre partición de prueba estratificada (Test Set) de <code class="font-code-num">datos_concatenados.csv</code>
						</p>
					</div>
				</div>

				<div class="flex items-center gap-2 flex-wrap">
					<span class="px-2 py-0.5 rounded bg-surface-container-low font-code-num text-xs text-on-surface">
						Muestras: <strong>{samplesDisplay}</strong>
					</span>
					<span class="px-2 py-0.5 rounded bg-surface-container-low font-code-num text-xs text-on-surface">
						Tasa aprobación real: <strong>{approvalRateDisplay}</strong>
					</span>
					{#if lastRetrainDuration !== null}
						<span class="px-2 py-0.5 rounded bg-emerald-500/15 font-code-num text-xs text-emerald-700 dark:text-emerald-300 font-semibold">
							Tiempo: {lastRetrainDuration}s
						</span>
					{/if}
					{#if classicMetadata?.fallback_global}
						<span class="px-2 py-0.5 rounded bg-amber-500/15 font-label-sm text-xs text-amber-800 dark:text-amber-300 font-semibold">
							Cohorte Complementada
						</span>
					{/if}
				</div>
			</div>

			<div class="grid grid-cols-1 lg:grid-cols-12 gap-space-md">
				<!-- Tabla 1: Modelos Clásicos -->
				<div class="lg:col-span-7 bg-surface-container-low p-space-sm rounded-lg flex flex-col gap-2">
					<div class="flex items-center justify-between">
						<span class="font-label-sm text-xs uppercase font-bold text-on-surface tracking-wider">
							Modelos Clásicos (3 Variables: P1, P2, TP/Lab)
						</span>
						<span class="font-code-num text-[11px] text-outline">Test Split 30%</span>
					</div>

					<div class="overflow-x-auto">
						<table class="w-full text-left border-collapse font-code-num text-xs">
							<thead>
								<tr class="border-b border-outline-variant/30 text-on-surface-variant">
									<th class="py-1.5 pr-2 font-semibold">Modelo</th>
									<th class="py-1.5 px-2 text-right font-semibold">AUC-ROC</th>
									<th class="py-1.5 px-2 text-right font-semibold">Accuracy</th>
									<th class="py-1.5 px-2 text-right font-semibold">Precision</th>
									<th class="py-1.5 px-2 text-right font-semibold">Recall</th>
									<th class="py-1.5 pl-2 text-right font-semibold">F1-Score</th>
								</tr>
							</thead>
							<tbody>
								{#each classicRows as row (row.key)}
									<tr class="border-b border-outline-variant/15 last:border-b-0">
										<td class="py-1.5 pr-2 font-body-sm font-semibold text-on-surface">
											{row.label}
										</td>
										<td class="py-1.5 px-2 text-right font-bold text-primary">
											{fmtPct(row.metrics?.auc_roc)}
										</td>
										<td class="py-1.5 px-2 text-right text-on-surface">
											{fmtPct(row.metrics?.accuracy)}
										</td>
										<td class="py-1.5 px-2 text-right text-on-surface-variant">
											{fmtPct(row.metrics?.precision)}
										</td>
										<td class="py-1.5 px-2 text-right text-on-surface-variant">
											{fmtPct(row.metrics?.recall)}
										</td>
										<td class="py-1.5 pl-2 text-right font-semibold text-secondary">
											{fmtPct(row.metrics?.f1)}
										</td>
									</tr>
								{/each}
							</tbody>
						</table>
					</div>
				</div>

				<!-- Tabla 2: Modelos Secuenciales / Series Temporales por Hito -->
				<div class="lg:col-span-5 bg-surface-container-low p-space-sm rounded-lg flex flex-col gap-2">
					<div class="flex items-center justify-between">
						<span class="font-label-sm text-xs uppercase font-bold text-on-surface tracking-wider">
							Series Temporales por Hitos (AUC-ROC)
						</span>
						<span class="font-code-num text-[11px] text-outline">Test Split 25%</span>
					</div>

					<div class="overflow-x-auto">
						<table class="w-full text-left border-collapse font-code-num text-xs">
							<thead>
								<tr class="border-b border-outline-variant/30 text-on-surface-variant">
									<th class="py-1.5 pr-2 font-semibold">Arquitectura</th>
									<th class="py-1.5 px-2 text-right font-semibold" title="Hito 1: Solo 1er Parcial">Hito 1 (P1)</th>
									<th class="py-1.5 px-2 text-right font-semibold" title="Hito 2: 1er Parcial + TP/Lab">Hito 2 (+TP)</th>
									<th class="py-1.5 px-2 text-right font-semibold" title="Hito 3: Proceso Completo (P1 + TP + P2)">Hito 3 (Total)</th>
									<th class="py-1.5 pl-2 text-right font-semibold">Acc / F1 (H3)</th>
								</tr>
							</thead>
							<tbody>
								<tr class="border-b border-outline-variant/15">
									<td class="py-1.5 pr-2 font-body-sm font-semibold text-on-surface">
										Gradient Boosting
									</td>
									<td class="py-1.5 px-2 text-right text-on-surface">
										{fmtPct(seriesMetadata?.metricas?.hito_1_primer_parcial?.auc_roc)}
									</td>
									<td class="py-1.5 px-2 text-right text-on-surface">
										{fmtPct(seriesMetadata?.metricas?.hito_2_tp_taller?.auc_roc)}
									</td>
									<td class="py-1.5 px-2 text-right font-bold text-primary">
										{fmtPct(seriesMetadata?.metricas?.hito_3_proceso_completo?.auc_roc)}
									</td>
									<td class="py-1.5 pl-2 text-right text-outline">
										Multi-Hito
									</td>
								</tr>
								<tr>
									<td class="py-1.5 pr-2 font-body-sm font-semibold text-on-surface">
										Red LSTM (PyTorch)
									</td>
									<td class="py-1.5 px-2 text-right text-on-surface">
										{fmtPct(lstmMetadata?.metricas_por_hito?.hito_1_primer_parcial?.auc_roc)}
									</td>
									<td class="py-1.5 px-2 text-right text-on-surface">
										{fmtPct(lstmMetadata?.metricas_por_hito?.hito_2_tp_taller?.auc_roc)}
									</td>
									<td class="py-1.5 px-2 text-right font-bold text-primary">
										{fmtPct(lstmMetadata?.metricas_por_hito?.hito_3_proceso_completo?.auc_roc)}
									</td>
									<td class="py-1.5 pl-2 text-right text-secondary font-semibold">
										{fmtPct(lstmMetadata?.metricas_por_hito?.hito_3_proceso_completo?.accuracy)} / {fmtPct(lstmMetadata?.metricas_por_hito?.hito_3_proceso_completo?.f1_score)}
									</td>
								</tr>
							</tbody>
						</table>
					</div>
				</div>
			</div>
		</div>
	{/if}
</div>
