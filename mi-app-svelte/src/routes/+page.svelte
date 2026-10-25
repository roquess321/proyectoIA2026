<script lang="ts">
    import { academicState } from "../lib/academic-state.svelte";
    import { goto } from "$app/navigation";

    let fiunaUser = $state("a.benitez");
    let fiunaPassword = $state("••••••••••••");
    let inswebCi = $state("4.819.302");
    let inswebPass = $state("••••••••");
    let selectedCareer = $state("electromecanica");

    let isSyncing = $state(false);
    let syncSuccess = $state(false);

    function handleSyncSubmit(event: SubmitEvent): void {
        event.preventDefault();
        if (isSyncing) return;

        isSyncing = true;
        syncSuccess = false;

        setTimeout(() => {
            isSyncing = false;
            syncSuccess = true;

            setTimeout(() => {
                academicState.activeNav = "dashboard-academico";
                goto("/dashboard");
            }, 900);
        }, 1500);
    }
</script>

<svelte:head>
    <title>Portal de Acceso &amp; Vinculación InsWeb - FIUNA</title>
</svelte:head>

<div class="flex flex-col w-full">
    <!-- Encabezado de la Sección -->
    <div
        class="relative mb-space-xl flex flex-col md:flex-row md:items-end justify-between gap-space-md"
    >
        <div class="flex flex-col gap-space-xs">
            <div class="flex items-center gap-space-xs">
                <span
                    class="inline-flex items-center justify-center w-6 h-6 rounded bg-primary text-on-primary"
                >
                    <span class="material-symbols-outlined text-sm"
                        >terminal</span
                    >
                </span>
                <span
                    class="font-label-sm text-label-sm uppercase tracking-wider text-secondary font-semibold"
                >
                    Submódulo de Extracción Segura
                </span>
            </div>
            <h1
                class="font-headline-lg text-headline-lg text-on-surface tracking-tight"
            >
                Portal de Acceso &amp; Vinculación InsWeb
            </h1>
            <p
                class="font-body-md text-body-md text-on-surface-variant max-w-2xl"
            >
                Conexión directa criptográfica con los servidores centrales de
                la Universidad Nacional de Asuncion (<code
                    class="font-code-num text-code-num text-on-surface bg-surface-container-high px-1 py-0.5 rounded"
                    >insweb.ing.una.py</code
                >) para la ingesta y análisis continuo del récord académico.
            </p>
        </div>

        <div
            class="flex items-center gap-space-sm bg-surface-container-lowest p-space-sm rounded-xl shadow-sm self-start md:self-auto"
        >
            <div
                class="w-3 h-3 rounded-full bg-emerald-500 animate-pulse"
            ></div>
            <div class="flex flex-col">
                <span
                    class="font-label-sm text-label-sm text-on-surface-variant"
                    >Conector Automatizado</span
                >
                <span
                    class="font-code-num text-code-num font-semibold text-on-surface"
                >
                    TLS 1.3 / FIUNA-SECURE
                </span>
            </div>
        </div>
    </div>

    <!-- Grilla Principal -->
    <div class="grid grid-cols-1 lg:grid-cols-12 gap-space-lg items-start">
        <!-- Columna Izquierda: Formulario de Credenciales -->
        <div class="lg:col-span-6 flex flex-col gap-space-lg">
            <div
                class="bg-surface-container-lowest rounded-xl shadow-sm p-space-xl flex flex-col gap-space-lg relative overflow-hidden"
            >
                <div
                    class="absolute -top-12 -right-12 w-48 h-48 bg-primary/5 rounded-full blur-2xl pointer-events-none"
                ></div>
                <div class="flex items-center justify-between">
                    <div class="flex items-center gap-space-sm">
                        <span
                            class="material-symbols-outlined text-primary text-2xl"
                            >passkey</span
                        >
                        <div>
                            <h2
                                class="font-headline-sm text-headline-sm text-on-surface font-bold"
                            >
                                Credenciales Académicas
                            </h2>
                            <span
                                class="font-body-sm text-body-sm text-on-surface-variant"
                            >
                                Autenticación Unificada de la Facultad
                            </span>
                        </div>
                    </div>
                    <span
                        class="px-space-sm py-1 bg-surface-container text-on-surface-variant rounded font-label-sm text-label-sm font-semibold uppercase"
                    >
                        Paso 1 de 2
                    </span>
                </div>

                <form
                    class="flex flex-col gap-space-md"
                    onsubmit={handleSyncSubmit}
                >
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-space-md">
                        <div class="flex flex-col gap-space-xs">
                            <label
                                class="font-label-sm text-label-sm text-on-surface font-semibold"
                                for="fiuna-user"
                            >
                                Usuario General FIUNA
                            </label>
                            <div class="relative flex items-center">
                                <span
                                    class="material-symbols-outlined absolute left-3 text-outline text-lg pointer-events-none"
                                >
                                    badge
                                </span>
                                <input
                                    class="w-full bg-surface-container-low text-on-surface font-body-md text-body-md pl-10 pr-3 py-2 rounded focus:outline-none focus:bg-surface-container-lowest focus:shadow-md transition-all"
                                    id="fiuna-user"
                                    placeholder="ej. j.perez"
                                    required
                                    type="text"
                                    bind:value={fiunaUser}
                                />
                            </div>
                        </div>

                        <div class="flex flex-col gap-space-xs">
                            <label
                                class="font-label-sm text-label-sm text-on-surface font-semibold"
                                for="fiuna-password"
                            >
                                Contraseña Institucional
                            </label>
                            <div class="relative flex items-center">
                                <span
                                    class="material-symbols-outlined absolute left-3 text-outline text-lg pointer-events-none"
                                >
                                    lock
                                </span>
                                <input
                                    class="w-full bg-surface-container-low text-on-surface font-body-md text-body-md pl-10 pr-3 py-2 rounded focus:outline-none focus:bg-surface-container-lowest focus:shadow-md transition-all"
                                    id="fiuna-password"
                                    placeholder="Contraseña institucional"
                                    required
                                    type="password"
                                    bind:value={fiunaPassword}
                                />
                            </div>
                        </div>
                    </div>

                    <div
                        class="bg-surface-container-low rounded-xl p-space-md flex flex-col gap-space-md relative overflow-hidden"
                    >
                        <div class="flex items-center justify-between">
                            <div
                                class="flex items-center gap-space-xs text-primary"
                            >
                                <span class="material-symbols-outlined text-lg"
                                    >cloud_sync</span
                                >
                                <span
                                    class="font-label-md text-label-md font-bold tracking-tight"
                                >
                                    Vinculación de Credenciales
                                    insweb.ing.una.py
                                </span>
                            </div>
                            <span
                                class="material-symbols-outlined text-secondary text-base"
                                >verified_user</span
                            >
                        </div>
                        <p
                            class="font-body-sm text-body-sm text-on-surface-variant"
                        >
                            Requerido para la extracción en segundo plano de
                            actas finales, asistencia e historial de malla
                            curricular.
                        </p>

                        <div
                            class="grid grid-cols-1 md:grid-cols-2 gap-space-sm"
                        >
                            <div class="flex flex-col gap-space-xs">
                                <label
                                    class="font-label-sm text-label-sm text-on-surface font-medium"
                                    for="insweb-ci"
                                >
                                    Cédula / Matrícula InsWeb
                                </label>
                                <div class="relative flex items-center">
                                    <span
                                        class="material-symbols-outlined absolute left-3 text-outline text-lg pointer-events-none"
                                    >
                                        fingerprint
                                    </span>
                                    <input
                                        class="w-full bg-surface-container-lowest text-on-surface font-code-num text-code-num pl-10 pr-3 py-2 rounded shadow-sm focus:outline-none focus:bg-surface-container-lowest transition-all"
                                        id="insweb-ci"
                                        placeholder="ej. 4580214"
                                        required
                                        type="text"
                                        bind:value={inswebCi}
                                    />
                                </div>
                            </div>

                            <div class="flex flex-col gap-space-xs">
                                <label
                                    class="font-label-sm text-label-sm text-on-surface font-medium"
                                    for="insweb-pass"
                                >
                                    Clave del Portal InsWeb
                                </label>
                                <div class="relative flex items-center">
                                    <span
                                        class="material-symbols-outlined absolute left-3 text-outline text-lg pointer-events-none"
                                    >
                                        key
                                    </span>
                                    <input
                                        class="w-full bg-surface-container-lowest text-on-surface font-code-num text-code-num pl-10 pr-3 py-2 rounded shadow-sm focus:outline-none transition-all"
                                        id="insweb-pass"
                                        placeholder="Clave de acceso al sistema"
                                        required
                                        type="password"
                                        bind:value={inswebPass}
                                    />
                                </div>
                            </div>
                        </div>

                        <div class="flex flex-col gap-space-xs">
                            <label
                                class="font-label-sm text-label-sm text-on-surface font-medium"
                                for="career-select"
                            >
                                Carrera de Ingeniería
                            </label>
                            <div class="relative flex items-center">
                                <span
                                    class="material-symbols-outlined absolute left-3 text-outline text-lg pointer-events-none"
                                >
                                    school
                                </span>
                                <select
                                    class="w-full bg-surface-container-lowest text-on-surface font-body-md text-body-md pl-10 pr-8 py-2 rounded shadow-sm focus:outline-none appearance-none cursor-pointer"
                                    id="career-select"
                                    bind:value={selectedCareer}
                                >
                                    <option value="electromecanica"
                                        >Ingeniería Electromecánica (Plan 2013)</option
                                    >
                                    <option value="civil"
                                        >Ingeniería Civil</option
                                    >
                                    <option value="industrial"
                                        >Ingeniería Industrial</option
                                    >
                                    <option value="electronica"
                                        >Ingeniería Electrónica</option
                                    >
                                    <option value="mecatronica"
                                        >Ingeniería Mecatrónica</option
                                    >
                                    <option value="geografica"
                                        >Ingeniería Geográfica y Ambiental</option
                                    >
                                </select>
                                <span
                                    class="material-symbols-outlined absolute right-3 text-outline text-base pointer-events-none"
                                >
                                    expand_more
                                </span>
                            </div>
                        </div>
                    </div>

                    <div
                        class="bg-surface-container-high/60 rounded-lg p-space-sm flex items-start gap-space-sm"
                    >
                        <span
                            class="material-symbols-outlined text-secondary text-lg mt-0.5"
                            >lock_clock</span
                        >
                        <div class="flex flex-col">
                            <span
                                class="font-label-sm text-label-sm text-on-surface font-semibold"
                            >
                                Cifrado de extremo a extremo (E2EE)
                            </span>
                            <p
                                class="font-body-sm text-body-sm text-on-surface-variant"
                            >
                                Las credenciales del portal InsWeb son
                                procesadas localmente en memoria volátil de
                                sesión y nunca se conservan en texto plano en la
                                infraestructura central de IA.
                            </p>
                        </div>
                    </div>

                    <button
                        class="w-full py-3 px-space-md text-on-primary rounded font-label-md text-label-md uppercase tracking-wider flex items-center justify-center gap-space-sm transition-all shadow-md active:scale-[0.99] mt-space-xs {syncSuccess
                            ? 'bg-emerald-700'
                            : 'bg-primary hover:bg-primary-container'}"
                        disabled={isSyncing}
                        type="submit"
                    >
                        <span
                            class="material-symbols-outlined text-lg {isSyncing
                                ? 'animate-spin'
                                : ''}"
                        >
                            {#if isSyncing}
                                autorenew
                            {:else if syncSuccess}
                                check_circle
                            {:else}
                                sync
                            {/if}
                        </span>
                        <span>
                            {#if isSyncing}
                                Estableciendo túnel HTTPS seguro...
                            {:else if syncSuccess}
                                ¡Conexión Validada con Éxito!
                            {:else}
                                Sincronizar e Iniciar Sesión con InsWeb
                            {/if}
                        </span>
                    </button>
                </form>

                <div
                    class="flex items-center justify-between pt-space-xs border-t-0"
                >
                    <a
                        class="font-label-sm text-label-sm text-secondary hover:text-on-surface flex items-center gap-1 transition-colors"
                        href="#ayuda"
                    >
                        <span class="material-symbols-outlined text-sm"
                            >help</span
                        >
                        ¿Problemas con tu PIN de InsWeb?
                    </a>
                    <span class="font-label-sm text-label-sm text-outline">
                        FIUNA Auth Node #3 (San Lorenzo)
                    </span>
                </div>
            </div>

            <div
                class="bg-surface-container rounded-xl p-space-lg flex items-center gap-space-md shadow-sm"
            >
                <div
                    class="h-16 w-16 rounded-xl overflow-hidden shrink-0 shadow-inner"
                >
                    <img
                        class="w-full h-full object-cover"
                        alt="Detalle de placa de circuito electrónico universitario"
                        src="https://lh3.googleusercontent.com/aida-public/AB6AXuDB_ed-DwBNGaoP4tnasZLrMI7imLs3tvqV0AMYjo-ycWIECz0K655ZsUatGSItYPGS1-OJLntXbNKgjObEHauPgkdrhk8iWTvu3Vja4j492Do--TOitdpdzQ1bKlMwIwHEUtbLZdHEYch0lixj2a3M4o__llHaJVCfASAsexRpYBsgG3-FQEidyse3qDDkijYqXGty7SZjnEKlFw6nMh6yggwgLFVLVUAmDs69q7okedUnpa1jmbn2"
                    />
                </div>
                <div class="flex flex-col">
                    <span
                        class="font-label-sm text-label-sm uppercase tracking-wider text-secondary font-semibold"
                    >
                        Conector Híbrido
                    </span>
                    <span
                        class="font-headline-sm text-headline-sm text-on-surface leading-tight font-bold"
                    >
                        Arquitectura de Ingesta Asíncrona
                    </span>
                    <p
                        class="font-body-sm text-body-sm text-on-surface-variant mt-0.5"
                    >
                        La canalización optimiza consultas por lotes para evitar
                        bloqueos por sobrecarga en el portal UNA.
                    </p>
                </div>
            </div>
        </div>

        <!-- Columna Derecha: Monitor de Scraping en Vivo -->
        <div class="lg:col-span-6 flex flex-col gap-space-lg">
            <div
                class="bg-surface-container-lowest rounded-xl shadow-sm p-space-xl flex flex-col gap-space-lg"
            >
                <div
                    class="flex flex-col sm:flex-row sm:items-center justify-between gap-space-sm pb-space-xs"
                >
                    <div class="flex items-center gap-space-sm">
                        <div
                            class="w-2.5 h-2.5 rounded-full bg-secondary"
                        ></div>
                        <div>
                            <h2
                                class="font-headline-sm text-headline-sm text-on-surface font-bold"
                            >
                                Monitor de Scraping en Vivo
                            </h2>
                            <span
                                class="font-body-sm text-body-sm text-on-surface-variant"
                            >
                                Diagnóstico de Pipeline & Telemetría
                            </span>
                        </div>
                    </div>
                    <button
                        class="px-space-sm py-1.5 bg-surface-container-low hover:bg-surface-container text-on-surface rounded font-label-sm text-label-sm flex items-center gap-space-xs shadow-sm transition-all active:scale-95 self-start sm:self-auto"
                        onclick={() => academicState.forceRescrape()}
                        type="button"
                    >
                        <span
                            class="material-symbols-outlined text-sm text-secondary {academicState.isRescraping
                                ? 'animate-spin'
                                : ''}"
                        >
                            refresh
                        </span>
                        <span>Forzar Re-scraping</span>
                    </button>
                </div>

                <div class="grid grid-cols-2 md:grid-cols-3 gap-space-sm">
                    <div
                        class="bg-surface-container-low rounded-lg p-space-sm flex flex-col gap-0.5"
                    >
                        <span
                            class="font-label-sm text-label-sm uppercase text-outline"
                        >
                            Latencia InsWeb
                        </span>
                        <div class="flex items-baseline gap-1">
                            <span
                                class="font-code-num text-headline-sm font-bold text-on-surface"
                            >
                                {academicState.latency}
                            </span>
                            <span
                                class="font-code-num text-code-num text-on-surface-variant"
                                >ms</span
                            >
                        </div>
                        <span
                            class="font-label-sm text-label-sm text-emerald-700 flex items-center gap-0.5"
                        >
                            <span class="material-symbols-outlined text-xs"
                                >check_circle</span
                            >
                            Servidor Nominal
                        </span>
                    </div>

                    <div
                        class="bg-surface-container-low rounded-lg p-space-sm flex flex-col gap-0.5"
                    >
                        <span
                            class="font-label-sm text-label-sm uppercase text-outline"
                        >
                            Estado Scraper
                        </span>
                        <div class="flex items-baseline gap-1">
                            <span
                                class="font-code-num text-headline-sm font-bold text-on-surface"
                            >
                                Óptimo
                            </span>
                        </div>
                        <span
                            class="font-label-sm text-label-sm text-secondary flex items-center gap-0.5"
                        >
                            <span class="material-symbols-outlined text-xs"
                                >bolt</span
                            >
                            Headless Chromium
                        </span>
                    </div>

                    <div
                        class="col-span-2 md:col-span-1 bg-surface-container-low rounded-lg p-space-sm flex flex-col gap-0.5"
                    >
                        <span
                            class="font-label-sm text-label-sm uppercase text-outline"
                            >Último Sync</span
                        >
                        <div class="flex items-baseline gap-1">
                            <span
                                class="font-code-num text-headline-sm font-bold text-on-surface"
                                >Hoy</span
                            >
                            <span
                                class="font-code-num text-code-num text-on-surface-variant"
                                >09:42</span
                            >
                        </div>
                        <span
                            class="font-label-sm text-label-sm text-on-surface-variant flex items-center gap-0.5"
                        >
                            <span class="material-symbols-outlined text-xs"
                                >schedule</span
                            >
                            Automático
                        </span>
                    </div>
                </div>

                <div class="flex flex-col gap-space-xs pt-space-xs">
                    <div class="flex items-center justify-between mb-space-xs">
                        <span
                            class="font-label-sm text-label-sm uppercase tracking-wider text-on-surface-variant font-semibold"
                        >
                            Fases del Pipeline de Extracción
                        </span>
                        <span
                            class="font-code-num text-code-num text-secondary font-semibold"
                            id="pipeline-status-text"
                        >
                            {academicState.pipelineStatus}
                        </span>
                    </div>

                    <div
                        class="flex flex-col gap-3 relative before:absolute before:left-3 before:top-3 before:bottom-3 before:w-0.5 before:bg-surface-container-high"
                    >
                        <div
                            class="flex items-start gap-space-md relative pl-1"
                        >
                            <span
                                class="z-10 flex h-5 w-5 rounded-full bg-emerald-500 text-on-error items-center justify-center shadow-sm"
                            >
                                <span class="material-symbols-outlined text-xs"
                                    >done</span
                                >
                            </span>
                            <div
                                class="flex-1 bg-surface-container-low p-space-sm rounded-lg flex flex-col sm:flex-row sm:items-center justify-between gap-1 shadow-sm"
                            >
                                <div class="flex flex-col">
                                    <span
                                        class="font-body-md text-body-md font-semibold text-on-surface leading-snug"
                                    >
                                        Handshake HTTPS insweb.ing.una.py
                                    </span>
                                    <span
                                        class="font-label-sm text-label-sm text-on-surface-variant"
                                    >
                                        Validación de certificados SSL y tokens
                                        de sesión activa
                                    </span>
                                </div>
                                <div class="flex items-center gap-space-xs">
                                    <span
                                        class="font-code-num text-code-num bg-surface-container-lowest px-2 py-0.5 rounded text-on-surface font-semibold"
                                    >
                                        120ms
                                    </span>
                                    <span
                                        class="px-2 py-0.5 rounded font-label-sm text-label-sm bg-emerald-100 text-emerald-800 font-semibold uppercase"
                                    >
                                        Completado
                                    </span>
                                </div>
                            </div>
                        </div>

                        <div
                            class="flex items-start gap-space-md relative pl-1"
                        >
                            <span
                                class="z-10 flex h-5 w-5 rounded-full bg-emerald-500 text-on-error items-center justify-center shadow-sm"
                            >
                                <span class="material-symbols-outlined text-xs"
                                    >done</span
                                >
                            </span>
                            <div
                                class="flex-1 bg-surface-container-low p-space-sm rounded-lg flex flex-col sm:flex-row sm:items-center justify-between gap-1 shadow-sm"
                            >
                                <div class="flex flex-col">
                                    <span
                                        class="font-body-md text-body-md font-semibold text-on-surface leading-snug"
                                    >
                                        Extracción de Legajo Académico y Ficha
                                        Alumno
                                    </span>
                                    <span
                                        class="font-label-sm text-label-sm text-on-surface-variant"
                                    >
                                        Parsing de C.I., matrícula oficial y
                                        plan vigente (Electromecánica)
                                    </span>
                                </div>
                                <div class="flex items-center gap-space-xs">
                                    <span
                                        class="font-code-num text-code-num bg-surface-container-lowest px-2 py-0.5 rounded text-on-surface font-semibold"
                                    >
                                        340ms
                                    </span>
                                    <span
                                        class="px-2 py-0.5 rounded font-label-sm text-label-sm bg-emerald-100 text-emerald-800 font-semibold uppercase"
                                    >
                                        Completado
                                    </span>
                                </div>
                            </div>
                        </div>

                        <div
                            class="flex items-start gap-space-md relative pl-1"
                        >
                            <span
                                class="z-10 flex h-5 w-5 rounded-full bg-emerald-500 text-on-error items-center justify-center shadow-sm"
                            >
                                <span class="material-symbols-outlined text-xs"
                                    >done</span
                                >
                            </span>
                            <div
                                class="flex-1 bg-surface-container-low p-space-sm rounded-lg flex flex-col sm:flex-row sm:items-center justify-between gap-1 shadow-sm"
                            >
                                <div class="flex flex-col">
                                    <span
                                        class="font-body-md text-body-md font-semibold text-on-surface leading-snug"
                                    >
                                        Scraping de Calificaciones Históricas
                                        (Actas 2020-2024)
                                    </span>
                                    <span
                                        class="font-label-sm text-label-sm text-on-surface-variant"
                                    >
                                        Extracción de 62 asignaturas cursadas,
                                        firmas y ponderaciones
                                    </span>
                                </div>
                                <div class="flex items-center gap-space-xs">
                                    <span
                                        class="font-code-num text-code-num bg-surface-container-lowest px-2 py-0.5 rounded text-on-surface font-semibold"
                                    >
                                        62 materias
                                    </span>
                                    <span
                                        class="px-2 py-0.5 rounded font-label-sm text-label-sm bg-emerald-100 text-emerald-800 font-semibold uppercase"
                                    >
                                        Completado
                                    </span>
                                </div>
                            </div>
                        </div>

                        <div
                            class="flex items-start gap-space-md relative pl-1"
                        >
                            <span
                                class="z-10 flex h-5 w-5 rounded-full bg-emerald-500 text-on-error items-center justify-center shadow-sm"
                            >
                                <span class="material-symbols-outlined text-xs"
                                    >done</span
                                >
                            </span>
                            <div
                                class="flex-1 bg-surface-container-low p-space-sm rounded-lg flex flex-col sm:flex-row sm:items-center justify-between gap-1 shadow-sm"
                            >
                                <div class="flex flex-col">
                                    <span
                                        class="font-body-md text-body-md font-semibold text-on-surface leading-snug"
                                    >
                                        Parseo de Inscripción Actual Semestre
                                        2024-2
                                    </span>
                                    <span
                                        class="font-label-sm text-label-sm text-on-surface-variant"
                                    >
                                        5 cátedras en curso detectadas con
                                        control de asistencia al 94%
                                    </span>
                                </div>
                                <div class="flex items-center gap-space-xs">
                                    <span
                                        class="font-code-num text-code-num bg-surface-container-lowest px-2 py-0.5 rounded text-on-surface font-semibold"
                                    >
                                        5 asignaturas
                                    </span>
                                    <span
                                        class="px-2 py-0.5 rounded font-label-sm text-label-sm bg-emerald-100 text-emerald-800 font-semibold uppercase"
                                    >
                                        Completado
                                    </span>
                                </div>
                            </div>
                        </div>

                        <div
                            class="flex items-start gap-space-md relative pl-1"
                        >
                            <span
                                class="z-10 flex h-5 w-5 rounded-full bg-secondary text-on-primary items-center justify-center shadow-sm"
                            >
                                <span class="material-symbols-outlined text-xs"
                                    >psychology</span
                                >
                            </span>
                            <div
                                class="flex-1 bg-surface-container-low p-space-sm rounded-lg flex flex-col sm:flex-row sm:items-center justify-between gap-1 shadow-sm"
                            >
                                <div class="flex flex-col">
                                    <span
                                        class="font-body-md text-body-md font-semibold text-on-surface leading-snug"
                                    >
                                        Carga en el Motor de Inferencia IA FIUNA
                                    </span>
                                    <span
                                        class="font-label-sm text-label-sm text-on-surface-variant"
                                    >
                                        Embeddings matriciales calibrados y
                                        pronósticos listos
                                    </span>
                                </div>
                                <div class="flex items-center gap-space-xs">
                                    <span
                                        class="font-code-num text-code-num bg-secondary-fixed text-on-secondary-fixed px-2 py-0.5 rounded font-semibold"
                                    >
                                        Modelos Listos
                                    </span>
                                    <span
                                        class="px-2 py-0.5 rounded font-label-sm text-label-sm bg-secondary text-on-secondary font-semibold uppercase"
                                    >
                                        Activo
                                    </span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <div
                    class="bg-surface-container rounded-lg p-space-md flex flex-col gap-space-xs"
                >
                    <div class="flex items-center justify-between">
                        <span
                            class="font-label-sm text-label-sm uppercase font-semibold text-on-surface"
                        >
                            Rendimiento de Parseo de Datos UNA
                        </span>
                        <span
                            class="font-code-num text-code-num text-on-surface font-semibold"
                        >
                            100 % de integridad
                        </span>
                    </div>
                    <div
                        class="w-full bg-surface-container-high h-2 rounded overflow-hidden"
                    >
                        <div
                            class="bg-secondary h-full rounded transition-all duration-700"
                            style="width: 100%;"
                        ></div>
                    </div>
                    <div
                        class="flex items-center justify-between text-on-surface-variant font-label-sm text-label-sm mt-0.5"
                    >
                        <span>67 Registros normalizados</span>
                        <span>0 Excepciones de red</span>
                    </div>
                </div>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-2 gap-space-md">
                <div
                    class="bg-surface-container-lowest p-space-md rounded-xl shadow-sm flex items-center gap-space-md"
                >
                    <div
                        class="h-12 w-12 rounded-lg bg-surface-container-low flex items-center justify-center text-primary shrink-0"
                    >
                        <span class="material-symbols-outlined text-2xl"
                            >dns</span
                        >
                    </div>
                    <div class="flex flex-col min-w-0">
                        <span
                            class="font-label-sm text-label-sm text-on-surface-variant"
                        >
                            Servidor Principal
                        </span>
                        <span
                            class="font-body-md text-body-md font-semibold text-on-surface truncate"
                        >
                            insweb.ing.una.py:443
                        </span>
                        <span
                            class="font-code-num text-code-num text-emerald-700"
                        >
                            Online / Sin demoras
                        </span>
                    </div>
                </div>

                <div
                    class="bg-surface-container-lowest p-space-md rounded-xl shadow-sm flex items-center gap-space-md"
                >
                    <div
                        class="h-12 w-12 rounded-lg bg-surface-container-low flex items-center justify-center text-primary shrink-0"
                    >
                        <span class="material-symbols-outlined text-2xl"
                            >security_update_good</span
                        >
                    </div>
                    <div class="flex flex-col min-w-0">
                        <span
                            class="font-label-sm text-label-sm text-on-surface-variant"
                        >
                            Integración API
                        </span>
                        <span
                            class="font-body-md text-body-md font-semibold text-on-surface truncate"
                        >
                            FIUNA-Sync v2.4
                        </span>
                        <span
                            class="font-code-num text-code-num text-secondary"
                        >
                            Cripto-Worker Listo
                        </span>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- Bottom Action Box -->
    <div
        class="mt-space-xl p-space-lg bg-surface-container-low rounded-xl flex flex-col md:flex-row items-center justify-between gap-space-md"
    >
        <div class="flex items-center gap-space-md">
            <div
                class="w-10 h-10 rounded-full bg-primary flex items-center justify-center text-on-primary shrink-0"
            >
                <span class="material-symbols-outlined">auto_graph</span>
            </div>
            <div class="flex flex-col">
                <span
                    class="font-label-md text-label-md font-bold text-on-surface"
                >
                    Próximo paso tras la validación de InsWeb
                </span>
                <span class="font-body-sm text-body-sm text-on-surface-variant">
                    El simulador proyectará de inmediato tus probabilidades de
                    firma para el 2.º Ciclo 2024.
                </span>
            </div>
        </div>
        <div class="flex items-center gap-space-sm w-full md:w-auto">
            <a
                href="/dashboard"
                class="w-full md:w-auto px-space-lg py-2.5 bg-primary text-on-primary rounded font-label-md text-label-md uppercase tracking-wider font-semibold text-center hover:bg-primary-container transition-all shadow-sm inline-block"
                onclick={() =>
                    (academicState.activeNav = "dashboard-academico")}
                >Acceder al Dashboard Principal</a
            >
        </div>
    </div>
</div>
