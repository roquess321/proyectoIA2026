<script lang="ts">
	import type { SubjectSimulation } from '../../types/simulator';
	import type { MLPredictResponse, MLSequentialPredictResponse } from '../../services/types';

	export interface Props {
		subject: SubjectSimulation;
		totalProcess: number | null;
		p2Value: number;
		mlPrediction?: MLPredictResponse | null;
		mlSequential?: MLSequentialPredictResponse | null;
	}

	let {
		subject,
		totalProcess,
		p2Value,
		mlPrediction = null,
		mlSequential = null
	}: Props = $props();

	let safeProcess = $derived(totalProcess ?? 0);

	// Calculations for required final scores (Scale: Final is out of 50 pts, min required usually 20 pts)
	let neededN2 = $derived(Math.max(20, Math.round(60 - safeProcess)));
	let neededN3 = $derived(Math.max(25, Math.round(75 - safeProcess)));
	let neededN4 = $derived(Math.max(30, Math.round(86 - safeProcess)));
	let neededN5 = $derived(Math.max(35, Math.round(95 - safeProcess)));

	let isN2Reachable = $derived(neededN2 <= 50 && safeProcess >= 30);
	let isN3Reachable = $derived(neededN3 <= 50 && safeProcess >= 30);
	let isN4Reachable = $derived(neededN4 <= 50 && safeProcess >= 30);
	let isN5Reachable = $derived(neededN5 <= 50 && safeProcess >= 30);

	// Referencias aritméticas locales de exigencia sobre el examen final (no es salida ML)
	let factibilidadN2 = $derived(
		isN2Reachable ? Math.max(10, Math.min(94, Math.round(105 - (neededN2 / 50) * 60))) : 0
	);
	let factibilidadN3 = $derived(
		isN3Reachable ? Math.max(5, Math.min(85, Math.round(100 - (neededN3 / 50) * 75))) : 0
	);
	let factibilidadN4 = $derived(
		isN4Reachable ? Math.max(2, Math.min(70, Math.round(100 - (neededN4 / 50) * 85))) : 0
	);
</script>

