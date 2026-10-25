<script lang="ts">
	import type { SubjectSimulation } from '../../types/simulator';

	export interface Props {
		subject: SubjectSimulation;
		p2Value: number;
		onP2Change: (value: number) => void;
	}

	let { subject, p2Value, onP2Change }: Props = $props();

	let p1Percentage = $derived(Math.round((subject.p1 / subject.p1Max) * 100));
	let labPercentage = $derived(Math.round((subject.lab / subject.labMax) * 100));
</script>

<div class="bg-surface-container-lowest p-space-lg rounded-xl shadow-sm flex flex-col gap-space-md">
	<div class="flex items-center justify-between pb-space-xs">
		<div class="flex items-center gap-space-xs">
			<span class="material-symbols-outlined text-secondary text-xl">tune</span>
			<h2 class="font-headline-sm text-headline-sm text-on-surface font-semibold">
				Matriz Paramétrica de Calificación
			</h2>
		</div>
		<span
			class="font-label-sm text-label-sm text-on-surface-variant bg-surface-container-high px-2 py-0.5 rounded"
		>
			{subject.catedra} • Semestre 2024-2
		</span>
	</div>

	<div class="grid grid-cols-1 md:grid-cols-2 gap-space-md">
		<!-- Primer Parcial (Fixed / Scraped) -->
		<div class="bg-surface-container-low p-space-md rounded-lg flex flex-col justify-between">
			<div class="flex items-center justify-between">
				<span class="font-label-md text-label-md font-semibold text-on-surface">
					Primer Parcial (P1)
				</span>
				<span class="flex items-center gap-1 font-label-sm text-label-sm text-outline">
					<span class="material-symbols-outlined text-sm">lock</span>
					InsWeb Sync
				</span>
			</div>
			<div class="my-space-md flex items-baseline justify-between">
				<span class="font-headline-lg text-headline-lg font-bold text-primary font-code-num">
					{subject.p1 < 10 ? `0${subject.p1.toFixed(1)}` : subject.p1.toFixed(1)}
					<span class="text-on-surface-variant font-normal text-headline-sm">
						/ {subject.p1Max}
					</span>
				</span>
				<span
					class="px-2 py-0.5 rounded text-[11px] font-semibold {p1Percentage < 60
						? 'bg-rose-100 text-rose-900 dark:bg-rose-950/80 dark:text-rose-200'
						: 'bg-emerald-100 text-emerald-900 dark:bg-emerald-950/80 dark:text-emerald-200'}"
				>
					{p1Percentage}% ({p1Percentage < 60 ? 'Bajo' : 'Óptimo'})
				</span>
			</div>
			<div class="flex items-center justify-between text-outline font-body-sm text-body-sm">
				<span>Examen Rendido: {subject.p1Date}</span>
				<span class="font-code-num text-code-num">Cátedra Media: {subject.p1ClassAverage}</span>
			</div>
		</div>

		<!-- Laboratorio / Informes Técnicos -->
		<div class="bg-surface-container-low p-space-md rounded-lg flex flex-col justify-between">
			<div class="flex items-center justify-between">
				<span class="font-label-md text-label-md font-semibold text-on-surface">
					Laboratorio &amp; Informes
				</span>
				<span class="flex items-center gap-1 font-label-sm text-label-sm text-secondary font-medium">
					<span class="material-symbols-outlined text-sm">verified</span>
					Registrado
				</span>
			</div>
			<div class="my-space-md flex items-baseline justify-between">
				<span class="font-headline-lg text-headline-lg font-bold text-primary font-code-num">
					{subject.lab < 10 ? `0${subject.lab.toFixed(1)}` : subject.lab.toFixed(1)}
					<span class="text-on-surface-variant font-normal text-headline-sm">
						/ {subject.labMax}
					</span>
				</span>
				<span
					class="px-2 py-0.5 rounded text-[11px] font-semibold bg-emerald-100 text-emerald-900 dark:bg-emerald-950/80 dark:text-emerald-200"
				>
					{labPercentage}% (Óptimo)
				</span>
			</div>
			<div class="flex items-center justify-between text-outline font-body-sm text-body-sm">
				<span>{subject.labSessionsEvaluated} Ensayos Evaluados</span>
				<span class="font-code-num text-code-num">
					Faltan: {subject.labPendingDeliveries} entregas
				</span>
			</div>
		</div>

		<!-- Segundo Parcial (Simulador Slider - Full Width within subgrid) -->
		<div
			class="md:col-span-2 bg-surface-container-high/60 p-space-md rounded-lg flex flex-col gap-space-sm shadow-xs border border-outline-variant/30"
		>
			<div class="flex items-center justify-between">
				<div class="flex items-center gap-space-xs">
					<span class="material-symbols-outlined text-secondary text-lg">sliders</span>
					<span class="font-label-md text-label-md font-semibold text-on-surface">
						Segundo Parcial (P2) - Proyección Dinámica
					</span>
				</div>
				<div class="flex items-center gap-2">
					<span class="font-label-sm text-label-sm text-on-surface-variant font-medium">
						Ajuste manual:
					</span>
					<span
						class="font-headline-sm text-headline-sm font-bold bg-primary-container px-2.5 py-0.5 rounded font-code-num text-secondary-fixed dark:text-[#b1c7f0]"
					>
						{p2Value} / 20
					</span>
				</div>
			</div>

			<div class="py-2">
				<input
					type="range"
					min="0"
					max="20"
					step="1"
					class="w-full h-2.5 bg-surface-container-highest rounded-lg appearance-none cursor-pointer accent-secondary focus:outline-none"
					value={p2Value}
					oninput={(e) => onP2Change(parseFloat(e.currentTarget.value))}
				/>
				<div class="flex justify-between text-[11px] font-code-num text-outline mt-1.5 px-0.5">
					<button
						type="button"
						class="hover:text-secondary cursor-pointer transition-colors"
						onclick={() => onP2Change(0)}
					>
						0 pts (Catastrófico)
					</button>
					<button
						type="button"
						class="hover:text-secondary cursor-pointer transition-colors"
						onclick={() => onP2Change(10)}
					>
						10 pts (50%)
					</button>
					<button
						type="button"
						class="hover:text-secondary cursor-pointer transition-colors"
						onclick={() => onP2Change(13)}
					>
						12.5 pts (Mín. Sugerido)
					</button>
					<button
						type="button"
						class="hover:text-secondary cursor-pointer transition-colors"
						onclick={() => onP2Change(16)}
					>
						16 pts (Excelente)
					</button>
					<button
						type="button"
						class="hover:text-secondary cursor-pointer transition-colors"
						onclick={() => onP2Change(20)}
					>
						20 pts (Perfecto)
					</button>
				</div>
			</div>

			<div
				class="flex items-center justify-between bg-surface-container-lowest p-space-sm rounded-lg text-on-surface"
			>
				<span class="font-body-sm text-body-sm text-on-surface-variant flex items-center gap-1">
					<span class="material-symbols-outlined text-base text-secondary">insights</span>
					Impacto en Habilitación:
				</span>
				<span class="font-label-md text-label-md font-semibold text-secondary">
					Aporta +{p2Value.toFixed(1)} pts al proceso total
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
					<span class="material-symbols-outlined text-xl">event_available</span>
				</div>
				<div class="flex flex-col">
					<span class="font-label-md text-label-md font-semibold text-on-surface">
						Asistencia a Cátedra &amp; Talleres
					</span>
					<span class="font-body-sm text-body-sm text-on-surface-variant">
						{subject.attendedSessions} asistencias registradas de {subject.totalSessions} sesiones dictadas
					</span>
				</div>
			</div>
			<div class="flex items-center gap-space-md w-full md:w-auto justify-end">
				<div class="flex flex-col text-right">
					<span class="font-headline-sm text-headline-sm font-bold text-primary font-code-num">
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
