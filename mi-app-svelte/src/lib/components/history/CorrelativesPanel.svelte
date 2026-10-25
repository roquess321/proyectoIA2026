<script lang="ts">
	import type { AcademicRecord } from '../../types/academic-history';

	export interface Props {
		selectedRecord: AcademicRecord;
	}

	let { selectedRecord }: Props = $props();
</script>

<div
	class="bg-surface-container-lowest p-space-lg rounded-xl shadow-sm flex flex-col gap-space-md sticky top-20 border border-outline-variant/30"
>
	<!-- Header -->
	<div class="flex items-center justify-between pb-space-sm border-b border-outline-variant/20">
		<div class="flex items-center gap-space-xs">
			<span class="material-symbols-outlined text-secondary text-xl">account_tree</span>
			<h2 class="font-headline-sm text-headline-sm text-primary font-bold">
				Visualizador de Correlativas
			</h2>
		</div>
		<span class="bg-secondary-fixed text-on-secondary-fixed font-label-sm text-label-sm px-2 py-0.5 rounded font-semibold">
			Modo Predictivo
		</span>
	</div>

	<!-- Selected Course Summary Card -->
	<div class="p-space-md bg-surface-container-low rounded-lg flex flex-col gap-1 border border-outline-variant/20">
		<div class="flex items-center justify-between">
			<span class="font-code-num text-code-num font-bold text-secondary text-base">
				{selectedRecord.code}
			</span>
			<span
				class="font-label-sm text-label-sm px-2 py-0.5 rounded font-semibold {selectedRecord.status ===
				'APROBADA'
					? 'bg-emerald-100 text-emerald-900 dark:bg-emerald-950/80 dark:text-emerald-300'
					: selectedRecord.status === 'CURSO'
						? 'bg-secondary-fixed text-on-secondary-fixed'
						: 'bg-surface-container text-on-surface-variant'}"
			>
				{selectedRecord.status === 'APROBADA'
					? 'Aprobada'
					: selectedRecord.status === 'CURSO'
						? 'En Curso'
						: 'Pendiente'}
			</span>
		</div>
		<h3 class="font-headline-sm text-headline-sm text-primary font-bold">
			{selectedRecord.name}
		</h3>
		<span class="font-body-sm text-body-sm text-on-surface-variant">
			Dpto. de {selectedRecord.departmentName} • {selectedRecord.semester}
		</span>
	</div>

	<!-- Prerrequisitos Requeridos -->
	<div class="flex flex-col gap-space-xs">
		<span class="font-label-sm text-label-sm uppercase font-semibold text-on-surface-variant tracking-wider">
			Prerrequisitos Requeridos
		</span>
		<div class="flex flex-col gap-2 mt-1">
			{#if selectedRecord.prerequisites.length > 0}
				{#each selectedRecord.prerequisites as prereq}
					<div
						class="flex items-center justify-between p-space-sm bg-surface-container-lowest rounded shadow-sm border border-outline-variant/20"
					>
						<div class="flex items-center gap-2">
							<span
								class="material-symbols-outlined text-sm {prereq.includes('Aprobada') ||
								prereq.includes('Bachillerato') ||
								prereq.includes('Directo')
									? 'text-emerald-500'
									: 'text-secondary'}"
							>
								{prereq.includes('Aprobada') ||
								prereq.includes('Bachillerato') ||
								prereq.includes('Directo')
									? 'check_circle'
									: 'pending'}
							</span>
							<span class="font-body-sm text-body-sm font-medium text-on-surface">
								{prereq}
							</span>
						</div>
						<span
							class="bg-surface-container-high text-on-surface font-label-sm text-label-sm px-2 py-0.5 rounded"
						>
							{prereq.includes('Aprobada')
								? 'Aprobada'
								: prereq.includes('En curso') || prereq.includes('Simultáneo')
									? 'En Curso'
									: 'Requisito'}
						</span>
					</div>
				{/each}
			{:else}
				<span class="text-body-sm text-on-surface-variant italic">
					Sin correlativas previas requeridas.
				</span>
			{/if}
		</div>
	</div>

	<!-- Cátedras que Desbloquea -->
	<div class="flex flex-col gap-space-xs">
		<span class="font-label-sm text-label-sm uppercase font-semibold text-on-surface-variant tracking-wider">
			Cátedras que Desbloquea
		</span>
		<div class="flex flex-col gap-2 mt-1">
			{#if selectedRecord.unlocks.length > 0}
				{#each selectedRecord.unlocks as unlock}
					<div
						class="p-space-sm bg-surface-container-low rounded flex items-center justify-between border border-outline-variant/20"
					>
						<span class="font-body-sm text-body-sm text-on-surface font-medium">
							{unlock}
						</span>
						<span class="font-code-num text-code-num text-on-surface-variant font-medium">
							Prerrequisito
						</span>
					</div>
				{/each}
			{:else}
				<span class="text-body-sm text-on-surface-variant italic">
					Cátedra terminal del ciclo.
				</span>
			{/if}
		</div>
	</div>

	<!-- Pronóstico del Agente IA -->
	{#if selectedRecord.aiInsight}
		<div class="p-space-md bg-surface-container-high rounded-lg flex flex-col gap-space-xs border border-outline-variant/30">
			<div class="flex items-center gap-2 text-on-secondary-container">
				<span class="material-symbols-outlined text-sm text-secondary">psychology</span>
				<span class="font-label-sm text-label-sm uppercase font-bold tracking-wider text-secondary">
					Pronóstico del Agente IA
				</span>
			</div>
			<p class="font-body-sm text-body-sm text-on-surface">
				{selectedRecord.aiInsight.text}
			</p>
			<div class="flex items-center justify-between pt-1">
				<span class="font-label-md text-label-md text-primary font-bold">
					Desbloqueo Proyectado:
				</span>
				<span
					class="bg-primary text-on-primary font-code-num text-code-num font-bold px-2 py-0.5 rounded"
				>
					{selectedRecord.aiInsight.projectedUnlock}
				</span>
			</div>
			<span class="font-label-sm text-label-sm text-on-surface-variant">
				Probabilidad de habilitación según historial: {selectedRecord.aiInsight.probability}
			</span>
		</div>
	{/if}
</div>
