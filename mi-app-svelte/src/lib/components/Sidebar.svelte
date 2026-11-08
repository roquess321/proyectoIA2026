<script lang="ts">
	import { academicState, navItems } from "../academic-state.svelte";

	function handleNavClick(path: string): void {
		academicState.activeNav = path;
		academicState.closeMobileMenu();
	}
</script>

<!-- Backdrop / Overlay para versión móvil -->
{#if academicState.isMobileMenuOpen}
	<div
		class="fixed inset-0 bg-black/60 backdrop-blur-xs z-40 lg:hidden transition-opacity"
		onclick={() => academicState.closeMobileMenu()}
		onkeydown={(e) => e.key === "Escape" && academicState.closeMobileMenu()}
		tabindex="0"
		role="button"
		aria-label="Cerrar menú de navegación"
	></div>
{/if}

<aside
	class="fixed left-0 top-0 h-full w-72 bg-surface-container-lowest shadow-[0_1px_8px_rgba(0,0,0,0.06)] z-50 flex flex-col justify-between transition-transform duration-300 ease-in-out {academicState.isMobileMenuOpen
		? 'translate-x-0'
		: '-translate-x-full lg:translate-x-0'}"
>
	<div class="flex flex-col">
		<!-- Brand / Logo -->
		<div
			class="h-16 flex items-center justify-between px-space-lg gap-space-sm bg-primary text-on-primary"
		>
			<div class="flex items-center gap-space-sm">
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

			<!-- Botón de cerrar solo en móvil -->
			<button
				type="button"
				class="lg:hidden p-1.5 rounded-lg hover:bg-white/15 text-on-primary transition-colors cursor-pointer"
				onclick={() => academicState.closeMobileMenu()}
				aria-label="Cerrar menú"
			>
				<span class="material-symbols-outlined text-xl">close</span>
			</button>
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
					<span
						class="material-symbols-outlined text-secondary text-sm"
						>account_balance</span
					>
					<span
						class="font-body-sm text-body-sm font-semibold text-on-surface"
					>
						Facultad de Ingeniería
					</span>
				</div>
				<span
					class="font-label-sm text-label-sm text-on-surface-variant block"
				>
					Univ. Nacional de Asunción
				</span>
			</div>
		</div>

		<!-- Nav Links -->
		<nav
			class="flex flex-col gap-1 px-space-md mt-space-xs overflow-y-auto flex-1"
		>
			{#each navItems as item (item.path)}
				<a
					href={item.href}
					class="flex items-center gap-space-sm px-space-md py-space-sm rounded-lg text-left transition-all {academicState.activeNav ===
					item.path
						? 'bg-primary-container text-white dark:bg-[#132c4d] dark:text-[#d3e4fe] font-semibold shadow-sm'
						: 'text-on-surface-variant hover:bg-surface-container hover:text-on-surface dark:hover:bg-surface-container-high dark:hover:text-on-surface'}"
					onclick={() => handleNavClick(item.path)}
				>
					<span
						class="material-symbols-outlined text-lg {academicState.activeNav ===
						item.path
							? 'text-secondary-fixed dark:text-[#b1c7f0]'
							: ''}"
					>
						{item.icon}
					</span>
					<div class="flex flex-col">
						<span class="font-label-md text-label-md"
							>{item.title}</span
						>
						<span
							class="font-label-sm text-label-sm {academicState.activeNav ===
							item.path
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

	<!-- Footer sutil del Sidebar -->
	<div class="px-space-md py-space-sm border-t border-outline-variant/15 flex items-center justify-between text-on-surface-variant">
		<button
			type="button"
			class="font-label-sm text-label-sm text-secondary hover:text-on-surface transition-colors flex items-center gap-1 cursor-pointer"
			onclick={() => handleNavClick("feedback-ajustes-ia")}
		>
			<span class="material-symbols-outlined text-sm">help_outline</span>
			Mesa de Ayuda
		</button>
		<span class="font-code-num text-code-num text-xs opacity-70">v2.5.0</span>
	</div>
</aside>
