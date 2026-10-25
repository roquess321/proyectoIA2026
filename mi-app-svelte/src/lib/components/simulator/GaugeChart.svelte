<script lang="ts">
	export interface Props {
		probability: number;
		totalProcess: number;
	}

	let { probability, totalProcess }: Props = $props();

	const circumference = 314.159;

	let strokeOffset = $derived(
		circumference - (circumference * Math.min(100, Math.max(0, probability))) / 100
	);

	let progressPercent = $derived(Math.min(100, Math.max(0, (totalProcess / 50) * 100)));

	let deltaHabilitacion = $derived(totalProcess - 30.0);

	let riskInfo = $derived.by(() => {
		if (probability >= 75) {
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
</script>

<div
	class="bg-surface-container-lowest p-space-lg rounded-xl shadow-sm flex flex-col md:flex-row gap-space-lg items-center relative overflow-hidden"
>
	<div
		class="absolute -right-16 -top-16 w-48 h-48 rounded-full bg-secondary-fixed/20 blur-2xl pointer-events-none"
	></div>

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
				{probability}%
			</span>
			<span class="font-label-sm text-label-sm font-semibold tracking-wider uppercase text-outline mt-1">
				Éxito Est.
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
				<span class="material-symbols-outlined text-xs text-secondary">update</span>
				Simulación en vivo
			</span>
		</div>

		<p class="font-body-md text-body-md text-on-surface leading-relaxed mt-1">
			Tu trayectoria actual exige un puntaje mínimo calibrado en el Segundo Parcial para no
			comprometer el margen en la primera oportunidad de examen final.
		</p>

		<!-- Micro Score Progress Bar -->
		<div class="bg-surface-container-low p-space-sm rounded-lg flex flex-col gap-1.5 mt-space-xs">
			<div class="flex justify-between items-center text-on-surface font-label-sm text-label-sm">
				<span class="font-medium text-on-surface-variant">
					Puntaje de Proceso Acumulado Estimado
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

			<div class="flex justify-between items-center text-outline text-[11px] font-code-num">
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
	</div>
</div>
