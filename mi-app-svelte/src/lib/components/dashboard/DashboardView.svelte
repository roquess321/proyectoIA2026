<script lang="ts">
	import { onMount } from "svelte";
	import { academicState } from "../../academic-state.svelte";
	import {
		studentProfile,
		metricCards,
		courses,
		examEvents,
	} from "../../data/dashboard-mock";
	import StatusBanner from "./StatusBanner.svelte";
	import StatCards from "./StatCards.svelte";
	import CourseTracker from "./CourseTracker.svelte";
	import ExamCalendar from "./ExamCalendar.svelte";
	import AiCopilotCard from "./AiCopilotCard.svelte";
	import NoticeCard from "./NoticeCard.svelte";

	onMount(() => {
		academicState.activeNav = "dashboard";
	});
</script>

<svelte:head>
	<title>Dashboard Académico - FIUNA Academic AI Suite</title>
</svelte:head>

<div class="flex flex-col w-full gap-space-lg">
	<!-- Academic Status Banner -->
	<StatusBanner profile={studentProfile} />

	<!-- Key Metric Stat Cards Bento Grid -->
	<StatCards metrics={metricCards} />

	<!-- Main Grid: Course Tracker & Exam Calendar Widget -->
	<div class="grid grid-cols-1 lg:grid-cols-12 gap-space-lg items-start">
		<!-- Left: Current Enrolled Courses Grid (8 Cols) -->
		<div class="lg:col-span-8">
			<CourseTracker {courses} />
		</div>

		<!-- Right: Exam Calendar Widget & AI Copilot (4 Cols) -->
		<div class="lg:col-span-4 flex flex-col gap-space-md">
			<ExamCalendar exams={examEvents} />
			<AiCopilotCard />
			<NoticeCard />
		</div>
	</div>
</div>
