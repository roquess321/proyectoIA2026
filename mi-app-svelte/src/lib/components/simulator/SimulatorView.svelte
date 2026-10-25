<script lang="ts">
	import { onMount } from 'svelte';
	import { academicState } from '../../academic-state.svelte';
	import {
		simulationSubjects,
		quickPrompts
	} from '../../data/simulator-mock';
	import PredictiveHeader from './PredictiveHeader.svelte';
	import GaugeChart from './GaugeChart.svelte';
	import EvaluationMatrix from './EvaluationMatrix.svelte';
	import FinalExamScenarios from './FinalExamScenarios.svelte';
	import AiCopilotChat from './AiCopilotChat.svelte';

	onMount(() => {
		academicState.activeNav = 'agente-ia-pronosticos';
	});

	let selectedSubjectId = $state('mec-431');
	let p2Value = $state(14);

	let currentSubject = $derived(
		simulationSubjects.find((s) => s.id === selectedSubjectId) ?? simulationSubjects[0]
	);

	function handleSubjectChange(newId: string) {
		selectedSubjectId = newId;
		const found = simulationSubjects.find((s) => s.id === newId);
		if (found) {
			p2Value = found.defaultP2;
		}
	}

	function handleSetP2(val: number) {
		p2Value = val;
	}

	// Dynamic derived calculations
	let totalProcess = $derived(currentSubject.p1 + p2Value + currentSubject.lab);

	let probability = $derived(
		Math.max(10, Math.min(96, Math.round(15 + (totalProcess / 50) * 82)))
	);
</script>

<svelte:head>
	<title>Simulador Predictivo &amp; Agente IA - FIUNA Academic AI Suite</title>
</svelte:head>

<div class="flex flex-col w-full gap-space-lg">
	<!-- Top Predictive Status & Metric Header -->
	<PredictiveHeader
		subjects={simulationSubjects}
		{selectedSubjectId}
		onSubjectChange={handleSubjectChange}
	/>

	<!-- Primary Workspace: 2-Column Split Layout -->
	<div class="grid grid-cols-12 gap-space-lg items-start">
		<!-- LEFT COLUMN: Predictive Engine & Matrix (60% ~ 7 cols desktop) -->
		<div class="col-span-12 xl:col-span-7 flex flex-col gap-space-lg">
			<!-- Top Live Gauge & Mathematical Probability -->
			<GaugeChart {probability} {totalProcess} />

			<!-- Parametric Evaluation Matrix & Slider -->
			<EvaluationMatrix
				subject={currentSubject}
				{p2Value}
				onP2Change={handleSetP2}
			/>

			<!-- Simulated Final Exam Scenarios (1 al 5) -->
			<FinalExamScenarios
				subject={currentSubject}
				{totalProcess}
				{p2Value}
			/>
		</div>

		<!-- RIGHT COLUMN: AI Copilot Academic Conversational Agent (40% ~ 5 cols desktop) -->
		<AiCopilotChat
			subject={currentSubject}
			{quickPrompts}
			onSetP2={handleSetP2}
			onSwitchSubject={handleSubjectChange}
		/>
	</div>
</div>
