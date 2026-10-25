<script lang="ts">
	import type { StudentProfile } from "../../types/academic";
	import { academicState } from "../../academic-state.svelte";
	import { goto } from "$app/navigation";

	export interface Props {
		profile: StudentProfile;
		onSimulate?: () => void;
	}

	let { profile, onSimulate }: Props = $props();

	let isDownloading = $state(false);
	let downloadSuccess = $state(false);

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
	class="relative overflow-hidden rounded-xl bg-surface-container-lowest p-space-lg shadow-sm"
>
	<div
		class="absolute -right-12 -top-12 h-64 w-64 rounded-full bg-secondary-fixed opacity-40 blur-3xl pointer-events-none"
	></div>

	<div
		class="flex flex-col lg:flex-row lg:items-center justify-between gap-space-md relative z-10"
	>
		<div class="flex flex-col sm:flex-row sm:items-center gap-space-md">
			<div class="relative">
				<img
					class="w-20 h-20 rounded-xl object-cover shadow-sm bg-surface-container"
					alt="Retrato de {profile.nombre}"
					src={profile.avatarUrl}
				/>
				<span
					class="absolute -bottom-1 -right-1 flex h-4 w-4 items-center justify-center rounded-full bg-surface-container-lowest"
				>
					<span class="h-2.5 w-2.5 rounded-full bg-secondary"></span>
				</span>
			</div>

			<div class="flex flex-col">
				<div class="flex flex-wrap items-center gap-x-space-sm gap-y-1">
					<h1
						class="font-headline-lg text-headline-lg text-on-surface font-bold tracking-tight"
					>
						{profile.nombre}
					</h1>
					<span
						class="inline-flex items-center gap-1 rounded bg-secondary-fixed px-2 py-0.5 font-label-sm text-label-sm text-on-secondary-fixed font-semibold uppercase tracking-wider"
					>
						<span class="material-symbols-outlined text-xs"
							>verified</span
						>
						{profile.estado}
					</span>
				</div>

				<div
					class="flex flex-wrap items-center gap-x-space-md gap-y-1 mt-1 text-on-surface-variant font-body-sm text-body-sm"
				>
					<span class="flex items-center gap-1">
						<span
							class="material-symbols-outlined text-base text-secondary"
							>badge</span
						>
						Matrícula:
						<strong
							class="text-on-surface font-semibold font-code-num text-code-num"
						>
							{profile.matricula}
						</strong>
					</span>
					<span class="flex items-center gap-1">
						<span
							class="material-symbols-outlined text-base text-secondary"
							>school</span
						>
						Carrera:
						<strong class="text-on-surface font-semibold">
							{profile.carrera} ({profile.plan})
						</strong>
					</span>
					<span class="flex items-center gap-1">
						<span
							class="material-symbols-outlined text-base text-secondary"
							>timelapse</span
						>
						Semestre Vigente:
						<strong class="text-on-surface font-semibold"
							>{profile.semestre}</strong
						>
					</span>
				</div>
			</div>
		</div>

		<div class="flex items-center gap-space-sm self-start lg:self-center">
			<button
				type="button"
				class="flex items-center gap-space-xs rounded bg-primary-container px-space-md py-space-sm text-on-primary font-label-md text-label-md font-semibold transition-all hover:bg-primary shadow-sm"
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
				class="relative flex items-center justify-center p-space-sm rounded bg-surface-container hover:bg-surface-container-high text-on-surface-variant hover:text-on-surface transition-colors"
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
