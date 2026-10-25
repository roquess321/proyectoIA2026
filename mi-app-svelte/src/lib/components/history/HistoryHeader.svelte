<script lang="ts">
	export interface Props {
		onExportPdf: () => void;
		onSyncInsweb: () => void;
		isSyncing: boolean;
	}

	let { onExportPdf, onSyncInsweb, isSyncing }: Props = $props();
</script>

<div class="flex flex-col md:flex-row md:items-end justify-between gap-space-md">
	<div class="flex flex-col gap-1">
		<div class="flex items-center gap-2">
			<span class="font-label-sm text-label-sm uppercase tracking-wider text-secondary font-bold">
				Malla Curricular Plan 2013
			</span>
			<span class="w-1.5 h-1.5 rounded-full bg-outline"></span>
			<span class="font-code-num text-code-num text-on-surface-variant">
				Matrícula: 16842-FIUNA
			</span>
		</div>
		<h1 class="font-headline-lg text-headline-lg text-primary tracking-tight font-bold">
			Historial Académico &amp; Malla Curricular
		</h1>
		<p class="font-body-sm text-body-sm text-on-surface-variant">
			Registro certificado de calificaciones convalidadas y visualizador dinámico de rutas
			correlativas.
		</p>
	</div>

	<div class="flex items-center gap-space-sm flex-wrap">
		<button
			type="button"
			class="flex items-center gap-2 bg-surface-container-lowest text-on-surface px-space-md py-2 rounded-lg shadow-sm hover:bg-surface-container transition-all cursor-pointer border border-outline-variant/30"
			onclick={onExportPdf}
		>
			<span class="material-symbols-outlined text-secondary text-base">picture_as_pdf</span>
			<span class="font-label-md text-label-md font-semibold">Exportar a PDF Oficial</span>
		</button>

		<button
			type="button"
			class="flex items-center gap-2 bg-primary text-on-primary px-space-md py-2 rounded-lg shadow-sm hover:bg-primary-container transition-all cursor-pointer font-semibold"
			onclick={onSyncInsweb}
			disabled={isSyncing}
		>
			<span
				class="material-symbols-outlined text-base {isSyncing ? 'animate-spin' : ''}"
			>
				sync
			</span>
			<span class="font-label-md text-label-md">
				{isSyncing ? 'Sincronizando...' : 'Sincronizar con InsWeb'}
			</span>
		</button>
	</div>
</div>
