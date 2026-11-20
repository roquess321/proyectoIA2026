<script lang="ts">
	import type { SubjectSimulation } from "../../types/simulator";

	export interface Props {
		subject: SubjectSimulation;
		p2Value: number;
		includeP2Projection?: boolean;
		onP2Change: (value: number) => void;
		onToggleP2Projection?: (enabled: boolean) => void;
	}

	let {
		subject,
		p2Value,
		includeP2Projection = true,
		onP2Change,
		onToggleP2Projection
	}: Props = $props();

	let p1Percentage = $derived(
		subject.p1 !== null && subject.p1Max > 0
			? Math.round((subject.p1 / subject.p1Max) * 100)
			: null
	);
	let labPercentage = $derived(
		subject.hasLab && subject.lab !== null && subject.labMax > 0
			? Math.round((subject.lab / subject.labMax) * 100)
			: null
	);

	function handleSliderInput(val: number): void {
		if (!includeP2Projection && onToggleP2Projection) {
			onToggleP2Projection(true);
		}
		onP2Change(val);
	}
</script>

<div
	class="bg-surface-container-lowest p-4 sm:p-space-lg rounded-xl shadow-sm flex flex-col gap-space-md"
>
	<div
		class="flex flex-col sm:flex-row sm:items-center justify-between gap-1 pb-space-xs"
	>
		<div class="flex items-center gap-space-xs">
			<span class="material-symbols-outlined text-secondary text-xl"
				>tune</span
			>
			<h2
				class="font-headline-sm text-base sm:text-headline-sm text-on-surface font-semibold"
			>
				Matriz Paramétrica de Calificación
			</h2>
		</div>
		<span
			class="font-label-sm text-xs sm:text-label-sm text-on-surface-variant bg-surface-container-high px-2 py-0.5 rounded self-start sm:self-auto"
		>
			{subject.catedra} • Escala 0–{subject.p1Max}
		</span>
	</div>

	<div class="grid grid-cols-1 md:grid-cols-2 gap-space-md">
		<!-- Primer Parcial (Real de SQLite o Demo) -->
		<div
			class="bg-surface-container-low p-space-md rounded-lg flex flex-col justify-between"
		>
			<div class="flex items-center justify-between">
				<span
					class="font-label-md text-label-md font-semibold text-on-surface"
				>
					Primer Parcial (P1)
				</span>
				<span
					class="flex items-center gap-1 font-label-sm text-label-sm text-outline"
				>
					<span class="material-symbols-outlined text-sm">lock</span>
					InsWeb Sync
				</span>
			</div>
			<div class="my-space-md flex items-baseline justify-between gap-2">
				{#if subject.p1 !== null && p1Percentage !== null}
					<span
						class="font-headline-lg text-headline-lg font-bold text-primary font-code-num"
					>
						{subject.p1 < 10
							? `0${subject.p1.toFixed(1)}`
							: subject.p1.toFixed(1)}
						<span
							class="text-on-surface-variant font-normal text-headline-sm"
						>
							/ {subject.p1Max}
						</span>
					</span>
					<span
						class="px-2 py-0.5 rounded text-[11px] font-semibold {p1Percentage <
						60
							? 'bg-rose-100 text-rose-900 dark:bg-rose-950/80 dark:text-rose-200'
							: 'bg-emerald-100 text-emerald-900 dark:bg-emerald-950/80 dark:text-emerald-200'}"
					>
						{p1Percentage}% ({p1Percentage < 60 ? "Bajo" : "Óptimo"})
					</span>
				{:else}
					<div class="flex flex-col">
						<span class="font-headline-md text-headline-md font-bold text-on-surface-variant">
							Pendiente
						</span>
						<span class="text-xs text-outline">Sin nota en InsWeb</span>
					</div>
					<span
						class="px-2 py-0.5 rounded text-[11px] font-semibold bg-surface-container-high text-on-surface-variant"
					>
						Sin rendir
					</span>
				{/if}
			</div>
			<div
				class="flex items-center justify-between text-outline font-body-sm text-body-sm gap-2"
			>
				<span>{subject.p1Date}</span>
				<span class="font-code-num text-code-num"
					>Media ref. dataset: {subject.p1ClassAverage}/{subject.p1Max}</span
				>
			</div>
		</div>

		<!-- Laboratorio / Trabajo Práctico (Solo si la materia lo posee) -->
		<div
			class="bg-surface-container-low p-space-md rounded-lg flex flex-col justify-between"
		>
			<div class="flex items-center justify-between gap-2">
				<span
					class="font-label-md text-label-md font-semibold text-on-surface truncate"
				>
					{subject.labLabel ?? "Laboratorio & TP"}
				</span>
				<span
					class="flex items-center gap-1 font-label-sm text-label-sm {subject.hasLab ? 'text-secondary' : 'text-outline'} font-medium shrink-0"
				>
					<span class="material-symbols-outlined text-sm">
						{subject.hasLab ? "verified" : "block"}
					</span>
					{subject.hasLab ? "Registrado" : "No aplica"}
				</span>
			</div>
			<div class="my-space-md flex items-baseline justify-between gap-2">
				{#if !subject.hasLab}
					<div class="flex flex-col">
						<span class="font-headline-md text-headline-md font-bold text-on-surface-variant">
							No posee
						</span>
						<span class="text-xs text-outline">No aplica en esta materia</span>
					</div>
					<span
						class="px-2 py-0.5 rounded text-[11px] font-semibold bg-surface-container-high text-on-surface-variant"
					>
						Sin Lab/TP
					</span>
				{:else if subject.lab === null || labPercentage === null}
					<div class="flex flex-col">
						<span class="font-headline-md text-headline-md font-bold text-on-surface-variant">
							Pendiente
						</span>
						<span class="text-xs text-outline">
							{subject.labLabel ?? "TP / Laboratorio"} sin puntaje aún
						</span>
					</div>
					<span
						class="px-2 py-0.5 rounded text-[11px] font-semibold bg-amber-100 text-amber-900 dark:bg-amber-950/80 dark:text-amber-200"
					>
						Pendiente
					</span>
				{:else}
					<span
						class="font-headline-lg text-headline-lg font-bold text-primary font-code-num"
					>
						{subject.lab < 10
							? `0${subject.lab.toFixed(1)}`
							: subject.lab.toFixed(1)}
						<span
							class="text-on-surface-variant font-normal text-headline-sm"
						>
							/ {subject.labMax}
						</span>
					</span>
					<span
						class="px-2 py-0.5 rounded text-[11px] font-semibold {labPercentage <
						60
							? 'bg-rose-100 text-rose-900 dark:bg-rose-950/80 dark:text-rose-200'
							: 'bg-emerald-100 text-emerald-900 dark:bg-emerald-950/80 dark:text-emerald-200'}"
					>
						{labPercentage}% ({labPercentage < 60 ? "Bajo" : "Óptimo"})
					</span>
				{/if}
			</div>
			<div
				class="flex items-center justify-between text-outline font-body-sm text-body-sm"
			>
				{#if !subject.hasLab}
					<span>Sin evaluaciones prácticas registradas en InsWeb</span>
				{:else}
					<span>{subject.labSessionsEvaluated} Registro(s) en periodo</span>
					<span class="font-code-num text-code-num">
						Pendientes: {subject.labPendingDeliveries}
					</span>
				{/if}
			</div>
		</div>

		<!-- Segundo Parcial (Simulador Slider - Full Width within subgrid) -->
		<div
			class="md:col-span-2 bg-surface-container-high/60 p-space-md rounded-lg flex flex-col gap-space-sm shadow-xs border border-outline-variant/30"
		>
			<div class="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
				<div class="flex items-center gap-space-xs">
					<span
						class="material-symbols-outlined text-secondary text-lg"
						>sliders</span
					>
					<span
						class="font-label-md text-label-md font-semibold text-on-surface"
					>
						Segundo Parcial (P2) - {subject.p2 !== null ? "Registrado / Editable" : "Proyección Dinámica"}
					</span>
				</div>
				<div class="flex flex-wrap items-center gap-2">
					{#if !subject.hasOfficialWeights && subject.p2 === null && onToggleP2Projection}
						<div class="inline-flex rounded-lg bg-surface-container p-0.5 border border-outline-variant/30">
							<button
								type="button"
								class="px-2.5 py-1 rounded text-[11px] font-semibold transition-colors cursor-pointer {!includeP2Projection
									? 'bg-primary text-on-primary shadow-2xs'
									: 'text-on-surface-variant hover:text-on-surface'}"
								onclick={() => onToggleP2Projection(false)}
							>
								Evaluar solo P1 (Hito 1)
							</button>
							<button
								type="button"
								class="px-2.5 py-1 rounded text-[11px] font-semibold transition-colors cursor-pointer {includeP2Projection
									? 'bg-secondary text-on-secondary shadow-2xs'
									: 'text-on-surface-variant hover:text-on-surface'}"
								onclick={() => onToggleP2Projection(true)}
							>
								Proyectar P2
							</button>
						</div>
					{/if}
					<span
						class="font-headline-sm text-headline-sm font-bold bg-primary-container px-2.5 py-0.5 rounded font-code-num text-secondary-fixed dark:text-[#b1c7f0]"
					>
						{includeP2Projection || subject.p2 !== null ? `${p2Value} / ${subject.p2Max}` : "Sin proyectar"}
					</span>
				</div>
			</div>

			<div class="py-2">
				<input
					type="range"
					min="0"
					max={subject.p2Max}
					step="1"
					class="w-full h-2.5 bg-surface-container-highest rounded-lg appearance-none cursor-pointer accent-secondary focus:outline-none"
					value={p2Value}
					oninput={(e) =>
						handleSliderInput(parseFloat(e.currentTarget.value))}
				/>
				<div
					class="flex justify-between text-[11px] font-code-num text-outline mt-1.5 px-0.5 flex-wrap gap-1"
				>
					{#if subject.p2Max === 100}
						<button type="button" class="hover:text-secondary cursor-pointer transition-colors" onclick={() => handleSliderInput(0)}>
							0 pts
						</button>
						<button type="button" class="hover:text-secondary cursor-pointer transition-colors" onclick={() => handleSliderInput(40)}>
							40 pts
						</button>
						<button type="button" class="hover:text-secondary cursor-pointer transition-colors" onclick={() => handleSliderInput(60)}>
							60 pts (60%)
						</button>
						<button type="button" class="hover:text-secondary cursor-pointer transition-colors" onclick={() => handleSliderInput(80)}>
							80 pts
						</button>
						<button type="button" class="hover:text-secondary cursor-pointer transition-colors" onclick={() => handleSliderInput(100)}>
							100 pts
						</button>
					{:else}
						<button type="button" class="hover:text-secondary cursor-pointer transition-colors" onclick={() => handleSliderInput(0)}>
							0 pts (Catastrófico)
						</button>
						<button type="button" class="hover:text-secondary cursor-pointer transition-colors" onclick={() => handleSliderInput(10)}>
							10 pts (50%)
						</button>
						<button type="button" class="hover:text-secondary cursor-pointer transition-colors" onclick={() => handleSliderInput(13)}>
							13 pts (Mín. Sugerido)
						</button>
						<button type="button" class="hover:text-secondary cursor-pointer transition-colors" onclick={() => handleSliderInput(16)}>
							16 pts (Excelente)
						</button>
						<button type="button" class="hover:text-secondary cursor-pointer transition-colors" onclick={() => handleSliderInput(20)}>
							20 pts (Perfecto)
						</button>
					{/if}
				</div>
			</div>

			<div
				class="flex items-center justify-between bg-surface-container-lowest p-space-sm rounded-lg text-on-surface"
			>
				<span
					class="font-body-sm text-body-sm text-on-surface-variant flex items-center gap-1"
				>
					<span
						class="material-symbols-outlined text-base text-secondary"
						>insights</span
					>
					Modo de Evaluación:
				</span>
				<span
					class="font-label-md text-label-md font-semibold text-secondary text-right"
				>
					{#if subject.hasOfficialWeights}
						Aporta +{p2Value.toFixed(1)} pts al proceso total
					{:else if includeP2Projection || subject.p2 !== null}
						Escala real 0–100 (sin ponderación forzada 50/50)
					{:else}
						Modo Hito 1: evaluando solo con notas reales registradas
					{/if}
				</span>
			</div>
		</div>

		<!-- Asistencia Registrada Status Bar -->
		<div
			class="md:col-span-2 bg-surface-container-low p-space-md rounded-lg flex flex-col md:flex-row items-center justify-between gap-space-md"
		>
			<div class="flex items-center gap-space-md w-full md:w-auto">
				<div
					class="w-10 h-10 rounded bg-emerald-100 text-emerald-800 dark:bg-emerald-950/80 dark:text-emerald-300 flex items-center justify-center shrink-0"
				>
					<span class="material-symbols-outlined text-xl"
						>event_available</span
					>
				</div>
				<div class="flex flex-col">
					<span
						class="font-label-md text-label-md font-semibold text-on-surface"
					>
						Asistencia a Cátedra &amp; Talleres
					</span>
					<span
						class="font-body-sm text-body-sm text-on-surface-variant"
					>
						{subject.attendedSessions} asistencias de referencia de {subject.totalSessions}
						sesiones (no exportado por InsWeb)
					</span>
				</div>
			</div>
			<div
				class="flex items-center gap-space-md w-full md:w-auto justify-end"
			>
				<div class="flex flex-col text-right">
					<span
						class="font-headline-sm text-headline-sm font-bold text-primary font-code-num"
					>
						{subject.attendanceRate.toFixed(1)}%
					</span>
					<span
						class="font-label-sm text-label-sm text-emerald-700 dark:text-emerald-400 font-semibold"
					>
						{subject.attendanceArticle}
					</span>
				</div>
			</div>
		</div>
	</div>
</div>