<div class="bg-surface-container-lowest p-4 sm:p-space-lg rounded-xl shadow-sm flex flex-col gap-space-md">
	<div class="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
		<div class="flex flex-col">
			<h2 class="font-headline-sm text-headline-sm text-on-surface font-semibold">
				Escenarios en Examen Final &amp; Diagnóstico Temporal
			</h2>
			<span class="font-body-sm text-body-sm text-on-surface-variant">
				{#if subject.hasOfficialWeights && totalProcess !== null}
					Requerimientos sobre el examen de 50 puntos acumulativos según ponderación FIUNA
				{:else}
					Análisis cualitativo y proyección secuencial fiel a las calificaciones registradas en InsWeb
				{/if}
			</span>
		</div>
		<span
			class="font-label-sm text-label-sm bg-surface-container-high text-on-surface font-semibold px-2.5 py-1 rounded self-start sm:self-center"
		>
			{#if subject.hasOfficialWeights && totalProcess !== null}
				Ponderación 50% Proceso / 50% Final
			{:else}
				Sin ponderación 50/50 forzada
			{/if}
		</span>
	</div>

	{#if subject.hasOfficialWeights && totalProcess !== null}
		<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-space-sm">
			<!-- Nota 2 (Aprobado) -->
			<div
				class="p-space-md bg-surface-container-low rounded-lg flex flex-col justify-between transition-all hover:bg-surface-container-high/80"
			>
				<div class="flex items-center justify-between">
					<span class="px-2 py-0.5 rounded text-[11px] font-bold bg-primary-container text-secondary-fixed dark:text-[#b1c7f0]">
						NOTA 2
					</span>
					<span class="font-label-sm text-label-sm text-secondary font-semibold">Aprobado</span>
				</div>
				<div class="my-space-sm flex flex-col">
					<span class="font-headline-md text-headline-md font-bold text-primary font-code-num">
						{#if isN2Reachable}
							{neededN2} / 50
						{:else}
							Inalcanzable
						{/if}
					</span>
					<span class="font-label-sm text-label-sm text-on-surface-variant">
						{isN2Reachable ? 'Mínimo para pasar' : 'Requiere habilitar (≥30 pts)'}
					</span>
				</div>
				<div class="w-full bg-surface-container-highest h-1.5 rounded-full overflow-hidden">
					<div
						class="bg-secondary h-full rounded-full transition-all duration-300"
						style="width: {isN2Reachable ? (neededN2 / 50) * 100 : 100}%"
					></div>
				</div>
				<span class="font-code-num text-code-num text-secondary text-right mt-1.5 font-medium">
					Ref. aritmética: {factibilidadN2}%
				</span>
			</div>

			<!-- Nota 3 (Bueno) -->
			<div
				class="p-space-md bg-surface-container-low rounded-lg flex flex-col justify-between transition-all hover:bg-surface-container-high/80"
			>
				<div class="flex items-center justify-between">
					<span class="px-2 py-0.5 rounded text-[11px] font-bold bg-primary-container text-secondary-fixed dark:text-[#b1c7f0]">
						NOTA 3
					</span>
					<span class="font-label-sm text-label-sm text-on-surface font-semibold">Bueno</span>
				</div>
				<div class="my-space-sm flex flex-col">
					<span class="font-headline-md text-headline-md font-bold text-primary font-code-num">
						{#if isN3Reachable}
							{neededN3} / 50
						{:else}
							Inalcanzable
						{/if}
					</span>
					<span class="font-label-sm text-label-sm text-on-surface-variant">Exigencia media</span>
				</div>
				<div class="w-full bg-surface-container-highest h-1.5 rounded-full overflow-hidden">
					<div
						class="bg-secondary h-full rounded-full transition-all duration-300"
						style="width: {isN3Reachable ? (neededN3 / 50) * 100 : 100}%"
					></div>
				</div>
				<span class="font-code-num text-code-num text-on-surface-variant text-right mt-1.5 font-medium">
					Ref. aritmética: {factibilidadN3}%
				</span>
			</div>

			<!-- Nota 4 (Muy Bueno) -->
			<div
				class="p-space-md bg-surface-container-low rounded-lg flex flex-col justify-between transition-all hover:bg-surface-container-high/80"
			>
				<div class="flex items-center justify-between">
					<span class="px-2 py-0.5 rounded text-[11px] font-bold bg-primary-container text-secondary-fixed dark:text-[#b1c7f0]">
						NOTA 4
					</span>
					<span class="font-label-sm text-label-sm text-on-surface font-semibold">Muy Bueno</span>
				</div>
				<div class="my-space-sm flex flex-col">
					<span class="font-headline-md text-headline-md font-bold text-primary font-code-num">
						{#if isN4Reachable}
							{neededN4} / 50
						{:else}
							Inalcanzable
						{/if}
					</span>
					<span class="font-label-sm text-label-sm text-on-surface-variant">Alta concentración</span>
				</div>
				<div class="w-full bg-surface-container-highest h-1.5 rounded-full overflow-hidden">
					<div
						class="bg-secondary h-full rounded-full transition-all duration-300"
						style="width: {isN4Reachable ? (neededN4 / 50) * 100 : 100}%"
					></div>
				</div>
				<span class="font-code-num text-code-num text-outline text-right mt-1.5 font-medium">
					Ref. aritmética: {factibilidadN4}%
				</span>
			</div>

			<!-- Nota 5 (Sobresaliente) -->
			<div
				class="p-space-md bg-surface-container-low/50 rounded-lg flex flex-col justify-between opacity-80"
			>
				<div class="flex items-center justify-between">
					<span
						class="px-2 py-0.5 rounded text-[11px] font-bold bg-surface-container-highest text-on-surface-variant"
					>
						NOTA 5
					</span>
					<span class="font-label-sm text-label-sm text-outline font-semibold">Sobresaliente</span>
				</div>
				<div class="my-space-sm flex flex-col">
					<span class="font-headline-md text-headline-md font-bold text-outline font-code-num">
						{#if isN5Reachable}
							{neededN5} / 50
						{:else}
							N/A
						{/if}
					</span>
					<span class="font-label-sm text-label-sm text-rose-500 font-semibold">
						{#if isN5Reachable}
							Alta exigencia (95%)
						{:else}
							No alcanzable
						{/if}
					</span>
				</div>
				<div class="w-full bg-surface-container-highest h-1.5 rounded-full overflow-hidden">
					<div
						class="bg-rose-400 h-full rounded-full transition-all duration-300"
						style="width: 100%"
					></div>
				</div>
				<span class="font-code-num text-code-num text-rose-500 text-right mt-1.5 font-medium">
					Límite por P1: {subject.p1 !== null ? (subject.p1 < 10 ? `0${subject.p1}` : subject.p1) : '--'}/{subject.p1Max}
				</span>
			</div>
		</div>
	{:else}
		<div class="p-space-md rounded-lg bg-surface-container-low border border-outline-variant/30 flex items-start gap-3">
			<span class="material-symbols-outlined text-secondary text-xl shrink-0 mt-0.5">info</span>
			<p class="font-body-sm text-body-sm text-on-surface-variant leading-relaxed">
				Ponderación oficial (50/50) no disponible en InsWeb para esta cátedra — se omite el cálculo forzoso de puntaje en examen final para mantener la fidelidad de los datos.
			</p>
		</div>
	{/if}

	<!-- Diagnóstico ML + Serie Temporal Real o Guía Local -->
	<div
		class="bg-surface-container-high/50 p-space-md rounded-lg flex items-center gap-space-md mt-space-xs"
	>
		<div
			class="w-10 h-10 rounded-full bg-secondary text-on-secondary flex items-center justify-center shrink-0 shadow-sm"
		>
			<span class="material-symbols-outlined text-xl">
				{mlPrediction || mlSequential ? 'psychology' : 'history_edu'}
			</span>
		</div>
		<div class="flex flex-col gap-1">
			{#if mlPrediction}
				<span class="font-label-sm text-label-sm font-semibold uppercase tracking-wider text-secondary">
					Diagnóstico &amp; Serie Temporal (Backend ML + LSTM)
				</span>
				<p class="font-body-md text-body-md text-on-surface">
					<strong class="font-semibold text-primary">Recomendación del Motor IA:</strong>
					{mlPrediction.resumen.recomendacion}
				</p>
				{#if mlPrediction.resumen.analisis_serie_temporal}
					<p class="font-body-sm text-body-sm text-on-surface-variant">
						{#if mlPrediction.resumen.analisis_serie_temporal.tendencia}
							<strong class="text-on-surface">Tendencia:</strong>
							{mlPrediction.resumen.analisis_serie_temporal.tendencia}.
						{/if}
						{#if mlPrediction.resumen.analisis_serie_temporal.comparativa?.analisis_comparativo}
							{mlPrediction.resumen.analisis_serie_temporal.comparativa.analisis_comparativo}
						{/if}
					</p>
				{/if}
			{:else if mlSequential}
				<span class="font-label-sm text-label-sm font-semibold uppercase tracking-wider text-secondary">
					Diagnóstico Secuencial Real ({mlSequential.hito})
				</span>
				<p class="font-body-md text-body-md text-on-surface">
					<strong class="font-semibold text-primary">Recomendación Temporal:</strong>
					{mlSequential.recomendacion}
				</p>
				<p class="font-body-sm text-body-sm text-on-surface-variant">
					<strong class="text-on-surface">Tendencia:</strong> {mlSequential.tendencia}.
					{#if mlSequential.comparativa_modelos?.consenso?.analisis_comparativo}
						{mlSequential.comparativa_modelos.consenso.analisis_comparativo}
					{/if}
				</p>
			{:else}
				<span class="font-label-sm text-label-sm font-semibold uppercase tracking-wider text-secondary">
					Guía Orientativa Local (conecta el backend FastAPI para inferencia real)
				</span>
				<p class="font-body-md text-body-md text-on-surface">
					<strong class="font-semibold text-primary">
						{subject.p1 !== null ? `Base P1 (${subject.p1}/${subject.p1Max}) / P2 (${p2Value}/${subject.p2Max}):` : 'Estado:'}
					</strong>
					{subject.historicalInsight}
				</p>
			{/if}
		</div>
	</div>
</div>
