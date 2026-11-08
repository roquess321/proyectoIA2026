<script lang="ts">
	import { onMount } from 'svelte';
	import { academicState } from '../academic-state.svelte';
	import { authState } from '../auth-state.svelte';

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
	class="fixed top-0 left-0 lg:left-72 right-0 h-16 bg-surface/90 border-b border-outline-variant/30 dark:border-surface-container-high/60 backdrop-blur-xl shadow-[0_1px_8px_rgba(0,0,0,0.04)] dark:shadow-none z-40 flex items-center justify-between px-3 sm:px-space-md lg:px-space-lg transition-all"
>
	<div class="flex items-center gap-1 sm:gap-space-md">
		<!-- Botón Hamburguesa para Móvil -->
		<button
			type="button"
			class="lg:hidden p-2 rounded-lg text-on-surface hover:bg-surface-container active:bg-surface-container-high transition-colors cursor-pointer mr-0.5"
			onclick={() => academicState.toggleMobileMenu()}
			aria-label="Abrir menú de navegación"
		>
			<span class="material-symbols-outlined text-2xl">menu</span>
		</button>

		<!-- Logo / Marca visible solo en móvil -->
		<div class="lg:hidden flex items-center gap-1.5 mr-1">
			<span class="font-headline-sm text-base font-bold text-primary dark:text-white leading-none">FIUNA</span>
			<span class="text-[10px] uppercase font-bold text-secondary px-1.5 py-0.5 rounded bg-secondary-fixed/60 dark:bg-secondary-container/40">AI</span>
		</div>

		<!-- Periodo Lectivo (Visible en pantallas medianas y grandes) -->
		<div class="hidden md:flex items-center gap-space-xs bg-surface-container-high px-space-sm py-1 rounded">
			<span class="material-symbols-outlined text-primary text-base">calendar_month</span>
			<span class="font-label-sm text-label-sm font-semibold text-on-surface">
				Periodo 2024-2 (Segundo Ciclo)
			</span>
		</div>

		{#if authState.isLoggedIn && authState.user}
			<div
				class="flex items-center gap-1.5 bg-surface-container-lowest px-2 sm:px-space-sm py-1 rounded shadow-xs"
			>
				<span class="h-2 w-2 rounded-full {authState.user.isSynced ? 'bg-emerald-500' : 'bg-amber-500'} shrink-0"></span>
				<span class="font-label-sm text-label-sm font-medium text-on-surface-variant truncate max-w-[120px] sm:max-w-none">
					{authState.user.isSynced ? 'InsWeb' : 'Local'}
				</span>
				<span class="hidden sm:inline font-label-sm text-label-sm text-outline">(C.I. {authState.user.cedula})</span>
			</div>
		{:else}
			<div
				class="hidden sm:flex items-center gap-space-xs bg-surface-container-lowest px-space-sm py-1 rounded shadow-xs opacity-80"
			>
				<span class="h-2 w-2 rounded-full bg-slate-400"></span>
				<span class="font-label-sm text-label-sm font-medium text-outline">
					Modo Invitado
				</span>
			</div>
		{/if}
	</div>

	<div class="flex items-center gap-1 sm:gap-space-md">
		<button
			class="hidden xs:flex p-space-xs rounded text-on-surface-variant hover:bg-surface-container hover:text-on-surface relative transition-colors cursor-pointer"
			title="Notificaciones"
			type="button"
		>
			<span class="material-symbols-outlined text-xl">notifications</span>
			<span class="absolute top-1 right-1 h-2 w-2 rounded-full bg-error"></span>
		</button>

		<button
			class="p-space-xs rounded text-on-surface-variant hover:bg-surface-container hover:text-on-surface transition-colors cursor-pointer"
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
			class="p-space-xs rounded text-on-surface-variant hover:bg-surface-container hover:text-on-surface transition-colors cursor-pointer"
			title={dark ? 'Cambiar a tema claro' : 'Cambiar a tema oscuro'}
			type="button"
			onclick={toggleTheme}
		>
			<span class="material-symbols-outlined text-xl">
				{dark ? 'light_mode' : 'dark_mode'}
			</span>
		</button>

		<div class="h-6 w-px bg-surface-container-high hidden sm:block"></div>

		{#if authState.isLoggedIn && authState.user}
			<div class="flex items-center gap-1 sm:gap-space-sm pl-0.5 sm:pl-space-xs">
				<div class="hidden sm:flex flex-col text-right">
					<span class="font-label-md text-label-md font-semibold text-on-surface leading-tight truncate max-w-[150px]">
						{authState.user.nombre}
					</span>
					<span class="font-label-sm text-label-sm text-on-surface-variant truncate max-w-[150px]">
						{authState.user.carrera}
					</span>
				</div>
				<div
					class="w-8 h-8 rounded-full bg-primary text-on-primary flex items-center justify-center font-bold text-xs ring-2 ring-surface-container-high shrink-0"
					title="C.I. {authState.user.cedula} • {authState.user.nombre}"
				>
					{authState.user.nombre.slice(0, 2).toUpperCase()}
				</div>
				<button
					type="button"
					class="p-space-xs rounded text-outline hover:text-error hover:bg-error/10 transition-colors cursor-pointer"
					title="Cerrar Sesión"
					onclick={() => authState.logout()}
				>
					<span class="material-symbols-outlined text-lg">logout</span>
				</button>
			</div>
		{:else}
			<div class="flex items-center gap-1 sm:gap-space-sm pl-0.5 sm:pl-space-xs">
				<a
					href="/"
					class="px-2.5 sm:px-space-sm py-1 rounded bg-primary text-on-primary font-label-sm text-label-sm hover:bg-primary-container transition-colors shadow-sm whitespace-nowrap"
					onclick={() => (academicState.activeNav = 'acceso-insweb')}
				>
					Acceder
				</a>
			</div>
		{/if}
	</div>
</header>