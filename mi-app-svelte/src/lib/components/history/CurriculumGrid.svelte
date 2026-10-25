<script lang="ts">
	import type { SemesterCurriculumBlock } from '../../types/academic-history';

	export interface Props {
		blocks: SemesterCurriculumBlock[];
		onSelectCourseByCode: (code: string) => void;
	}

	let { blocks, onSelectCourseByCode }: Props = $props();
</script>

<div class="flex flex-col gap-space-lg">
	<div class="bg-surface-container-lowest p-space-lg rounded-xl shadow-sm flex flex-col gap-space-md border border-outline-variant/30">
		<!-- Header & Legend -->
		<div class="flex flex-col md:flex-row md:items-center justify-between gap-space-sm border-b border-outline-variant/20 pb-space-md">
			<div>
				<h2 class="font-headline-md text-headline-md text-primary font-bold">
					Malla Curricular Secuencial
				</h2>
				<p class="font-body-sm text-body-sm text-on-surface-variant">
					Flujo interactivo de dependencias académicas por semestre
				</p>
			</div>

			<div class="flex items-center gap-space-md flex-wrap text-label-sm font-label-sm">
				<div class="flex items-center gap-1.5">
					<span class="w-3 h-3 rounded-full bg-surface-container-highest"></span>
					<span class="text-on-surface">Aprobada</span>
				</div>
				<div class="flex items-center gap-1.5">
					<span class="w-3 h-3 rounded-full bg-secondary-fixed"></span>
					<span class="text-on-surface">En Curso</span>
				</div>
				<div class="flex items-center gap-1.5">
					<span class="w-3 h-3 rounded-full bg-surface-container"></span>
					<span class="text-on-surface">Habilitada p/ Matrícula</span>
				</div>
				<div class="flex items-center gap-1.5">
					<span class="w-3 h-3 rounded-full bg-surface-container-low opacity-60"></span>
					<span class="text-on-surface-variant">Bloqueada</span>
				</div>
			</div>
		</div>

		<!-- Semester Columns Grid -->
		<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-space-md pt-space-sm">
			{#each blocks as block}
				<div class="bg-surface-container-low p-space-md rounded-lg flex flex-col gap-space-sm border border-outline-variant/20">
					<div class="flex items-center justify-between pb-space-xs">
						<span class="font-label-md text-label-md text-primary font-bold">
							{block.semesterName}
						</span>
						<span class="bg-surface-container text-on-surface-variant font-code-num text-code-num px-1.5 py-0.5 rounded">
							{block.credits} Cred
						</span>
					</div>

					<div class="flex flex-col gap-2">
						{#each block.courses as course}
							<button
								type="button"
								class="p-space-sm rounded text-left transition-all cursor-pointer border border-outline-variant/10 {course.status ===
								'APROBADA'
									? 'bg-surface-container-highest hover:bg-surface-container-high'
									: course.status === 'CURSO'
										? 'bg-secondary-fixed text-on-secondary-fixed shadow-sm hover:opacity-90'
										: course.status === 'HABILITADA'
											? 'bg-surface-container hover:bg-surface-container-high'
											: 'bg-surface-container-lowest opacity-75 hover:opacity-100'}"
								onclick={() => onSelectCourseByCode(course.code)}
							>
								<span
									class="font-code-num text-code-num font-bold block {course.status ===
									'CURSO'
										? 'text-on-secondary-fixed'
										: 'text-secondary'}"
								>
									{course.code}
								</span>
								<span class="font-body-sm text-body-sm text-on-surface font-medium block">
									{course.name}
								</span>
								{#if course.gradeText}
									<span
										class="font-label-sm text-label-sm block mt-1 {course.status === 'CURSO'
											? 'text-on-secondary-fixed font-semibold'
											: 'text-on-surface-variant'}"
									>
										{course.gradeText}
									</span>
								{/if}
							</button>
						{/each}
					</div>
				</div>
			{/each}
		</div>
	</div>

	<!-- Bottom 3 Info Cards -->
	<div class="grid grid-cols-1 md:grid-cols-3 gap-space-md">
		<div
			class="bg-surface-container-lowest p-space-md rounded-xl shadow-sm flex items-center gap-space-md border border-outline-variant/30"
		>
			<div class="w-12 h-12 rounded-lg bg-surface-container-high flex items-center justify-center shrink-0">
				<span class="material-symbols-outlined text-secondary text-2xl">verified_user</span>
			</div>
			<div class="flex flex-col">
				<span class="font-label-md text-label-md text-primary font-bold">Certificado de Malla</span>
				<span class="font-body-sm text-body-sm text-on-surface-variant">
					Convalidado por Secretaría General FIUNA bajo ordenanza 112/19.
				</span>
			</div>
		</div>

		<div
			class="bg-surface-container-lowest p-space-md rounded-xl shadow-sm flex items-center gap-space-md border border-outline-variant/30"
		>
			<div class="w-12 h-12 rounded-lg bg-surface-container-high flex items-center justify-center shrink-0">
				<span class="material-symbols-outlined text-secondary text-2xl">speed</span>
			</div>
			<div class="flex flex-col">
				<span class="font-label-md text-label-md text-primary font-bold">Rendimiento Histórico</span>
				<span class="font-body-sm text-body-sm text-on-surface-variant">
					88.2% de asignaturas aprobadas en 1ra oportunidad.
				</span>
			</div>
		</div>

		<div
			class="bg-surface-container-lowest p-space-md rounded-xl shadow-sm flex items-center gap-space-md border border-outline-variant/30"
		>
			<div class="w-12 h-12 rounded-lg bg-surface-container-high flex items-center justify-center shrink-0">
				<span class="material-symbols-outlined text-secondary text-2xl">model_training</span>
			</div>
			<div class="flex flex-col">
				<span class="font-label-md text-label-md text-primary font-bold">Simulación Continua</span>
				<span class="font-body-sm text-body-sm text-on-surface-variant">
					El agente actualiza correlativas tras cada cierre de actas oficiales.
				</span>
			</div>
		</div>
	</div>
</div>
