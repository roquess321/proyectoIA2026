<script lang="ts">
	import { academicState, navItems } from '../academic-state.svelte';
</script>

<aside
	class="fixed left-0 top-0 h-full w-72 bg-surface-container-lowest shadow-[0_1px_8px_rgba(0,0,0,0.04)] z-50 flex flex-col justify-between"
>
	<div class="flex flex-col">
		<!-- Brand / Logo -->
		<div class="h-16 flex items-center px-space-lg gap-space-sm bg-primary text-on-primary">
			<img
				alt="Logo FIUNA"
				class="h-8 w-auto object-contain"
				src="https://lh3.googleusercontent.com/aida-public/AB6AXuAgGX46pke8o-mdRRDA6fE3WkBE8pLWh4817om4sZtv8HbVqQGjJrI4_iPczi1zobQJVmouon7naEvBB8O8iEWrA3GqWT4AYaSM7HWmKdpbYI6bz4HD_e9W7XpStl9IlGIW09HlyIMY8-FsvcCvVajov_363rqAt4Ke9V_XCreCuoL6GOnijz6K-QDetbvWwLyn79PoVVTdyraKj6daA-EEW9DqhaN-DWjrkdPl3yZrLYmc3Otpghbx"
			/>
			<div class="flex flex-col">
				<span
					class="font-headline-sm text-headline-sm font-bold tracking-tight text-on-primary leading-none"
				>
					FIUNA
				</span>
				<span
					class="font-label-sm text-label-sm tracking-wider uppercase text-secondary-fixed opacity-90"
				>
					Academic AI Suite
				</span>
			</div>
		</div>

		<!-- Institutional Context -->
		<div class="px-space-md py-space-sm">
			<div class="p-space-sm bg-surface-container-low rounded-lg">
				<span
					class="font-label-sm text-label-sm uppercase tracking-wider text-on-surface-variant block mb-1"
				>
					Entorno Institucional
				</span>
				<div class="flex items-center gap-space-xs">
					<span class="material-symbols-outlined text-secondary text-sm">account_balance</span>
					<span class="font-body-sm text-body-sm font-semibold text-on-surface">
						Facultad de Ingeniería
					</span>
				</div>
				<span class="font-label-sm text-label-sm text-on-surface-variant block">
					Univ. Nacional de Asunción
				</span>
			</div>
		</div>

		<!-- Nav Links -->
		<nav class="flex flex-col gap-1 px-space-md mt-space-xs">
			{#each navItems as item (item.path)}
				<a
					href={item.href}
					class="flex items-center gap-space-sm px-space-md py-space-sm rounded-lg text-left transition-all {academicState.activeNav ===
					item.path
						? 'bg-primary-container text-white dark:bg-[#132c4d] dark:text-[#d3e4fe] font-semibold shadow-sm'
						: 'text-on-surface-variant hover:bg-surface-container hover:text-on-surface dark:hover:bg-surface-container-high dark:hover:text-on-surface'}"
					onclick={() => (academicState.activeNav = item.path)}
				>
					<span
						class="material-symbols-outlined text-lg {academicState.activeNav === item.path
							? 'text-secondary-fixed dark:text-[#b1c7f0]'
							: ''}"
					>
						{item.icon}
					</span>
					<div class="flex flex-col">
						<span class="font-label-md text-label-md">{item.title}</span>
						<span
							class="font-label-sm text-label-sm {academicState.activeNav === item.path
								? 'text-white/80 dark:text-[#b1c7f0]/80'
								: 'opacity-80'}"
						>
							{item.subtitle}
						</span>
					</div>
				</a>
			{/each}
		</nav>
	</div>

	<!-- Bottom Card: Copilot Status -->
	<div class="p-space-md bg-surface-container-low">
		<div
			class="bg-surface-container-lowest p-space-sm rounded-lg shadow-sm flex flex-col gap-space-xs"
		>
			<div class="flex items-center justify-between">
				<span class="font-label-sm text-label-sm font-semibold uppercase text-secondary">
					Copiloto Activo
				</span>
				<span class="flex h-2 w-2 relative">
					<span
						class="animate-ping absolute inline-flex h-full w-full rounded-full bg-secondary opacity-75"
					></span>
					<span class="relative inline-flex rounded-full h-2 w-2 bg-secondary"></span>
				</span>
			</div>
			<p class="font-body-sm text-body-sm text-on-surface-variant">
				Modelo entrenado con estadísticas de cátedras FIUNA 2018-2024.
			</p>
			<div class="flex items-center justify-between pt-space-xs">
				<button
					type="button"
					class="font-label-sm text-label-sm text-secondary hover:text-on-surface transition-colors flex items-center gap-1"
					onclick={() => (academicState.activeNav = 'feedback-ajustes-ia')}
				>
					<span class="material-symbols-outlined text-sm">help_outline</span>
					Mesa de Ayuda
				</button>
				<span class="font-code-num text-code-num text-on-surface-variant">v2.4.1</span>
			</div>
		</div>
	</div>
</aside>
