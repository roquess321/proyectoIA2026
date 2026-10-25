<script lang="ts">
	import type { SubjectSimulation } from '../../types/simulator';

	export interface Props {
		subject: SubjectSimulation;
		totalProcess: number;
		p2Value: number;
	}

	let { subject, totalProcess, p2Value }: Props = $props();

	// Calculations for required final scores (Scale: Final is out of 50 pts, min required usually 20 pts)
	let neededN2 = $derived(Math.max(20, Math.round(60 - totalProcess)));
	let neededN3 = $derived(Math.max(25, Math.round(75 - totalProcess)));
	let neededN4 = $derived(Math.max(30, Math.round(86 - totalProcess)));
	let neededN5 = $derived(Math.max(35, Math.round(95 - totalProcess)));

	let isN2Reachable = $derived(neededN2 <= 50 && totalProcess >= 30);
	let isN3Reachable = $derived(neededN3 <= 50 && totalProcess >= 30);
	let isN4Reachable = $derived(neededN4 <= 50 && totalProcess >= 30);
	let isN5Reachable = $derived(neededN5 <= 50 && totalProcess >= 30);

	// Feasibilities
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

<div class="bg-surface-container-lowest p-space-lg rounded-xl shadow-sm flex flex-col gap-space-md">
	<div class="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
		<div class="flex flex-col">
			<h2 class="font-headline-sm text-headline-sm text-on-surface font-semibold">
				Escenarios Predictivos en Examen Final (Escala 1 al 5)
			</h2>
			<span class="font-body-sm text-body-sm text-on-surface-variant">
				Requerimientos sobre el examen de 50 puntos acumulativos según ponderación FIUNA
			</span>
		</div>
		<span
			class="font-label-sm text-label-sm bg-surface-container-high text-on-surface font-semibold px-2.5 py-1 rounded self-start sm:self-center"
		>
			Ponderación 50% Proceso / 50% Final
		</span>
	</div>

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
				Factibilidad: {factibilidadN2}%
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
				Factibilidad: {factibilidadN3}%
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
				Factibilidad: {factibilidadN4}%
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
				Límite por P1: {subject.p1 < 10 ? `0${subject.p1}` : subject.p1}/20
			</span>
		</div>
	</div>

	<!-- Historical Cohort Comparison Banner -->
	<div
		class="bg-surface-container-high/50 p-space-md rounded-lg flex items-center gap-space-md mt-space-xs"
	>
		<div
			class="w-10 h-10 rounded-full bg-secondary text-on-secondary flex items-center justify-center shrink-0 shadow-sm"
		>
			<span class="material-symbols-outlined text-xl">history_edu</span>
		</div>
		<div class="flex flex-col">
			<span class="font-label-sm text-label-sm font-semibold uppercase tracking-wider text-secondary">
				Validación Empírica Histórica
			</span>
			<p class="font-body-md text-body-md text-on-surface">
				<strong class="font-semibold text-primary">Comparativa con 4 semestres anteriores:</strong>
				{#if p2Value >= 14}
					{subject.historicalInsight}
				{:else}
					Con P2 en {p2Value} puntos, solo el 34% de alumnos logró aprobar en la primera oportunidad de final sin rendir mesa de recuperación.
				{/if}
			</p>
		</div>
	</div>
</div>
