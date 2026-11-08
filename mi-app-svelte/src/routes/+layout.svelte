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

	<!-- Contenedor principal con offset para el sidebar en pantallas grandes -->
	<div class="pl-0 lg:pl-72 transition-[padding] duration-300">
		<!-- Barra superior con usuario y estado -->
		<Header />

		<!-- Renderizado de la ruta actual con espacio superior suficiente para que el header fijo nunca se superponga -->
		<main
			class="w-full pt-20 sm:pt-20 lg:pt-24 pb-10 sm:pb-16 bg-background px-3 sm:px-space-md lg:px-space-lg min-h-screen"
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
