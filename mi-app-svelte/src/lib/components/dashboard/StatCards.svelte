<script lang="ts">
	import type { MetricCard } from '../../types/academic';

	interface Props {
		metrics: MetricCard[];
	}

	let { metrics }: Props = $props();
</script>

<div class="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-5 gap-space-md">
	{#each metrics as card (card.id)}
		<div class="flex flex-col justify-between rounded-xl bg-surface-container-lowest p-space-md shadow-sm">
			<div class="flex items-center justify-between text-on-surface-variant">
				<span class="font-label-sm text-label-sm font-semibold uppercase tracking-wider">
					{card.title}
				</span>
				<div class="rounded-lg bg-surface-container p-1 text-secondary">
					<span class="material-symbols-outlined text-lg">{card.icon}</span>
				</div>
			</div>

			{#if card.id === 'habilitaciones'}
				<div class="mt-space-sm flex items-center gap-3">
					<div class="flex flex-col">
						<span class="font-headline-md text-headline-md font-bold text-on-surface font-code-num">
							{card.safeCount}
						</span>
						<span class="font-label-sm text-label-sm text-on-surface-variant">Seguras</span>
					</div>
					<div class="h-8 w-px bg-surface-container-high"></div>
					<div class="flex flex-col">
						<span class="font-headline-md text-headline-md font-bold text-error font-code-num">
							{card.alertCount}
						</span>
						<span class="font-label-sm text-label-sm text-error font-semibold">Alerta</span>
					</div>
				</div>

				<div
					class="mt-space-sm flex items-center gap-1 font-label-sm text-label-sm text-on-tertiary-container bg-tertiary-fixed/30 px-2 py-0.5 rounded"
				>
					<span class="material-symbols-outlined text-sm">warning</span>
					<span>{card.alertMessage}</span>
				</div>
			{:else}
				<div class="mt-space-sm flex items-baseline gap-2">
					<span class="font-headline-lg text-headline-lg text-primary font-bold font-code-num">
						{card.value}
					</span>
					{#if card.total}
						<span class="font-body-sm text-body-sm text-on-surface-variant">/ {card.total}</span>
					{/if}
					{#if card.unit}
						<span class="font-body-sm text-body-sm text-on-surface-variant">{card.unit}</span>
					{/if}
				</div>

				{#if card.footerType === 'badge'}
					<div
						class="mt-space-sm flex items-center gap-1 rounded bg-surface-container-low px-2 py-1 font-label-sm text-label-sm text-on-secondary-container"
					>
						{#if card.badgeIcon}
							<span class="material-symbols-outlined text-sm">{card.badgeIcon}</span>
						{/if}
						<span>{card.badgeText}</span>
					</div>
				{:else if card.footerType === 'progress'}
					<div class="mt-space-sm flex flex-col gap-1">
						<div class="h-1.5 w-full overflow-hidden rounded-full bg-surface-container">
							<div
								class="h-full rounded-full bg-secondary transition-all duration-700"
								style="width: {card.progressPercent}%;"
							></div>
						</div>
						<span class="font-label-sm text-label-sm text-on-surface-variant font-code-num text-right">
							{card.badgeText}
						</span>
					</div>
				{:else if card.footerType === 'split'}
					<div
						class="mt-space-sm flex items-center justify-between font-label-sm text-label-sm text-on-surface-variant"
					>
						<span>{card.leftLabel}</span>
						<span class="font-semibold text-secondary">{card.rightLabel}</span>
					</div>
				{/if}
			{/if}
		</div>
	{/each}
</div>
