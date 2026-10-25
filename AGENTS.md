# Pautas de trabajo para el Agente (Svelte 5 Project)

## Principios Generales
- Utiliza siempre sintaxis de Svelte 5 (Runes como `$state`, `$derived`, `$props`).
- Escribe todo el código en TypeScript de forma estricta (evita el uso de `any`).
- Responde siempre en español y mantén un tono técnico pero directo.
- Pide permiso antes de instalar librerías nuevas.

## Estructura y Archivos
- Las páginas de la app van estrictamente dentro de `src/routes/`.
- Los componentes reutilizables deben ubicarse en `src/lib/components/`.

## Convenciones de Código
- Aplica formato con Prettier.
- No modifiques variables de entorno `.env` sin solicitar confirmación explícita.