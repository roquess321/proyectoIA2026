<script lang="ts">
	import { onMount } from 'svelte';
	import { academicState } from '../../academic-state.svelte';
	import { goto } from '$app/navigation';
	import { getAvailableMLModels } from '../../services/gemini';
	import type { Course } from '../../types/academic';

	interface Props {
		courses?: Course[];
		isRealData?: boolean;
		totalAprobadas?: number;
		onSimulate?: () => void;
	}

	let {
		courses = [],
		isRealData = false,
		totalAprobadas = 0,
		onSimulate
	}: Props = $props();

	let modelsCount = $state<number | null>(null);
	let bestAucPct = $state<string | null>(null);

	onMount(async () => {
		try {
			const catalog = await getAvailableMLModels();
			modelsCount = catalog.modelos_activos.length;
			const auc =
				catalog.series_temporales?.ensamble_clasico?.[0]?.metricas?.hito_3_proceso_completo
					?.auc_roc ??
				catalog.primer_parcial?.[0]?.metricas?.random_forest?.auc_roc ??
				null;
			if (typeof auc === 'number') {
				bestAucPct = (auc * 100).toFixed(1);
			}
		} catch {
			// Mantiene respaldo local si el backend está offline
		}
	});

	let totalCourses = $derived(courses.length);
	let alertCourses = $derived(courses.filter((c) => c.status === 'alerta'));
	let safeCourses = $derived(Math.max(0, totalCourses - alertCourses.length));
	let safePercent = $derived(
		totalCourses > 0 ? Number(((safeCourses / totalCourses) * 100).toFixed(1)) : 100
	);
	let alertPercent = $derived(Number((100 - safePercent).toFixed(1)));
</script>

<div class="relative overflow-hidden rounded-xl bg-surface-container-lowest p-space-md shadow-sm">
	<div class="absolute top-0 left-0 right-0 h-1 bg-secondary"></div>

	<div class="flex items-center justify-between gap-2">
		<div class="flex items-center gap-space-xs">
			<span class="material-symbols-outlined text-secondary">psychology</span>
			<span class="font-label-md text-label-md font-bold text-on-surface">
				Asistente Predictivo FIUNA
			</span>
		</div>
		<span class="rounded bg-surface-container px-2 py-0.5 font-label-sm text-label-sm font-semibold text-secondary font-code-num">
			{#if modelsCount !== null && bestAucPct !== null}
				{modelsCount} Modelos • AUC {bestAucPct}%
			{:else}
				5 Modelos ML + LSTM
			{/if}
		</span>
	</div>

	<div class="mt-space-sm p-space-sm rounded bg-surface-container-low text-on-surface font-body-sm text-body-sm">
		{#if alertCourses.length > 0}
			<p class="leading-relaxed">
				Detectada <strong class="text-error font-semibold">alerta temprana</strong> en
				<em>{alertCourses[0].name}</em>{#if alertCourses.length > 1} y {alertCourses.length - 1} cátedra(s) más{/if}.
				Ejecuta el simulador para calcular la probabilidad real con los 5 modelos de IA (clásicos y serie temporal LSTM).
			</p>
		{:else if totalCourses > 0}
			<p class="leading-relaxed">
				Seguimiento sobre <strong class="font-semibold font-code-num">{totalCourses}</strong> asignaturas
				en curso ({isRealData ? 'datos reales InsWeb' : 'modo demostración'}) y
				<strong class="font-semibold font-code-num">{totalAprobadas}</strong> aprobadas.
				Usa el simulador para evaluar escenarios reales de 2do Parcial y final con ML + LSTM.
			</p>
		{:else}
			<p class="leading-relaxed">
				Motor predictivo listo para evaluar tus evaluaciones parciales y de taller mediante modelos clásicos y red neuronal LSTM.
			</p>
		{/if}
	</div>

	<!-- Barra proporcional real de cátedras sin alerta temprana -->
	<div class="mt-space-sm flex flex-col gap-1">
		<div class="flex items-center justify-between font-label-sm text-label-sm text-on-surface-variant">
			<span>Cátedras sin alerta temprana:</span>
			<span class="font-bold text-secondary font-code-num">
				{safePercent}% ({safeCourses}/{totalCourses})
			</span>
		</div>
		<div class="h-2 w-full bg-surface-container rounded-full overflow-hidden flex">
			<div class="bg-secondary h-full transition-all duration-500" style="width: {safePercent}%;"></div>
			<div class="bg-error h-full transition-all duration-500" style="width: {alertPercent}%;"></div>
		</div>
	</div>

	<!-- Action Button -->
	<div class="mt-space-md">
		<button
			type="button"
			class="w-full flex items-center justify-center gap-space-xs rounded bg-primary text-on-primary py-space-sm font-label-md text-label-md font-semibold hover:bg-surface-container-highest hover:text-on-surface transition-all shadow-sm cursor-pointer"
			onclick={() => {
				if (onSimulate) {
					onSimulate();
				} else {
					academicState.activeNav = 'agente-ia-pronosticos';
					goto('/agente-ia-pronosticos');
				}
			}}
		>
			<span class="material-symbols-outlined text-base">batch_prediction</span>
			Simular Escenarios con Agente IA
		</button>
	</div>
</div>
