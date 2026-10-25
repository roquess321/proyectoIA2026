---
name: svelte-5-rules
description: Directivas y buenas prácticas para desarrollo con Svelte 5 y SvelteKit.
---

# Reglas de desarrollo en Svelte 5

- **Uso estricto de Runes:**
  - Usa `$state()` para declarar variables de estado en lugar de asignaciones simples.
  - Usa `$derived()` para valores calculados o derivados en lugar de marcas reactivas `$:`.
  - Usa `$props()` para recibir propiedades en el componente en lugar de `export let`.
  - Usa `$effect()` para efectos secundarios.
- **Estructura de Componentes:**
  - Mantén el bloque `<script lang="ts">` en la parte superior, seguido de la plantilla HTML y el bloque `<style>`.
- **Enrutamiento SvelteKit:**
  - Coloca las vistas en `src/routes/+page.svelte`.
  - Define la lógica del servidor en `src/routes/+page.server.ts`.