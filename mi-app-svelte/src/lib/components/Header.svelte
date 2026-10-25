<script lang="ts">
	import { onMount } from 'svelte';
	import { academicState } from '../academic-state.svelte';

	let dark = $state(false);

	function applyTheme(): void {
		const html = document.documentElement;
		if (dark) {
			html.classList.add('dark');
		} else {
			html.classList.remove('dark');
		}
		localStorage.setItem('theme', dark ? 'dark' : 'light');
	}

	function toggleTheme(): void {
		dark = !dark;
	}

	onMount(() => {
		const saved = localStorage.getItem('theme');
		dark = saved === 'dark';
		applyTheme();
	});

	$effect(() => {
		applyTheme();
	});
</script>

<header
	class="fixed top-0 left-72 right-0 h-16 bg-surface/90 border-b border-outline-variant/30 dark:border-surface-container-high/60 backdrop-blur-xl shadow-[0_1px_8px_rgba(0,0,0,0.04)] dark:shadow-none z-40 flex items-center justify-between px-space-lg transition-colors"
>
	<div class="flex items-center gap-space-md">
		<div class="flex items-center gap-space-xs bg-surface-container-high px-space-sm py-1 rounded">
			<span class="material-symbols-outlined text-primary text-base">calendar_month</span>
			<span class="font-label-sm text-label-sm font-semibold text-on-surface">
				Periodo Lectivo 2024-2 (Segundo Ciclo)
			</span>
		</div>
		<div
			class="flex items-center gap-space-xs bg-surface-container-lowest px-space-sm py-1 rounded shadow-sm"
		>
			<span class="h-2 w-2 rounded-full bg-emerald-500"></span>
			<span class="font-label-sm text-label-sm font-medium text-on-surface-variant">
				InsWeb Conectado
			</span>
			<span class="font-label-sm text-label-sm text-outline">(Último sync: hoy 09:42)</span>
		</div>
	</div>

	<div class="flex items-center gap-space-md">
		<button
			class="p-space-xs rounded text-on-surface-variant hover:bg-surface-container hover:text-on-surface relative transition-colors"
			title="Notificaciones"
			type="button"
		>
			<span class="material-symbols-outlined text-xl">notifications</span>
			<span class="absolute top-1 right-1 h-2 w-2 rounded-full bg-error"></span>
		</button>

		<button
			class="p-space-xs rounded text-on-surface-variant hover:bg-surface-container hover:text-on-surface transition-colors"
			title="Sincronización Rápida"
			type="button"
			onclick={() => academicState.forceRescrape()}
		>
			<span
				class="material-symbols-outlined text-xl {academicState.isRescraping ? 'animate-spin' : ''}"
			>
				sync
			</span>
		</button>

		<!-- Botón de tema oscuro/claro -->
		<button
			class="p-space-xs rounded text-on-surface-variant hover:bg-surface-container hover:text-on-surface transition-colors"
			title={dark ? 'Cambiar a tema claro' : 'Cambiar a tema oscuro'}
			type="button"
			onclick={toggleTheme}
		>
			<span class="material-symbols-outlined text-xl">
				{dark ? 'light_mode' : 'dark_mode'}
			</span>
		</button>

		<div class="h-6 w-px bg-surface-container-high"></div>

		<div class="flex items-center gap-space-sm pl-space-xs">
			<div class="flex flex-col text-right">
				<span class="font-label-md text-label-md font-semibold text-on-surface leading-tight">
					Alejandro Benítez
				</span>
				<span class="font-label-sm text-label-sm text-on-surface-variant">Ing. Electromecánica</span>
			</div>
			<img
				alt="Foto de perfil de Alejandro Benítez"
				class="w-8 h-8 rounded-full object-cover ring-2 ring-surface-container-high"
				src="https://lh3.googleusercontent.com/aida-public/AB6AXuB8kJ8FISwkV6OknOgU0T7j3qRhwrIH2U1kypIEEFDa--01sG9zkVj7oWJ_5WG452Ig4i94JueK2YPEYHgLASnwTCcUJYc7MSbtBjI4ymazMa1wiMt_seGP6F1dWEs56_3IcHZ0-sF40L3lkzpQwgLkNB6MqFJ79KcVHgdN040oqJg0pbttWoL0sRVJ6qfIbtqpuA0_iIVKCGY1bX5GffM55HRS_PnCZWF9VvY8Adwi10slrChZ_3cA"
			/>
		</div>
	</div>
</header>