<script lang="ts">
	import type {
		MLPredictResponse,
		MLModelProbability,
		MLSequentialPredictResponse
	} from '../../services/types';
	import type { SubjectSimulation } from '../../types/simulator';

	export interface Props {
		probability: number | null;
		totalProcess: number | null;
		subject?: SubjectSimulation;
		p2Value?: number;
		includeP2Projection?: boolean;
		mlPrediction?: MLPredictResponse | null;
		mlSequential?: MLSequentialPredictResponse | null;
		mlLoading?: boolean;
	}

	let {
		probability,
		totalProcess,
		subject,
		p2Value = 0,
		includeP2Projection = false,
		mlPrediction = null,
		mlSequential = null,
		mlLoading = false
	}: Props = $props();

	const circumference = 314.159;

	let strokeOffset = $derived(
		probability !== null
			? circumference - (circumference * Math.min(100, Math.max(0, probability))) / 100
			: circumference
	);

	let progressPercent = $derived(
		totalProcess !== null ? Math.min(100, Math.max(0, (totalProcess / 50) * 100)) : 0
	);

	let deltaHabilitacion = $derived(totalProcess !== null ? totalProcess - 30.0 : 0);

	let riskInfo = $derived.by(() => {
		if (probability === null) {
			return {
				label: 'Sin 1er Parcial Registrado',
				chipClass:
					'bg-surface-container-high text-on-surface-variant border border-outline-variant/40',
				gaugeColor: 'text-outline'
			};
		} else if (probability >= 75) {
			return {
				label: 'Alta Probabilidad / Favorable',
				chipClass:
					'bg-emerald-100 text-emerald-900 dark:bg-emerald-950/80 dark:text-emerald-300 border border-emerald-300 dark:border-emerald-700/50',
				gaugeColor: 'text-secondary'
			};
		} else if (probability >= 50) {
			return {
				label: 'Riesgo Moderado / Recuperable',
				chipClass:
					'bg-amber-100 text-amber-900 dark:bg-amber-950/80 dark:text-amber-200 border border-amber-300 dark:border-amber-700/50',
				gaugeColor: 'text-secondary'
			};
		} else {
			return {
				label: 'Riesgo Crítico / Refuerzo Urgente',
				chipClass:
					'bg-rose-100 text-rose-900 dark:bg-rose-950/80 dark:text-rose-300 border border-rose-300 dark:border-rose-700/50',
				gaugeColor: 'text-rose-500'
			};
		}
	});

	let modelEntries = $derived.by(() => {
		if (!mlPrediction)
			return [] as Array<{ key: string; item: MLModelProbability; isTemporal: boolean }>;
		const entries: Array<{ key: string; item: MLModelProbability; isTemporal: boolean }> = [];
		for (const [key, item] of Object.entries(mlPrediction.probabilidades)) {
			if (item) {
				entries.push({
					key,
					item,
					isTemporal: key === 'ensamble_temporal_gb' || key === 'red_neuronal_lstm'
				});
			}
		}
		return entries;
	});
</script>

<div
	class="bg-surface-container-lowest p-4 sm:p-space-lg rounded-xl shadow-sm flex flex-col gap-space-md relative overflow-hidden"
