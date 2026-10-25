<script lang="ts">
	import type { HistoryStatsData } from '../../types/academic-history';

	export interface Props {
		stats: HistoryStatsData;
	}

	let { stats }: Props = $props();
</script>

<div class="grid grid-cols-2 md:grid-cols-5 gap-space-sm">
	<!-- Total Asignaturas -->
	<div
		class="bg-surface-container-lowest p-space-md rounded-xl shadow-sm flex flex-col justify-between"
	>
		<div class="flex items-center justify-between">
			<span class="font-label-sm text-label-sm uppercase text-on-surface-variant font-semibold">
				Total Asignaturas
			</span>
			<span class="material-symbols-outlined text-secondary text-lg">library_books</span>
		</div>
		<div class="mt-2">
			<span class="font-headline-lg text-headline-lg text-primary leading-none font-bold font-code-num">
				{stats.totalSubjects}
			</span>
			<span class="font-code-num text-code-num text-on-surface-variant block mt-1">
				100% Carga Lectiva
			</span>
		</div>
	</div>

	<!-- Aprobadas -->
	<div
		class="bg-surface-container-lowest p-space-md rounded-xl shadow-sm flex flex-col justify-between"
	>
		<div class="flex items-center justify-between">
			<span class="font-label-sm text-label-sm uppercase text-on-surface-variant font-semibold">
				Aprobadas
			</span>
			<span class="material-symbols-outlined text-secondary text-lg">verified</span>
		</div>
		<div class="mt-2 flex items-baseline gap-2">
			<span class="font-headline-lg text-headline-lg text-primary leading-none font-bold font-code-num">
				{stats.approvedCount}
			</span>
			<span class="font-code-num text-code-num text-secondary font-semibold">
				{stats.approvedPercentage}%
			</span>
		</div>
	</div>

	<!-- En Curso -->
	<div
		class="bg-surface-container-lowest p-space-md rounded-xl shadow-sm flex flex-col justify-between"
	>
		<div class="flex items-center justify-between">
			<span class="font-label-sm text-label-sm uppercase text-on-surface-variant font-semibold">
				En Curso
			</span>
			<span class="material-symbols-outlined text-secondary text-lg">timelapse</span>
		</div>
		<div class="mt-2 flex items-baseline gap-2">
			<span class="font-headline-lg text-headline-lg text-primary leading-none font-bold font-code-num">
				{stats.inProgressCount}
			</span>
			<span class="font-code-num text-code-num text-on-surface-variant">
				{stats.inProgressCredits} Créditos
			</span>
		</div>
	</div>

	<!-- Pendientes -->
	<div
		class="bg-surface-container-lowest p-space-md rounded-xl shadow-sm flex flex-col justify-between"
	>
		<div class="flex items-center justify-between">
			<span class="font-label-sm text-label-sm uppercase text-on-surface-variant font-semibold">
				Pendientes
			</span>
			<span class="material-symbols-outlined text-secondary text-lg">pending_actions</span>
		</div>
		<div class="mt-2 flex items-baseline gap-2">
			<span class="font-headline-lg text-headline-lg text-primary leading-none font-bold font-code-num">
				{stats.pendingCount}
			</span>
			<span class="font-code-num text-code-num text-on-surface-variant">Plan Restante</span>
		</div>
	</div>

	<!-- Promedio Ponderado -->
	<div
		class="col-span-2 md:col-span-1 bg-surface-container-high p-space-md rounded-xl shadow-sm flex flex-col justify-between"
	>
		<div class="flex items-center justify-between">
			<span class="font-label-sm text-label-sm uppercase text-on-secondary-container font-semibold">
				Promedio Ponderado
			</span>
			<span class="material-symbols-outlined text-secondary text-lg">grade</span>
		</div>
		<div class="mt-2">
			<span class="font-headline-lg text-headline-lg text-primary leading-none font-bold font-code-num">
				{stats.averageGrade.toFixed(2)}
			</span>
			<div class="flex items-center gap-1 mt-1">
				<span class="material-symbols-outlined text-xs text-secondary">trending_up</span>
				<span class="font-code-num text-code-num text-on-surface-variant font-medium">
					{stats.deltaCohort}
				</span>
			</div>
		</div>
	</div>
</div>
