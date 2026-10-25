<script lang="ts">
	import { onMount } from 'svelte';
	import { academicState } from '../../academic-state.svelte';
	import {
		historyStats,
		academicRecords,
		curriculumBlocks
	} from '../../data/academic-history-mock';
	import type { AcademicRecord } from '../../types/academic-history';
	import HistoryHeader from './HistoryHeader.svelte';
	import HistoryStats from './HistoryStats.svelte';
	import AcademicTable from './AcademicTable.svelte';
	import CorrelativesPanel from './CorrelativesPanel.svelte';
	import CurriculumGrid from './CurriculumGrid.svelte';

	onMount(() => {
		academicState.activeNav = 'historial-malla-curricular';
	});

	let activeTab = $state<'history' | 'curriculum'>('history');
	let isSyncing = $state(false);
	let toastMessage = $state<string | null>(null);

	// Select default course as ELE18 (matching the original template)
	let selectedRecord = $state<AcademicRecord>(
		academicRecords.find((r) => r.code === 'ELE18') ?? academicRecords[0]
	);

	function showToast(message: string, durationMs = 3500) {
		toastMessage = message;
		setTimeout(() => {
			if (toastMessage === message) {
				toastMessage = null;
			}
		}, durationMs);
	}

	function handleExportPdf() {
		showToast(
			'Generando Certificado Oficial de Historial Académico y Malla con código QR de verificación...'
		);
	}

	function handleSyncInsweb() {
		if (isSyncing) return;
		isSyncing = true;

		setTimeout(() => {
			isSyncing = false;
			showToast(
				'Sincronización con el servidor de InsWeb FIUNA completada con éxito. 52 registros verificados.'
			);
		}, 1200);
	}

	function handleSelectRecord(record: AcademicRecord) {
		selectedRecord = record;
	}

	function handleSelectCourseByCode(code: string) {
		const found = academicRecords.find((r) => r.code === code);
		if (found) {
			selectedRecord = found;
			activeTab = 'history';
		}
	}
</script>

<svelte:head>
	<title>Historial Académico &amp; Malla Curricular - FIUNA Academic AI Suite</title>
</svelte:head>

<div class="flex flex-col w-full gap-space-lg relative">
	<!-- Toast notification -->
	{#if toastMessage}
		<div
			class="fixed bottom-6 right-6 z-50 bg-primary text-on-primary px-space-md py-3 rounded-lg shadow-xl border border-secondary/30 flex items-center gap-space-sm max-w-md animate-fade-in"
		>
			<span class="material-symbols-outlined text-secondary text-xl">info</span>
			<span class="font-body-sm text-body-sm font-medium">{toastMessage}</span>
			<button
				type="button"
				class="ml-auto text-on-primary/70 hover:text-on-primary cursor-pointer"
				onclick={() => (toastMessage = null)}
			>
				<span class="material-symbols-outlined text-base">close</span>
			</button>
		</div>
	{/if}

	<!-- Top Header & Actions -->
	<HistoryHeader
		onExportPdf={handleExportPdf}
		onSyncInsweb={handleSyncInsweb}
		{isSyncing}
	/>

	<!-- 5 Key Metric Stat Cards -->
	<HistoryStats stats={historyStats} />

	<!-- Tab Switcher Bar -->
	<div
		class="flex items-center justify-between bg-surface-container-lowest rounded-xl p-1 shadow-sm border border-outline-variant/30"
	>
		<div class="flex gap-1" id="tab-controls">
			<button
				type="button"
				class="flex items-center gap-2 px-space-md py-2 rounded-lg font-semibold transition-all cursor-pointer {activeTab ===
				'history'
					? 'bg-primary-container text-white dark:bg-[#132c4d] dark:text-[#d3e4fe] shadow-sm'
					: 'text-on-surface-variant hover:bg-surface-container hover:text-on-surface dark:hover:bg-surface-container-high dark:hover:text-on-surface'}"
				onclick={() => (activeTab = 'history')}
			>
				<span
					class="material-symbols-outlined text-base {activeTab === 'history'
						? 'text-secondary-fixed dark:text-[#b1c7f0]'
						: ''}"
				>
					format_list_bulleted
				</span>
				<span class="font-label-md text-label-md">Historial de Calificaciones (Datos InsWeb)</span>
			</button>

			<button
				type="button"
				class="flex items-center gap-2 px-space-md py-2 rounded-lg font-semibold transition-all cursor-pointer {activeTab ===
				'curriculum'
					? 'bg-primary-container text-white dark:bg-[#132c4d] dark:text-[#d3e4fe] shadow-sm'
					: 'text-on-surface-variant hover:bg-surface-container hover:text-on-surface dark:hover:bg-surface-container-high dark:hover:text-on-surface'}"
				onclick={() => (activeTab = 'curriculum')}
			>
				<span
					class="material-symbols-outlined text-base {activeTab === 'curriculum'
						? 'text-secondary-fixed dark:text-[#b1c7f0]'
						: ''}"
				>
					schema
				</span>
				<span class="font-label-md text-label-md">Malla Curricular &amp; Correlativas</span>
			</button>
		</div>

		<div
			class="hidden md:flex items-center gap-2 px-space-md text-on-surface-variant font-code-num text-code-num"
		>
			<span class="w-2 h-2 rounded-full bg-secondary"></span>
			Cálculo de Promedio Oficial FIUNA: Escala 1 al 5
		</div>
	</div>

	<!-- TAB 1: History Table + Correlatives Panel -->
	{#if activeTab === 'history'}
		<div class="grid grid-cols-1 xl:grid-cols-12 gap-space-lg">
			<!-- Left: Academic Table with Filters (8 cols) -->
			<div class="xl:col-span-8">
				<AcademicTable
					records={academicRecords}
					{selectedRecord}
					onSelectRecord={handleSelectRecord}
				/>
			</div>

			<!-- Right: Correlatives Inspector Panel (4 cols) -->
			<div class="xl:col-span-4">
				<CorrelativesPanel {selectedRecord} />
			</div>
		</div>
	{:else}
		<!-- TAB 2: Curriculum Sequential Flow -->
		<CurriculumGrid
			blocks={curriculumBlocks}
			onSelectCourseByCode={handleSelectCourseByCode}
		/>
	{/if}
</div>
