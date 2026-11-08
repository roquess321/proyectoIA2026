<script lang="ts">
	import { authState } from "../../auth-state.svelte";

	export interface Props {
		onExportPdf: () => void;
		onSyncInsweb: () => void;
		isSyncing: boolean;
		cedula?: string;
		carrera?: string;
	}

	let { onExportPdf, onSyncInsweb, isSyncing, cedula, carrera }: Props = $props();

	let displayCedula = $derived(cedula || authState.user?.cedula || "16842-FIUNA");
	let displayCarrera = $derived(carrera || authState.user?.carrera || "Malla Curricular Plan 2013");
</script>

<div class="flex flex-col md:flex-row md:items-end justify-between gap-space-md">
	<div class="flex flex-col gap-1">
		<div class="flex flex-wrap items-center gap-2">
			<span class="font-label-sm text-xs sm:text-label-sm uppercase tracking-wider text-secondary font-bold">
				{displayCarrera}
			</span>
			<span class="w-1.5 h-1.5 rounded-full bg-outline"></span>
			<span class="font-code-num text-xs sm:text-code-num text-on-surface-variant font-medium">
				C.I. / Matrícula: {displayCedula}
			</span>
		</div>
		<h1 class="font-headline-lg text-2xl sm:text-headline-lg text-primary tracking-tight font-bold">
			Historial Académico &amp; Malla Curricular
		</h1>
		<p class="font-body-sm text-body-sm text-on-surface-variant">
			Registro certificado de calificaciones convalidadas y visualizador dinámico de rutas
			correlativas.
		</p>
	</div>

	<div class="flex items-center gap-2 sm:gap-space-sm flex-wrap w-full md:w-auto">
		<button
			type="button"
			class="flex-1 sm:flex-none flex items-center justify-center gap-2 bg-surface-container-lowest text-on-surface px-3 sm:px-space-md py-2 rounded-lg shadow-sm hover:bg-surface-container transition-all cursor-pointer border border-outline-variant/30 text-xs sm:text-label-md"
			onclick={onExportPdf}
		>
			<span class="material-symbols-outlined text-secondary text-base">picture_as_pdf</span>
			<span class="font-label-md font-semibold">Exportar PDF</span>
		</button>

		<button
			type="button"
			class="flex-1 sm:flex-none flex items-center justify-center gap-2 bg-primary text-on-primary px-3 sm:px-space-md py-2 rounded-lg shadow-sm hover:bg-primary-container transition-all cursor-pointer font-semibold text-xs sm:text-label-md"
			onclick={onSyncInsweb}
			disabled={isSyncing}
		>
			<span
				class="material-symbols-outlined text-base {isSyncing ? 'animate-spin' : ''}"
			>
				sync
			</span>
			<span class="font-label-md">
				{isSyncing ? 'Sincronizando...' : 'Sincronizar InsWeb'}
			</span>
		</button>
	</div>
</div>
