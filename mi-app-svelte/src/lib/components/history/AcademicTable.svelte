<script lang="ts">
	import type { AcademicRecord } from '../../types/academic-history';

	export interface Props {
		records: AcademicRecord[];
		selectedRecord: AcademicRecord;
		onSelectRecord: (record: AcademicRecord) => void;
	}

	let { records, selectedRecord, onSelectRecord }: Props = $props();

	let periodFilter = $state('ALL');
	let deptFilter = $state('ALL');
	let statusFilter = $state('ALL');
	let searchQuery = $state('');

	let filteredRecords = $derived(
		records.filter((rec) => {
			const matchPeriod = periodFilter === 'ALL' || rec.period === periodFilter;
			const matchDept = deptFilter === 'ALL' || rec.department === deptFilter;
			const matchStatus = statusFilter === 'ALL' || rec.status === statusFilter;
			const query = searchQuery.toLowerCase().trim();
			const matchSearch =
				query === '' ||
				rec.code.toLowerCase().includes(query) ||
				rec.name.toLowerCase().includes(query) ||
				rec.departmentName.toLowerCase().includes(query);

			return matchPeriod && matchDept && matchStatus && matchSearch;
		})
	);
</script>

<div class="flex flex-col gap-space-md">
	<!-- Filter Toolbar -->
	<div
		class="bg-surface-container-lowest p-space-md rounded-xl shadow-sm flex flex-col md:flex-row gap-space-md items-center justify-between border border-outline-variant/30"
	>
		<div class="grid grid-cols-1 sm:grid-cols-3 gap-space-sm w-full md:w-auto flex-1">
			<!-- Period Filter -->
			<div class="flex flex-col gap-1">
				<label class="font-label-sm text-label-sm uppercase text-on-surface-variant font-semibold" for="filter-period">
					Periodo
				</label>
				<select
					id="filter-period"
					class="bg-surface-container-low text-on-surface font-body-sm text-body-sm py-1.5 px-space-sm rounded border border-outline-variant/30 focus:outline-none focus:ring-1 focus:ring-secondary cursor-pointer"
					bind:value={periodFilter}
				>
					<option value="ALL">Todos los Periodos</option>
					<option value="2021-1">2021-1 (1er Ciclo)</option>
					<option value="2021-2">2021-2 (2do Ciclo)</option>
					<option value="2022-2">2022-2 (2do Ciclo)</option>
					<option value="2023-1">2023-1 (1er Ciclo)</option>
					<option value="2024-2">2024-2 (2do Ciclo)</option>
					<option value="Proyectado">Proyectado</option>
				</select>
			</div>

			<!-- Department Filter -->
			<div class="flex flex-col gap-1">
				<label class="font-label-sm text-label-sm uppercase text-on-surface-variant font-semibold" for="filter-dept">
					Departamento
				</label>
				<select
					id="filter-dept"
					class="bg-surface-container-low text-on-surface font-body-sm text-body-sm py-1.5 px-space-sm rounded border border-outline-variant/30 focus:outline-none focus:ring-1 focus:ring-secondary cursor-pointer"
					bind:value={deptFilter}
				>
					<option value="ALL">Todos los Departamentos</option>
					<option value="MAT">Matemática</option>
					<option value="FIS">Física</option>
					<option value="MEC">Mecánica</option>
					<option value="ELE">Eléctrica</option>
					<option value="HUM">Humanidades &amp; Gestión</option>
				</select>
			</div>

			<!-- Status Filter -->
			<div class="flex flex-col gap-1">
				<label class="font-label-sm text-label-sm uppercase text-on-surface-variant font-semibold" for="filter-status">
					Estado
				</label>
				<select
					id="filter-status"
					class="bg-surface-container-low text-on-surface font-body-sm text-body-sm py-1.5 px-space-sm rounded border border-outline-variant/30 focus:outline-none focus:ring-1 focus:ring-secondary cursor-pointer"
					bind:value={statusFilter}
				>
					<option value="ALL">Todos los Estados</option>
					<option value="APROBADA">Aprobadas</option>
					<option value="CURSO">En Curso</option>
					<option value="PENDIENTE">Pendientes</option>
				</select>
			</div>
		</div>

		<!-- Live Search -->
		<div class="flex items-center gap-space-sm w-full md:w-auto justify-end">
			<div class="relative w-full md:w-56">
				<span
					class="material-symbols-outlined absolute left-2.5 top-2 text-on-surface-variant text-sm pointer-events-none"
				>
					search
				</span>
				<input
					type="text"
					class="w-full bg-surface-container-low text-on-surface font-body-sm text-body-sm pl-8 pr-space-sm py-1.5 rounded placeholder:text-on-surface-variant border border-outline-variant/30 focus:outline-none focus:ring-1 focus:ring-secondary"
					placeholder="Buscar asignatura o código..."
					bind:value={searchQuery}
				/>
			</div>
		</div>
	</div>

	<!-- Table Card -->
	<div class="bg-surface-container-lowest rounded-xl shadow-sm overflow-hidden border border-outline-variant/30">
		<div class="overflow-x-auto">
			<table class="w-full text-left border-collapse">
				<thead>
					<tr
						class="bg-surface-container-low text-on-surface-variant font-label-sm text-label-sm uppercase tracking-wider border-b border-outline-variant/20"
					>
						<th class="py-space-sm px-space-md">Código</th>
						<th class="py-space-sm px-space-md">Asignatura</th>
						<th class="py-space-sm px-space-sm text-center">Semestre</th>
						<th class="py-space-sm px-space-sm text-center">Calificación</th>
						<th class="py-space-sm px-space-sm">Oportunidad</th>
						<th class="py-space-sm px-space-sm text-center">Créd.</th>
						<th class="py-space-sm px-space-sm">Periodo</th>
						<th class="py-space-sm px-space-sm font-code-num text-code-num">Acta InsWeb</th>
						<th class="py-space-sm px-space-md text-right">Estado</th>
					</tr>
				</thead>
				<tbody class="font-body-sm text-body-sm divide-y divide-outline-variant/10">
					{#each filteredRecords as row (row.code)}
						<tr
							class="hover:bg-surface-container cursor-pointer transition-colors {selectedRecord.code ===
							row.code
								? 'bg-surface-container-high/80'
								: ''}"
							onclick={() => onSelectRecord(row)}
						>
							<td class="py-space-sm px-space-md font-code-num text-code-num font-semibold text-primary">
								{row.code}
							</td>
							<td class="py-space-sm px-space-md font-medium text-on-surface">
								{row.name}
							</td>
							<td class="py-space-sm px-space-sm text-center text-on-surface-variant font-code-num">
								{row.semester}
							</td>
							<td class="py-space-sm px-space-sm text-center">
								{#if row.grade !== null}
									<span
										class="inline-flex items-center justify-center w-6 h-6 rounded font-bold {row.grade ===
										5
											? 'bg-surface-container-highest text-secondary'
											: 'bg-surface-container-high text-primary'}"
									>
										{row.grade}
									</span>
								{:else}
									<span class="text-on-surface-variant font-code-num text-code-num">—</span>
								{/if}
							</td>
							<td class="py-space-sm px-space-sm text-on-surface-variant">
								{row.opportunity}
							</td>
							<td class="py-space-sm px-space-sm text-center font-code-num text-code-num">
								{row.credits}
							</td>
							<td class="py-space-sm px-space-sm font-code-num text-code-num">
								{row.period}
							</td>
							<td class="py-space-sm px-space-sm font-code-num text-code-num text-on-surface-variant">
								{row.actaNumber}
							</td>
							<td class="py-space-sm px-space-md text-right">
								<span
									class="font-label-sm text-label-sm px-2 py-0.5 rounded font-semibold {row.status ===
									'APROBADA'
										? 'bg-surface-container-high text-on-surface'
										: row.status === 'CURSO'
											? 'bg-secondary-fixed text-on-secondary-fixed'
											: 'bg-surface-container text-on-surface-variant'}"
								>
									{row.status === 'APROBADA'
										? 'Aprobada'
										: row.status === 'CURSO'
											? 'En Curso'
											: 'Pendiente'}
								</span>
							</td>
						</tr>
					{:else}
						<tr>
							<td colspan="9" class="py-space-lg text-center text-on-surface-variant">
								No se encontraron asignaturas con los filtros seleccionados.
							</td>
						</tr>
					{/each}
				</tbody>
			</table>
		</div>

		<!-- Footer -->
		<div
			class="p-space-md bg-surface-container-low flex flex-col sm:flex-row items-center justify-between gap-space-sm border-t border-outline-variant/20"
		>
			<span class="font-body-sm text-body-sm text-on-surface-variant">
				Mostrando cátedras registradas en Sistema de Gestión Académica InsWeb FIUNA
			</span>
			<div class="flex items-center gap-1 font-label-sm text-label-sm">
				<span class="material-symbols-outlined text-secondary text-sm">lock</span>
				<span class="text-on-surface-variant font-medium">
					Validación con firma digital institucional activa
				</span>
			</div>
		</div>
	</div>
</div>
