<script lang="ts">
	import type { Course } from '../../types/academic';
	import CourseCard from './CourseCard.svelte';

	interface Props {
		courses: Course[];
		onSimulatePlan?: (course: Course) => void;
	}

	let { courses, onSimulatePlan }: Props = $props();

	let filterMode = $state<'todas' | 'habilitadas' | 'alerta' | 'en_curso'>('todas');
	let isFilterMenuOpen = $state(false);

	let filteredCourses = $derived(
		courses.filter((c) => {
			if (filterMode === 'todas') return true;
			if (filterMode === 'habilitadas') return c.status === 'habilitado' || c.status === 'excelencia';
			if (filterMode === 'alerta') return c.status === 'alerta';
			if (filterMode === 'en_curso') return c.status === 'en_curso' || c.status === 'favorable';
			return true;
		})
	);
</script>

<div class="flex flex-col gap-space-md">
	<div
		class="flex items-center justify-between bg-surface-container-lowest px-space-md py-space-sm rounded-lg shadow-sm"
	>
		<div class="flex items-center gap-space-xs">
			<span class="material-symbols-outlined text-secondary text-lg">menu_book</span>
			<h2 class="font-headline-sm text-headline-sm text-on-surface font-bold">Cátedras En Curso</h2>
			<span
				class="ml-2 rounded-full bg-surface-container px-2 py-0.5 font-label-sm text-label-sm font-semibold text-on-surface-variant"
			>
				{filteredCourses.length} Registradas
			</span>
		</div>

		<div class="relative">
			<button
				type="button"
				class="font-label-sm text-label-sm text-secondary hover:text-on-surface font-semibold flex items-center gap-1 transition-colors px-2 py-1 rounded hover:bg-surface-container"
				onclick={() => (isFilterMenuOpen = !isFilterMenuOpen)}
			>
				<span class="material-symbols-outlined text-sm">tune</span>
				Filtrar Criterios
			</button>

			{#if isFilterMenuOpen}
				<div
					class="absolute right-0 mt-1 w-44 bg-surface-container-lowest rounded-lg shadow-lg border border-surface-container-high py-1 z-20 flex flex-col font-label-sm text-label-sm"
				>
					<button
						type="button"
						class="px-3 py-1.5 text-left hover:bg-surface-container {filterMode === 'todas'
							? 'text-secondary font-bold'
							: 'text-on-surface'}"
						onclick={() => {
							filterMode = 'todas';
							isFilterMenuOpen = false;
						}}
					>
						Todas las asignaturas
					</button>
					<button
						type="button"
						class="px-3 py-1.5 text-left hover:bg-surface-container {filterMode === 'habilitadas'
							? 'text-secondary font-bold'
							: 'text-on-surface'}"
						onclick={() => {
							filterMode = 'habilitadas';
							isFilterMenuOpen = false;
						}}
					>
						Habilitadas
					</button>
					<button
						type="button"
						class="px-3 py-1.5 text-left hover:bg-surface-container {filterMode === 'alerta'
							? 'text-error font-bold'
							: 'text-on-surface'}"
						onclick={() => {
							filterMode = 'alerta';
							isFilterMenuOpen = false;
						}}
					>
						En Riesgo / Alerta
					</button>
					<button
						type="button"
						class="px-3 py-1.5 text-left hover:bg-surface-container {filterMode === 'en_curso'
							? 'text-secondary font-bold'
							: 'text-on-surface'}"
						onclick={() => {
							filterMode = 'en_curso';
							isFilterMenuOpen = false;
						}}
					>
						En Curso Regular
					</button>
				</div>
			{/if}
		</div>
	</div>

	<!-- List of Course Cards -->
	{#each filteredCourses as course (course.id)}
		<CourseCard {course} {onSimulatePlan} />
	{/each}
</div>
