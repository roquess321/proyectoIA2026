<script lang="ts">
	import type { StudentProfile } from "../../types/academic";
	import { academicState } from "../../academic-state.svelte";
	import { authState } from "../../auth-state.svelte";
	import { goto } from "$app/navigation";

	export interface Props {
		profile: StudentProfile;
		onSimulate?: () => void;
	}

	let { profile, onSimulate }: Props = $props();

	let isDownloading = $state(false);
	let downloadSuccess = $state(false);

	let displayName = $derived(
		authState.isLoggedIn && authState.user
			? authState.user.nombre
			: "Estudiante (No Autenticado)"
	);

	let displayCarrera = $derived(
		authState.isLoggedIn && authState.user
			? (profile.plan ? `${authState.user.carrera} (${profile.plan})` : authState.user.carrera)
			: `${profile.carrera} (${profile.plan})`
	);

	let displayMatricula = $derived(
		authState.isLoggedIn && authState.user
			? authState.user.cedula
			: "Sin sesión"
	);

	let displayEstado = $derived(
		authState.isLoggedIn && authState.user
			? (authState.user.isSynced ? "InsWeb Conectado" : "Activo")
			: "Modo Invitado"
	);

	function handleDownload() {
		if (isDownloading) return;
		isDownloading = true;
		downloadSuccess = false;

		setTimeout(() => {
			isDownloading = false;
			downloadSuccess = true;
			setTimeout(() => {
				downloadSuccess = false;
			}, 3000);
		}, 1200);
	}
</script>

<div
	class="relative overflow-hidden rounded-xl bg-surface-container-lowest p-4 sm:p-space-lg shadow-sm"
>
	<div
		class="absolute -right-12 -top-12 h-64 w-64 rounded-full bg-secondary-fixed opacity-40 blur-3xl pointer-events-none"
	></div>

	<div
		class="flex flex-col lg:flex-row lg:items-center justify-between gap-space-md relative z-10"
	>
		<div class="flex flex-col sm:flex-row sm:items-center gap-space-sm sm:gap-space-md">
			<div class="relative shrink-0 self-start sm:self-center">
				{#if authState.isLoggedIn && authState.user}
					<div
						class="w-14 h-14 sm:w-20 sm:h-20 rounded-xl bg-primary text-on-primary font-bold text-xl sm:text-2xl flex items-center justify-center shadow-sm"
					>
						{authState.user.nombre.slice(0, 2).toUpperCase()}
					</div>
				{:else}
					<div
						class="w-14 h-14 sm:w-20 sm:h-20 rounded-xl bg-surface-container-high text-outline flex items-center justify-center shadow-sm"
					>
						<span class="material-symbols-outlined text-3xl sm:text-4xl">person_off</span>
					</div>
				{/if}
				<span
					class="absolute -bottom-1 -right-1 flex h-4 w-4 items-center justify-center rounded-full bg-surface-container-lowest"
				>
					<span class="h-2.5 w-2.5 rounded-full {authState.isLoggedIn ? 'bg-secondary' : 'bg-slate-400'}"></span>
				</span>
			</div>

			<div class="flex flex-col">
				<div class="flex flex-wrap items-center gap-x-space-sm gap-y-1">
					<h1
						class="font-headline-lg text-xl sm:text-headline-lg text-on-surface font-bold tracking-tight"
					>
						{displayName}
					</h1>
					<span
						class="inline-flex items-center gap-1 rounded {authState.isLoggedIn ? 'bg-secondary-fixed text-on-secondary-fixed' : 'bg-surface-container-high text-outline'} px-2 py-0.5 font-label-sm text-xs sm:text-label-sm font-semibold uppercase tracking-wider"
					>
						<span class="material-symbols-outlined text-xs"
							>{authState.isLoggedIn ? 'verified' : 'lock'}</span
						>
						{displayEstado}
					</span>
				</div>

				<div
					class="flex flex-wrap items-center gap-x-space-md gap-y-1.5 mt-1.5 text-on-surface-variant font-body-sm text-xs sm:text-body-sm"
				>
					<span class="flex items-center gap-1">
						<span
							class="material-symbols-outlined text-base text-secondary"
							>badge</span
						>
						C.I. / Matrícula:
						<strong
							class="text-on-surface font-semibold font-code-num text-code-num"
						>
							{displayMatricula}
						</strong>
					</span>
					<span class="flex items-center gap-1">
						<span
							class="material-symbols-outlined text-base text-secondary"
							>school</span
						>
						Carrera:
						<strong class="text-on-surface font-semibold">
							{displayCarrera}
						</strong>
					</span>
					<span class="flex items-center gap-1">
						<span
							class="material-symbols-outlined text-base text-secondary"
							>timelapse</span
						>
						Semestre:
						<strong class="text-on-surface font-semibold"
							>{profile.semestre}</strong
						>
					</span>
				</div>
			</div>
		</div>

		<div class="flex items-center gap-2 sm:gap-space-sm w-full sm:w-auto self-start lg:self-center">
			<button
				type="button"
				class="flex-1 sm:flex-none flex items-center justify-center gap-space-xs rounded bg-primary-container px-space-md py-2.5 sm:py-space-sm text-on-primary font-label-md text-label-md font-semibold transition-all hover:bg-primary shadow-sm active:scale-98"
				onclick={() => {
					if (onSimulate) {
						onSimulate();
					} else {
						academicState.activeNav = "agente-ia-pronosticos";
						goto("/agente-ia-pronosticos");
					}
				}}
			>
				<span class="material-symbols-outlined text-lg"
					>auto_awesome</span
				>
				Simulador Predictivo IA
			</button>

			<button
				type="button"
				class="relative flex items-center justify-center p-2.5 sm:p-space-sm rounded bg-surface-container hover:bg-surface-container-high text-on-surface-variant hover:text-on-surface transition-colors cursor-pointer shrink-0"
				title="Descargar Constancia Académica"
				onclick={handleDownload}
			>
				<span
					class="material-symbols-outlined text-xl {isDownloading
						? 'animate-bounce'
						: ''}"
				>
					{downloadSuccess ? "check_circle" : "file_download"}
				</span>
			</button>

			{#if downloadSuccess}
				<span
					class="text-xs text-emerald-700 bg-emerald-100 px-2 py-1 rounded font-medium animate-fade-in"
				>
					Constancia generada
				</span>
			{/if}
		</div>
	</div>
</div>
