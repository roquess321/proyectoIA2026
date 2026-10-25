<script lang="ts">
	import { academicState } from '../../academic-state.svelte';
	import { goto } from '$app/navigation';

	interface Props {
		onSimulate?: () => void;
	}

	let { onSimulate }: Props = $props();
</script>

<div class="relative overflow-hidden rounded-xl bg-surface-container-lowest p-space-md shadow-sm">
	<div class="absolute top-0 left-0 right-0 h-1 bg-secondary"></div>

	<div class="flex items-center justify-between">
		<div class="flex items-center gap-space-xs">
			<span class="material-symbols-outlined text-secondary">psychology</span>
			<span class="font-label-md text-label-md font-bold text-on-surface">
				Asistente Predictivo FIUNA
			</span>
		</div>
		<span class="rounded bg-surface-container px-2 py-0.5 font-label-sm text-label-sm font-semibold text-secondary">
			Modelo v2.4
		</span>
	</div>

	<div class="mt-space-sm p-space-sm rounded bg-surface-container-low text-on-surface font-body-sm text-body-sm">
		<p class="leading-relaxed">
			Detectada probabilidad del <strong class="text-error font-semibold font-code-num">68% de recursar</strong> en <em>Máquinas Térmicas I</em> si mantienes el ritmo del P1. El modelo calcula que dedicando 12 horas adicionales de estudio guiado en ciclos Rankine y Otto alcanzarás el puntaje de corte de 15/20.
		</p>
	</div>

	<!-- Inline Visual Mini Sparkline/Distribution -->
	<div class="mt-space-sm flex flex-col gap-1">
		<div class="flex items-center justify-between font-label-sm text-label-sm text-on-surface-variant">
			<span>Probabilidad de Aprobación Malla:</span>
			<span class="font-bold text-secondary font-code-num">84.2%</span>
		</div>
		<div class="h-2 w-full bg-surface-container rounded-full overflow-hidden flex">
			<div class="bg-secondary h-full" style="width: 84.2%;"></div>
			<div class="bg-error h-full" style="width: 15.8%;"></div>
		</div>
	</div>

	<!-- Action Button -->
	<div class="mt-space-md">
		<button
			type="button"
			class="w-full flex items-center justify-center gap-space-xs rounded bg-primary text-on-primary py-space-sm font-label-md text-label-md font-semibold hover:bg-surface-container-highest hover:text-on-surface transition-all shadow-sm"
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