>
	<div
		class="absolute -right-16 -top-16 w-48 h-48 rounded-full bg-secondary-fixed/20 blur-2xl pointer-events-none"
	></div>

	<div class="flex flex-col md:flex-row gap-space-md sm:gap-space-lg items-center">
		<!-- Circular Gauge Chart -->
		<div class="relative w-44 h-44 flex items-center justify-center shrink-0">
			<svg class="w-full h-full transform -rotate-90" viewBox="0 0 120 120">
				<!-- Background Track Circle -->
				<circle
					class="text-surface-container-high"
					cx="60"
					cy="60"
					fill="transparent"
					r="50"
					stroke="currentColor"
					stroke-width="10"
				></circle>
				<!-- Animated Probability Circle -->
				<circle
					class="{riskInfo.gaugeColor} transition-all duration-700 ease-out"
					cx="60"
					cy="60"
					fill="transparent"
					r="50"
					stroke="currentColor"
					stroke-dasharray={circumference}
					stroke-dashoffset={strokeOffset}
					stroke-linecap="round"
					stroke-width="10"
				></circle>
			</svg>

			<div class="absolute inset-0 flex flex-col items-center justify-center text-center">
				<span class="font-headline-xl text-headline-xl leading-none font-bold text-primary">
					{probability !== null ? `${probability}%` : '--%'}
				</span>
				<span class="font-label-sm text-label-sm font-semibold tracking-wider uppercase text-outline mt-1">
					{#if probability === null}
						Sin P1
					{:else if mlPrediction}
						Consenso 5 Mod.
					{:else if mlSequential}
						Serie Temporal
					{:else}
						Est. Local
					{/if}
				</span>
			</div>
		</div>

		<!-- Metric Details & Trajectory -->
		<div class="flex flex-col gap-space-xs flex-1 w-full">
			<div class="flex flex-wrap items-center gap-space-xs">
				<span
					class="px-2.5 py-0.5 rounded text-[11px] font-semibold tracking-wide uppercase shadow-xs {riskInfo.chipClass}"
				>
					{riskInfo.label}
				</span>
				<span class="font-code-num text-code-num text-on-surface-variant flex items-center gap-1">
					<span class="material-symbols-outlined text-xs text-secondary {mlLoading ? 'animate-spin' : ''}">
						{mlLoading ? 'sync' : mlPrediction || mlSequential ? 'psychology' : 'info'}
					</span>
					{#if mlLoading}
						Calculando inferencia IA...
					{:else if mlPrediction}
						Inferencia Real (5 Modelos ML + LSTM)
					{:else if mlSequential}
						Serie Temporal Real ({mlSequential.hito})
					{:else if probability === null}
						Esperando nota de 1er Parcial
					{:else}
						Estimación aritmética local (Backend offline)
					{/if}
				</span>
			</div>

			<p class="font-body-md text-body-md text-on-surface leading-relaxed mt-1">
				{#if probability === null}
					Aún no se registra nota de 1er Parcial en InsWeb para ejecutar la predicción automática.
				{:else if mlPrediction}
					{mlPrediction.resumen.diagnostico}
				{:else if mlSequential}
					{mlSequential.diagnostico}
				{:else}
					Tu trayectoria actual exige calibrar el puntaje del Segundo Parcial para superar los 30.0 pts de habilitación reglamentaria.
				{/if}
			</p>

			<!-- Micro Score Progress Bar (solo si la materia tiene pesos oficiales 50/50) o Resumen Fiel de Notas -->
			{#if subject?.hasOfficialWeights && totalProcess !== null}
				<div class="bg-surface-container-low p-space-sm rounded-lg flex flex-col gap-1.5 mt-space-xs">
					<div class="flex justify-between items-center text-on-surface font-label-sm text-label-sm">
						<span class="font-medium text-on-surface-variant">
							Puntaje de Proceso Acumulado (P1 + P2 + Lab)
						</span>
						<span class="font-code-num text-code-num font-bold text-primary">
							{totalProcess.toFixed(1)} / 50 Puntos
						</span>
					</div>

					<div class="w-full h-2 rounded-full bg-surface-container-highest overflow-hidden">
						<div
							class="h-full bg-secondary rounded-full transition-all duration-300"
							style="width: {progressPercent}%"
						></div>
					</div>

					<div class="flex flex-col sm:flex-row sm:justify-between sm:items-center text-outline text-[11px] font-code-num gap-0.5">
						<span>Umbral Habilitación: 30.0 pts (60%)</span>
						{#if deltaHabilitacion >= 0}
							<span class="text-secondary font-semibold">
								+{deltaHabilitacion.toFixed(1)} pts margen de seguridad
							</span>
						{:else}
							<span class="text-rose-500 font-semibold">
								{deltaHabilitacion.toFixed(1)} pts (INSUFICIENTE - NO HABILITA)
							</span>
						{/if}
					</div>
				</div>
			{:else if subject}
				<div class="bg-surface-container-low p-space-sm rounded-lg flex flex-col gap-1.5 mt-space-xs">
					<div class="flex flex-wrap items-center justify-between gap-2 text-on-surface font-label-sm text-label-sm">
						<span class="font-medium text-on-surface-variant">
							Evaluaciones Reales en BD (Escala 0–100)
						</span>
						<span class="font-code-num text-[11px] text-secondary font-semibold">
							1er Parcial: {subject.p1 !== null ? `${subject.p1} / ${subject.p1Max}` : 'Pendiente'} •
							Lab/TP: {subject.hasLab ? (subject.lab !== null ? `${subject.lab} / ${subject.labMax}` : 'Pendiente') : 'No posee'} •
							2do Parcial: {subject.p2 !== null ? `${subject.p2} / ${subject.p2Max}` : includeP2Projection ? `Proyectado: ${p2Value} / ${subject.p2Max}` : 'Pendiente'}
						</span>
					</div>
					<span class="text-[11px] text-outline font-code-num">
						Sin ponderación oficial 50/50 en InsWeb — valores mostrados tal cual en BD
					</span>
				</div>
			{/if}
		</div>
	</div>

	<!-- Desglose en tiempo real de los 5 modelos (cuando hay proceso completo) o 2 modelos temporales (GB + LSTM) -->
	{#if modelEntries.length > 0}
		<div class="pt-space-sm border-t border-outline-variant/20">
			<div class="flex items-center justify-between mb-2 flex-wrap gap-1">
				<span class="font-label-sm text-label-sm uppercase tracking-wider text-on-surface-variant font-semibold">
					Desglose en Vivo por Modelo (POST /api/ml/predict)
				</span>
				{#if mlPrediction?.resumen.probabilidad_modelos_clasicos != null && mlPrediction?.resumen.probabilidad_modelos_temporales != null}
					<span class="font-code-num text-[11px] text-secondary font-semibold">
						Clásicos: {mlPrediction.resumen.probabilidad_modelos_clasicos}% • Temporales: {mlPrediction.resumen.probabilidad_modelos_temporales}%
					</span>
				{/if}
			</div>
			<div class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-2">
				{#each modelEntries as entry (entry.key)}
					<div
						class="p-2 rounded-lg border flex flex-col justify-between gap-1 {entry.isTemporal
							? 'bg-secondary-fixed/20 border-secondary/30 dark:bg-secondary-container/20'
							: 'bg-surface-container-low border-outline-variant/20'}"
					>
						<div class="flex items-center justify-between gap-1">
							<span class="text-[10px] font-bold uppercase tracking-wide {entry.isTemporal ? 'text-secondary' : 'text-outline'}">
								{entry.isTemporal ? 'Temporal' : 'Clásico'}
							</span>
							<span class="font-code-num text-xs font-bold {entry.item.probabilidad >= 50 ? 'text-emerald-600 dark:text-emerald-400' : 'text-rose-500'}">
								{entry.item.probabilidad.toFixed(1)}%
							</span>
						</div>
						<span class="text-[11px] font-semibold text-on-surface leading-tight truncate" title={entry.item.nombre}>
							{entry.item.nombre}
						</span>
					</div>
				{/each}
			</div>
		</div>
	{:else if mlSequential?.comparativa_modelos}
		<div class="pt-space-sm border-t border-outline-variant/20">
			<div class="flex items-center justify-between mb-2 flex-wrap gap-1">
				<span class="font-label-sm text-label-sm uppercase tracking-wider text-on-surface-variant font-semibold">
					Inferencia Secuencial Temporal (POST /api/ml/predict-sequential)
				</span>
				<span class="font-code-num text-[11px] text-secondary font-semibold">
					Etapa {mlSequential.etapa_temporal} • {mlSequential.estado_trayectoria}
				</span>
			</div>
			<div class="grid grid-cols-1 sm:grid-cols-2 gap-2">
				<div class="p-2.5 rounded-lg border bg-secondary-fixed/20 border-secondary/30 dark:bg-secondary-container/20 flex items-center justify-between gap-2">
					<div class="flex flex-col min-w-0">
						<span class="text-[10px] font-bold uppercase tracking-wide text-secondary">
							Temporal Clásico
						</span>
						<span class="text-xs font-semibold text-on-surface truncate">
							{mlSequential.comparativa_modelos.ensamble_clasico.modelo}
						</span>
					</div>
					<span class="font-code-num text-sm font-bold shrink-0 {mlSequential.comparativa_modelos.ensamble_clasico.probabilidad >= 50 ? 'text-emerald-600 dark:text-emerald-400' : 'text-rose-500'}">
						{mlSequential.comparativa_modelos.ensamble_clasico.probabilidad.toFixed(1)}%
					</span>
				</div>

				<div class="p-2.5 rounded-lg border bg-secondary-fixed/20 border-secondary/30 dark:bg-secondary-container/20 flex items-center justify-between gap-2">
					<div class="flex flex-col min-w-0">
						<span class="text-[10px] font-bold uppercase tracking-wide text-secondary">
							Deep Learning (PyTorch)
						</span>
						<span class="text-xs font-semibold text-on-surface truncate">
							{mlSequential.comparativa_modelos.red_neuronal_lstm.modelo}
						</span>
					</div>
					<span class="font-code-num text-sm font-bold shrink-0 {mlSequential.comparativa_modelos.red_neuronal_lstm.probabilidad >= 50 ? 'text-emerald-600 dark:text-emerald-400' : 'text-rose-500'}">
						{mlSequential.comparativa_modelos.red_neuronal_lstm.probabilidad.toFixed(1)}%
					</span>
				</div>
			</div>
		</div>
	{/if}
</div>
