<script lang="ts">
	import type { Course } from '../../types/academic';
	import { academicState } from '../../academic-state.svelte';
	import { goto } from '$app/navigation';

	interface Props {
		course: Course;
		onSimulatePlan?: (course: Course) => void;
	}

	let { course, onSimulatePlan }: Props = $props();
</script>

<div
	class="group flex flex-col rounded-xl bg-surface-container-lowest p-space-md shadow-sm transition-all hover:shadow-md relative overflow-hidden"
>
	{#if course.hasAlertBorder}
		<div class="absolute left-0 top-0 bottom-0 w-1.5 bg-error"></div>
	{/if}

	<div
		class="flex flex-col sm:flex-row sm:items-center justify-between gap-2 {course.hasAlertBorder
			? 'pl-2'
			: ''}"
	>
		<div>
			<div class="flex items-center gap-space-xs">
				<span
					class="font-label-sm text-label-sm font-semibold {course.hasAlertBorder
						? 'text-error'
						: 'text-secondary'} font-code-num uppercase"
				>
					{course.code}
				</span>
				<span class="text-outline-variant">•</span>
				<span class="font-label-sm text-label-sm text-on-surface-variant">
					{course.professor}
				</span>
			</div>
			<h3 class="font-headline-sm text-headline-sm text-on-surface font-bold mt-0.5">
				{course.name}
			</h3>
		</div>

		<!-- Status badge -->
		{#if course.statusBadge.type === 'error'}
			<span
				class="inline-flex items-center gap-1.5 rounded bg-error-container px-2.5 py-1 font-label-sm text-label-sm font-semibold text-on-error-container self-start sm:self-center"
			>
				{#if course.statusBadge.icon}
					<span class="material-symbols-outlined text-xs">{course.statusBadge.icon}</span>
				{/if}
				{course.statusBadge.text}
			</span>
		{:else if course.statusBadge.type === 'highest'}
			<span
				class="inline-flex items-center gap-1.5 rounded bg-surface-container-highest px-2.5 py-1 font-label-sm text-label-sm font-semibold text-primary self-start sm:self-center"
			>
				{#if course.statusBadge.icon}
					<span class="material-symbols-outlined text-xs text-secondary">
						{course.statusBadge.icon}
					</span>
				{/if}
				{course.statusBadge.text}
			</span>
		{:else if course.statusBadge.type === 'secondary'}
			<span
				class="inline-flex items-center gap-1.5 rounded bg-surface-container-low px-2.5 py-1 font-label-sm text-label-sm font-semibold text-on-secondary-container self-start sm:self-center"
			>
				{#if course.statusBadge.dot}
					<span class="h-2 w-2 rounded-full bg-secondary"></span>
				{/if}
				{course.statusBadge.text}
			</span>
		{:else}
			<span
				class="inline-flex items-center gap-1.5 rounded bg-surface-container-high px-2.5 py-1 font-label-sm text-label-sm font-semibold text-on-surface self-start sm:self-center"
			>
				{#if course.statusBadge.dot}
					<span class="h-2 w-2 rounded-full bg-secondary"></span>
				{/if}
				{course.statusBadge.text}
			</span>
		{/if}
	</div>

	<!-- Grades grid -->
	<div
		class="mt-space-md grid grid-cols-2 sm:grid-cols-4 gap-space-sm bg-surface-container-low p-space-sm rounded-lg {course.hasAlertBorder
			? 'pl-3'
			: ''}"
	>
		{#each course.grades as grade, idx}
			<div class="flex flex-col">
				<span class="font-label-sm text-label-sm text-on-surface-variant">{grade.label}</span>

				{#if grade.isApproved}
					<span
						class="font-headline-sm text-headline-sm text-secondary font-bold flex items-center gap-1"
					>
						<span class="material-symbols-outlined text-base">check_circle</span>
						{grade.value}
					</span>
					<span class="font-label-sm text-label-sm text-on-surface-variant">{grade.subtext}</span>
				{:else if course.actionLink && idx === 3}
					<button
						type="button"
						class="font-label-sm text-label-sm text-secondary hover:underline font-semibold flex items-center gap-1 mt-1 text-left"
						onclick={() => {
							if (onSimulatePlan) {
								onSimulatePlan(course);
							} else {
								academicState.activeNav = 'agente-ia-pronosticos';
								goto('/agente-ia-pronosticos');
							}
						}}
					>
						<span class="material-symbols-outlined text-xs">tune</span>
						{course.actionLink.label}
					</button>
				{:else}
					<span
						class="font-headline-sm text-headline-sm font-bold font-code-num {grade.highlight &&
						course.hasAlertBorder
							? 'text-error'
							: 'text-on-surface'}"
					>
						{grade.value}
						{#if grade.max}
							<span class="text-body-sm font-normal text-on-surface-variant">/ {grade.max}</span>
						{/if}
					</span>
					<span
						class="font-label-sm text-label-sm {grade.highlight && course.hasAlertBorder
							? 'text-error font-semibold'
							: grade.subtext.includes('Faltan')
								? 'text-on-tertiary-container font-medium'
								: 'text-on-surface-variant'}"
					>
						{grade.subtext}
					</span>
				{/if}
			</div>
		{/each}
	</div>

	<!-- AI Prognosis Footer -->
	<div
		class="mt-space-sm flex flex-col sm:flex-row sm:items-center justify-between gap-2 pt-space-xs text-on-surface-variant {course.hasAlertBorder
			? 'pl-2'
			: ''}"
	>
		<div
			class="flex items-center gap-1 font-body-sm text-body-sm {course.aiPrognosis.isCritical
				? 'text-error'
				: ''}"
		>
			<span
				class="material-symbols-outlined text-base {course.aiPrognosis.isCritical
					? 'text-error'
					: 'text-secondary'}"
			>
				{course.aiPrognosis.isCritical ? 'emergency' : 'psychology'}
			</span>
			<span>
				{course.aiPrognosis.text}
				<strong class="{course.aiPrognosis.isCritical ? '' : 'text-on-surface'} font-semibold">
					{course.aiPrognosis.highlightText}
				</strong>
			</span>
		</div>
		<span class="font-label-sm text-label-sm font-code-num text-outline">
			{course.accumulatedScore}
		</span>
	</div>
</div>
