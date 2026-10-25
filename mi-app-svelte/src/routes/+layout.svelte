<script lang="ts">
	import favicon from "#lib/assets/favicon.svg";
	import Sidebar from "#lib/components/Sidebar.svelte";
	import Header from "#lib/components/Header.svelte";
	import type { LayoutProps } from "./$types";

	let { children }: LayoutProps = $props();
</script>

<svelte:head>
	<link rel="icon" href={favicon} />
</svelte:head>

<div class="bg-background font-body-md text-on-surface min-h-screen">
	<!-- Barra lateral institucional -->
	<Sidebar />

	<!-- Contenedor principal con offset para el sidebar -->
	<div class="pl-72">
		<!-- Barra superior con usuario y estado -->
		<Header />

		<!-- Renderizado de la ruta actual -->
		<main
			class="w-full pt-16 bg-background px-space-lg py-space-lg min-h-screen"
		>
			{@render children()}
		</main>
	</div>
</div>

<style>
	:global(body) {
		margin: 0;
		padding: 0;
		overscroll-behavior: none;
	}
	:global(::-webkit-scrollbar) {
		display: none;
	}
</style>
