<script lang="ts">
	import type { ExamEvent } from '../../types/academic';

	interface Props {
		exams: ExamEvent[];
	}

	let { exams }: Props = $props();
</script>

<div class="flex flex-col rounded-xl bg-surface-container-lowest p-space-md shadow-sm">
	<div class="flex items-center justify-between pb-space-sm">
		<div class="flex items-center gap-space-xs">
			<span class="material-symbols-outlined text-secondary text-lg">event_upcoming</span>
			<h2 class="font-headline-sm text-headline-sm text-on-surface font-bold">
				Calendario de Exámenes
			</h2>
		</div>
		<span
			class="font-label-sm text-label-sm text-on-surface-variant bg-surface-container px-2 py-0.5 rounded font-code-num"
		>
			FIUNA 2024-2
		</span>
	</div>

	<p class="font-body-sm text-body-sm text-on-surface-variant">
		Fechas oficiales de 2dos Parciales y Periodos Ordinarios de Finales según cronograma de Facultad.
	</p>

	<!-- Exam Items List -->
	<div class="mt-space-md flex flex-col gap-space-sm">
		{#each exams as exam (exam.id)}
			<div
				class="flex items-center justify-between p-space-sm rounded-lg {exam.urgency === 'final'
					? 'bg-surface-container-high'
					: 'bg-surface-container-low hover:bg-surface-container'} transition-colors"
			>
				<div class="flex items-center gap-space-sm">
					{#if exam.urgency === 'critical'}
						<div
							class="flex flex-col items-center justify-center h-12 w-12 rounded bg-error-container text-on-error-container shadow-sm"
						>
							<span class="font-label-sm text-label-sm font-bold uppercase leading-none">
								{exam.month}
							</span>
							<span class="font-headline-sm text-headline-sm font-bold font-code-num leading-tight">
								{exam.day}
							</span>
						</div>
					{:else if exam.urgency === 'final'}
						<div
							class="flex flex-col items-center justify-center h-12 w-12 rounded bg-primary text-on-primary shadow-sm"
						>
							<span class="font-label-sm text-label-sm font-bold uppercase leading-none">
								{exam.month}
							</span>
							<span class="font-headline-sm text-headline-sm font-bold font-code-num leading-tight">
								{exam.day}
							</span>
						</div>
					{:else}
						<div
							class="flex flex-col items-center justify-center h-12 w-12 rounded bg-surface-container-lowest text-on-surface shadow-sm"
						>
							<span
								class="font-label-sm text-label-sm font-bold text-secondary uppercase leading-none"
							>
								{exam.month}
							</span>
							<span class="font-headline-sm text-headline-sm font-bold font-code-num leading-tight">
								{exam.day}
							</span>
						</div>
					{/if}

					<div class="flex flex-col">
						<span class="font-label-md text-label-md font-semibold text-on-surface line-clamp-1">
							{exam.title}
						</span>
						<span
							class="font-body-sm text-body-sm {exam.urgency === 'critical'
								? 'text-error font-medium'
								: 'text-on-surface-variant'}"
						>
							{exam.subtitle}
						</span>
					</div>
				</div>

				<div class="flex flex-col items-end">
					<span
						class="font-label-sm text-label-sm font-bold font-code-num {exam.urgency === 'critical'
							? 'text-error'
							: exam.urgency === 'final'
								? 'text-secondary'
								: 'text-secondary'}"
					>
						{exam.daysRemaining} DÍAS
					</span>
					<span class="font-label-sm text-label-sm text-outline">{exam.time}</span>
				</div>
			</div>
		{/each}
	</div>

	<div class="mt-space-md pt-space-sm flex items-center justify-between">
		<span class="font-body-sm text-body-sm text-on-surface-variant">
			Sede San Lorenzo • Campus UNA
		</span>
		<button
			type="button"
			class="font-label-sm text-label-sm text-secondary hover:text-on-surface font-semibold hover:underline"
		>
			Descargar PDF
		</button>
	</div>
</div>
