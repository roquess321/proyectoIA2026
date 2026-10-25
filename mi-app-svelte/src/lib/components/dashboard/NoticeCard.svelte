<script lang="ts">
	interface Props {
		category?: string;
		title?: string;
		message?: string;
	}

	let {
		category = 'Aviso de Coordinación',
		title = 'Inscripción a Exámenes Finales',
		message = 'El sistema InsWeb habilitará el formulario de confirmación de llamado a partir del 20 de Noviembre a las 00:00 hs.'
	}: Props = $props();
</script>

<div class="flex flex-col rounded-xl bg-surface-container-lowest p-space-md shadow-sm">
	<div class="flex items-center justify-between pb-space-xs">
		<span class="font-label-sm text-label-sm font-semibold uppercase text-on-surface-variant">
			{category}
		</span>
		<span class="material-symbols-outlined text-base text-on-surface-variant">campaign</span>
	</div>
	<div class="mt-space-xs">
		<h4 class="font-label-md text-label-md font-semibold text-on-surface">{title}</h4>
		<p class="mt-1 font-body-sm text-body-sm text-on-surface-variant">
			{message}
		</p>
	</div>
</div>
