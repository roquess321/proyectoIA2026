<script lang="ts">
    import { academicState } from "../lib/academic-state.svelte";
    import { authState } from "../lib/auth-state.svelte";
    import { goto } from "$app/navigation";
    import {
        loginLocalUser,
        registerLocalUser,
        linkInswebAccount,
        type LinkInswebResult
    } from "../lib/services/auth";

    // Pestaña activa cuando no está autenticado: 'login' | 'register'
    let activeAuthTab = $state<"login" | "register">("login");
    const user = $derived(authState.user);

    // Formulario de Inicio de Sesión Local
    let loginIdentifier = $state("");
    let loginPassword = $state("");
    let isLoggingIn = $state(false);
    let loginError = $state<string | null>(null);

    // Formulario de Registro Local
    let regNombre = $state("");
    let regUsuario = $state("");
    let regCedula = $state("");
    let regPassword = $state("");
    let regConfirmPassword = $state("");
    let regCarrera = $state("Ingeniería Electromecánica");
    let isRegistering = $state(false);
    let registerError = $state<string | null>(null);

    // Formulario de Sincronización / Vinculación con InsWeb
    let inswebPin = $state("");
    let isSyncing = $state(false);
    let syncSuccess = $state(false);
    let syncError = $state<string | null>(null);
    let syncDetails = $state<LinkInswebResult | null>(null);

    const carrerasDisponibles = [
        "Ingeniería Electromecánica",
        "Ingeniería Civil",
        "Ingeniería Industrial",
        "Ingeniería Electrónica",
        "Ingeniería Mecatrónica",
        "Ingeniería Geográfica y Ambiental"
    ];

    async function handleLoginSubmit(event: SubmitEvent): Promise<void> {
        event.preventDefault();
        if (isLoggingIn) return;

        loginError = null;
        if (!loginIdentifier.trim() || !loginPassword) {
            loginError = "Por favor ingresa tu identificador (usuario o cédula) y contraseña.";
            return;
        }

        isLoggingIn = true;
        try {
            const res = await loginLocalUser({
                identificador: loginIdentifier.trim(),
                password: loginPassword
            });

            authState.login({
                id: res.id,
                usuario: res.usuario,
                cedula: res.cedula,
                nombre: res.nombre,
                carrera: res.carrera,
                isSynced: res.is_synced,
                lastSync: res.last_sync ? new Date(res.last_sync).toLocaleString() : null
            });

            loginPassword = "";
            if (res.is_synced) {
                setTimeout(() => {
                    academicState.activeNav = "dashboard";
                    goto("/dashboard");
                }, 600);
            }
        } catch (err: unknown) {
            loginError = err instanceof Error ? err.message : "Error al iniciar sesión local.";
        } finally {
            isLoggingIn = false;
        }
    }

    async function handleRegisterSubmit(event: SubmitEvent): Promise<void> {
        event.preventDefault();
        if (isRegistering) return;

        registerError = null;

        const cleanCedula = regCedula.replace(/[^0-9]/g, "");
        if (!regNombre.trim() || !regUsuario.trim() || !cleanCedula || !regPassword) {
            registerError = "Todos los campos marcados son obligatorios.";
            return;
        }

        if (regPassword.length < 4) {
            registerError = "La contraseña debe contener al menos 4 caracteres.";
            return;
        }

        if (regPassword !== regConfirmPassword) {
            registerError = "Las contraseñas no coinciden.";
            return;
        }

        isRegistering = true;
        try {
            const res = await registerLocalUser({
                nombre: regNombre.trim(),
                usuario: regUsuario.trim(),
                cedula: cleanCedula,
                password: regPassword,
                carrera: regCarrera
            });

            authState.login({
                id: res.id,
                usuario: res.usuario,
                cedula: res.cedula,
                nombre: res.nombre,
                carrera: res.carrera,
                isSynced: res.is_synced,
                lastSync: null
            });

            regPassword = "";
            regConfirmPassword = "";
        } catch (err: unknown) {
            registerError = err instanceof Error ? err.message : "Error al registrar la cuenta local.";
        } finally {
            isRegistering = false;
        }
    }

    async function handleLinkInsweb(event: SubmitEvent): Promise<void> {
        event.preventDefault();
        if (isSyncing || !authState.user) return;

        syncError = null;
        syncSuccess = false;
        syncDetails = null;

        if (!inswebPin) {
            syncError = "Por favor ingresa la clave / PIN del portal InsWeb.";
            return;
        }

        isSyncing = true;
        academicState.isRescraping = true;
        academicState.pipelineStatus = "Iniciando scraper silencioso...";

        try {
            const res = await linkInswebAccount(authState.user.cedula, inswebPin);
            syncDetails = res;
            syncSuccess = true;

            const nowStr = new Date().toLocaleString();
            authState.setSynced(true, nowStr);
            academicState.pipelineStatus = "Sincronización Completada";

            inswebPin = "";
        } catch (err: unknown) {
            syncError = err instanceof Error ? err.message : "Error al vincular con InsWeb.";
            academicState.pipelineStatus = "Error en extracción";
        } finally {
            isSyncing = false;
            academicState.isRescraping = false;
        }
    }

    function handleEnterGuestMode(): void {
        academicState.activeNav = "dashboard";
        goto("/dashboard");
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
                    <span class="material-symbols-outlined text-sm">terminal</span>
                </span>
                <span
                    class="font-label-sm text-label-sm uppercase tracking-wider text-secondary font-semibold"
                >
                    Submódulo de Autenticación &amp; Extracción Segura
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
                Gestión de cuentas locales encriptadas e ingesta automatizada sin interfaz gráfica
                con los servidores centrales de la UNA (<code
                    class="font-code-num text-code-num text-on-surface bg-surface-container-high px-1 py-0.5 rounded"
                    >insweb.ing.una.py</code
                >).
            </p>
        </div>

        <div
            class="flex items-center gap-space-sm bg-surface-container-lowest p-space-sm rounded-xl shadow-sm self-start md:self-auto border border-outline-variant/30"
        >
            <div class="w-3 h-3 rounded-full bg-emerald-500 animate-pulse"></div>
            <div class="flex flex-col">
                <span class="font-label-sm text-label-sm text-on-surface-variant"
                    >Base de Datos SQLite</span
                >
                <span class="font-code-num text-code-num font-semibold text-on-surface">
                    copilot.db / PBKDF2-HMAC
                </span>
            </div>
        </div>
    </div>

    <!-- Grilla Principal -->
    <div class="grid grid-cols-1 lg:grid-cols-12 gap-space-lg items-start">
        <!-- Columna Izquierda: Formulario de Autenticación / Vinculación -->
        <div class="lg:col-span-6 flex flex-col gap-space-lg">
            <div
                class="bg-surface-container-lowest rounded-xl shadow-sm p-4 sm:p-space-md lg:p-space-xl flex flex-col gap-space-lg relative overflow-hidden border border-outline-variant/30"
            >
                <div
                    class="absolute -top-12 -right-12 w-48 h-48 bg-primary/5 rounded-full blur-2xl pointer-events-none"
                ></div>

                {#if !user}
                    <!-- ========================================== -->
                    <!-- VISTA NO AUTENTICADO: TABS LOGIN / REGISTRO -->
                    <!-- ========================================== -->
                    <div class="flex flex-col gap-space-md">
                        <div class="flex items-center justify-between pb-space-xs">
                            <div class="flex items-center gap-space-sm">
                                <span class="material-symbols-outlined text-primary text-2xl"
                                    >lock_person</span
                                >
                                <div>
                                    <h2 class="font-headline-sm text-headline-sm text-on-surface font-bold">
                                        Acceso Local FIUNA
                                    </h2>
                                    <span class="font-body-sm text-body-sm text-on-surface-variant">
                                        Base de datos local independiente
                                    </span>
                                </div>
                            </div>
                            <span class="px-space-sm py-1 bg-surface-container text-on-surface-variant rounded font-label-sm text-label-sm font-semibold uppercase">
                                Paso 1: Autenticación
                            </span>
                        </div>

                        <!-- Selector de Pestañas -->
                        <div class="grid grid-cols-2 p-1 bg-surface-container-low rounded-xl">
                            <button
                                type="button"
                                class="py-2 text-center font-label-md text-label-md font-semibold rounded-lg transition-all {activeAuthTab === 'login'
                                    ? 'bg-surface-container-lowest text-primary shadow-sm'
                                    : 'text-on-surface-variant hover:text-on-surface'}"
                                onclick={() => {
                                    activeAuthTab = "login";
                                    loginError = null;
                                }}
                            >
                                Iniciar Sesión
                            </button>
                            <button
                                type="button"
                                class="py-2 text-center font-label-md text-label-md font-semibold rounded-lg transition-all {activeAuthTab === 'register'
                                    ? 'bg-surface-container-lowest text-primary shadow-sm'
                                    : 'text-on-surface-variant hover:text-on-surface'}"
                                onclick={() => {
                                    activeAuthTab = "register";
                                    registerError = null;
                                }}
                            >
                                Crear Cuenta
                            </button>
                        </div>

                        {#if activeAuthTab === "login"}
                            <!-- Formulario de Iniciar Sesión -->
                            <form
                                class="flex flex-col gap-space-md pt-space-xs"
                                onsubmit={handleLoginSubmit}
                            >
                                <div class="flex flex-col gap-space-xs">
                                    <label
                                        class="font-label-sm text-label-sm text-on-surface font-semibold"
                                        for="login-identifier"
                                    >
                                        Usuario o Cédula de Identidad
                                    </label>
                                    <div class="relative flex items-center">
                                        <span class="material-symbols-outlined absolute left-3 text-outline text-lg pointer-events-none">
                                            person
                                        </span>
                                        <input
                                            class="w-full bg-surface-container-low text-on-surface font-body-md text-body-md pl-10 pr-3 py-2.5 rounded-lg border border-transparent focus:border-primary/40 focus:bg-surface-container-lowest focus:shadow-sm transition-all"
                                            id="login-identifier"
                                            placeholder="ej. 4580214 o j.perez"
                                            required
                                            type="text"
                                            bind:value={loginIdentifier}
                                        />
                                    </div>
                                </div>

                                <div class="flex flex-col gap-space-xs">
                                    <label
                                        class="font-label-sm text-label-sm text-on-surface font-semibold"
                                        for="login-password"
                                    >
                                        Contraseña Local
                                    </label>
                                    <div class="relative flex items-center">
                                        <span class="material-symbols-outlined absolute left-3 text-outline text-lg pointer-events-none">
                                            key
                                        </span>
                                        <input
                                            class="w-full bg-surface-container-low text-on-surface font-body-md text-body-md pl-10 pr-3 py-2.5 rounded-lg border border-transparent focus:border-primary/40 focus:bg-surface-container-lowest focus:shadow-sm transition-all"
                                            id="login-password"
                                            placeholder="Tu contraseña personal"
                                            required
                                            type="password"
                                            bind:value={loginPassword}
                                        />
                                    </div>
                                </div>

                                {#if loginError}
                                    <div class="p-space-sm rounded-lg bg-error/10 border border-error/30 text-error font-body-sm text-body-sm flex items-start gap-space-xs">
                                        <span class="material-symbols-outlined text-base mt-0.5">error</span>
                                        <span class="flex-1">{loginError}</span>
                                    </div>
                                {/if}

                                <button
                                    class="w-full py-3 px-space-md bg-primary hover:bg-primary-container text-on-primary rounded-lg font-label-md text-label-md uppercase tracking-wider flex items-center justify-center gap-space-sm transition-all shadow-md active:scale-[0.99] mt-space-xs"
                                    disabled={isLoggingIn}
                                    type="submit"
                                >
                                    {#if isLoggingIn}
                                        <span class="material-symbols-outlined text-lg animate-spin">autorenew</span>
                                        <span>Autenticando...</span>
                                    {:else}
                                        <span class="material-symbols-outlined text-lg">login</span>
                                        <span>Iniciar Sesión Local</span>
                                    {/if}
                                </button>
                            </form>
                        {:else}
                            <!-- Formulario de Crear Cuenta -->
                            <form
                                class="flex flex-col gap-space-md pt-space-xs"
                                onsubmit={handleRegisterSubmit}
                            >
                                <div class="grid grid-cols-1 md:grid-cols-2 gap-space-md">
                                    <div class="flex flex-col gap-space-xs">
                                        <label
                                            class="font-label-sm text-label-sm text-on-surface font-semibold"
                                            for="reg-nombre"
                                        >
                                            Nombre Completo
                                        </label>
                                        <input
                                            class="w-full bg-surface-container-low text-on-surface font-body-md text-body-md px-3 py-2.5 rounded-lg border border-transparent focus:border-primary/40 focus:bg-surface-container-lowest focus:shadow-sm transition-all"
                                            id="reg-nombre"
                                            placeholder="ej. Alejandro Benítez"
                                            required
                                            type="text"
                                            bind:value={regNombre}
                                        />
                                    </div>

                                    <div class="flex flex-col gap-space-xs">
                                        <label
                                            class="font-label-sm text-label-sm text-on-surface font-semibold"
                                            for="reg-usuario"
                                        >
                                            Nombre de Usuario
                                        </label>
                                        <input
                                            class="w-full bg-surface-container-low text-on-surface font-body-md text-body-md px-3 py-2.5 rounded-lg border border-transparent focus:border-primary/40 focus:bg-surface-container-lowest focus:shadow-sm transition-all"
                                            id="reg-usuario"
                                            placeholder="ej. abenitez"
                                            required
                                            type="text"
                                            bind:value={regUsuario}
                                        />
                                    </div>
                                </div>

                                <div class="grid grid-cols-1 md:grid-cols-2 gap-space-md">
                                    <div class="flex flex-col gap-space-xs">
                                        <label
                                            class="font-label-sm text-label-sm text-on-surface font-semibold"
                                            for="reg-cedula"
                                        >
                                            Cédula de Identidad (Sin puntos)
                                        </label>
                                        <div class="relative flex items-center">
                                            <span class="material-symbols-outlined absolute left-3 text-outline text-lg pointer-events-none">
                                                badge
                                            </span>
                                            <input
                                                class="w-full bg-surface-container-low text-on-surface font-code-num text-code-num pl-10 pr-3 py-2.5 rounded-lg border border-transparent focus:border-primary/40 focus:bg-surface-container-lowest focus:shadow-sm transition-all"
                                                id="reg-cedula"
                                                placeholder="ej. 4580214"
                                                required
                                                type="text"
                                                bind:value={regCedula}
                                            />
                                        </div>
                                    </div>

                                    <div class="flex flex-col gap-space-xs">
                                        <label
                                            class="font-label-sm text-label-sm text-on-surface font-semibold"
                                            for="reg-carrera"
                                        >
                                            Carrera
                                        </label>
                                        <select
                                            class="w-full bg-surface-container-low text-on-surface font-body-md text-body-md px-3 py-2.5 rounded-lg border border-transparent focus:border-primary/40 focus:bg-surface-container-lowest focus:shadow-sm transition-all cursor-pointer"
                                            id="reg-carrera"
                                            bind:value={regCarrera}
                                        >
                                            {#each carrerasDisponibles as car}
                                                <option value={car}>{car}</option>
                                            {/each}
                                        </select>
                                    </div>
                                </div>

                                <div class="grid grid-cols-1 md:grid-cols-2 gap-space-md">
                                    <div class="flex flex-col gap-space-xs">
                                        <label
                                            class="font-label-sm text-label-sm text-on-surface font-semibold"
                                            for="reg-password"
                                        >
                                            Contraseña
                                        </label>
                                        <input
                                            class="w-full bg-surface-container-low text-on-surface font-body-md text-body-md px-3 py-2.5 rounded-lg border border-transparent focus:border-primary/40 focus:bg-surface-container-lowest focus:shadow-sm transition-all"
                                            id="reg-password"
                                            placeholder="Mínimo 4 caracteres"
                                            required
                                            type="password"
                                            bind:value={regPassword}
                                        />
                                    </div>

                                    <div class="flex flex-col gap-space-xs">
                                        <label
                                            class="font-label-sm text-label-sm text-on-surface font-semibold"
                                            for="reg-confirm"
                                        >
                                            Confirmar Contraseña
                                        </label>
                                        <input
                                            class="w-full bg-surface-container-low text-on-surface font-body-md text-body-md px-3 py-2.5 rounded-lg border border-transparent focus:border-primary/40 focus:bg-surface-container-lowest focus:shadow-sm transition-all"
                                            id="reg-confirm"
                                            placeholder="Repite la contraseña"
                                            required
                                            type="password"
                                            bind:value={regConfirmPassword}
                                        />
                                    </div>
                                </div>

                                {#if registerError}
                                    <div class="p-space-sm rounded-lg bg-error/10 border border-error/30 text-error font-body-sm text-body-sm flex items-start gap-space-xs">
                                        <span class="material-symbols-outlined text-base mt-0.5">error</span>
                                        <span class="flex-1">{registerError}</span>
                                    </div>
                                {/if}

                                <button
                                    class="w-full py-3 px-space-md bg-secondary hover:bg-secondary-container text-on-secondary hover:text-on-secondary-container rounded-lg font-label-md text-label-md uppercase tracking-wider flex items-center justify-center gap-space-sm transition-all shadow-md active:scale-[0.99] mt-space-xs"
                                    disabled={isRegistering}
                                    type="submit"
                                >
                                    {#if isRegistering}
                                        <span class="material-symbols-outlined text-lg animate-spin">autorenew</span>
                                        <span>Guardando Cuenta...</span>
                                    {:else}
                                        <span class="material-symbols-outlined text-lg">person_add</span>
                                        <span>Registrar Cuenta Local</span>
                                    {/if}
                                </button>
                            </form>
                        {/if}

                        <!-- Modo Invitado Directo -->
                        <div class="pt-space-sm border-t border-outline-variant/30 flex items-center justify-between">
                            <span class="font-body-sm text-body-sm text-on-surface-variant">
                                ¿Deseas explorar sin credenciales?
                            </span>
                            <button
                                type="button"
                                class="font-label-sm text-label-sm text-primary hover:underline flex items-center gap-1 font-semibold"
                                onclick={handleEnterGuestMode}
                            >
                                Entrar como Invitado
                                <span class="material-symbols-outlined text-sm">arrow_forward</span>
                            </button>
                        </div>
                    </div>
                {:else}
                    <!-- ========================================== -->
                    <!-- VISTA AUTENTICADO: PERFIL + FORM VINCULAR  -->
                    <!-- ========================================== -->
                    <div class="flex flex-col gap-space-lg">
                        <!-- Tarjeta de Perfil Local Activo -->
                        <div class="p-space-lg rounded-xl bg-surface-container-low border border-outline-variant/40 flex flex-col gap-space-md">
                            <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-space-sm">
                                <div class="flex items-center gap-space-sm">
                                    <div class="w-12 h-12 rounded-full bg-primary/10 text-primary flex items-center justify-center font-bold text-lg border border-primary/20">
                                        {user.nombre.slice(0, 2).toUpperCase()}
                                    </div>
                                    <div class="flex flex-col">
                                        <div class="flex items-center gap-2">
                                            <h3 class="font-headline-sm text-headline-sm text-on-surface font-bold">
                                                {user.nombre}
                                            </h3>
                                            {#if user.isSynced}
                                                <span class="px-2 py-0.5 rounded-full bg-emerald-500/15 text-emerald-700 dark:text-emerald-400 font-label-sm text-label-sm font-semibold flex items-center gap-1">
                                                    <span class="material-symbols-outlined text-xs">verified</span>
                                                    InsWeb Vinculado
                                                </span>
                                            {:else}
                                                <span class="px-2 py-0.5 rounded-full bg-amber-500/15 text-amber-700 dark:text-amber-400 font-label-sm text-label-sm font-semibold flex items-center gap-1">
                                                    <span class="material-symbols-outlined text-xs">pending</span>
                                                    Pendiente de Scraping
                                                </span>
                                            {/if}
                                        </div>
                                        <p class="font-body-sm text-body-sm text-on-surface-variant">
                                            C.I. {user.cedula} • {user.carrera}
                                            {#if user.usuario}
                                                • <code class="text-xs text-primary">@{user.usuario}</code>
                                            {/if}
                                        </p>
                                    </div>
                                </div>

                                <button
                                    type="button"
                                    class="py-1.5 px-space-sm border border-outline-variant text-on-surface-variant hover:text-on-surface hover:bg-surface-container rounded-lg font-label-sm text-label-sm flex items-center gap-1 self-start sm:self-auto transition-colors"
                                    onclick={() => authState.logout()}
                                >
                                    <span class="material-symbols-outlined text-base">logout</span>
                                    Cerrar Sesión
                                </button>
                            </div>

                            {#if user.lastSync}
                                <div class="flex items-center gap-2 text-on-surface-variant font-label-sm text-label-sm pt-space-xs border-t border-outline-variant/30">
                                    <span class="material-symbols-outlined text-xs text-emerald-600">sync_saved_locally</span>
                                    <span>Última sincronización con InsWeb: <strong class="text-on-surface">{user.lastSync}</strong></span>
                                </div>
                            {/if}

                            <div class="flex items-center gap-space-sm pt-space-xs">
                                <button
                                    type="button"
                                    class="flex-1 py-2.5 px-space-md bg-primary hover:bg-primary-container text-on-primary rounded-lg font-label-md text-label-md uppercase tracking-wider flex items-center justify-center gap-2 transition-all shadow-sm"
                                    onclick={() => {
                                        academicState.activeNav = "dashboard";
                                        goto("/dashboard");
                                    }}
                                >
                                    <span class="material-symbols-outlined text-lg">dashboard</span>
                                    Ir al Dashboard Académico
                                </button>
                            </div>
                        </div>

                        <!-- Formulario de Vinculación / Sincronización InsWeb -->
                        <div class="bg-surface-container-low rounded-xl p-space-lg flex flex-col gap-space-md relative overflow-hidden border border-outline-variant/30">
                            <div class="flex items-center justify-between">
                                <div class="flex items-center gap-space-xs text-primary">
                                    <span class="material-symbols-outlined text-xl">cloud_sync</span>
                                    <span class="font-label-md text-label-md font-bold tracking-tight">
                                        {user.isSynced ? "Re-sincronizar Calificaciones InsWeb" : "Paso 2: Vincular con Récord InsWeb"}
                                    </span>
                                </div>
                                <span class="material-symbols-outlined text-secondary text-base">security</span>
                            </div>

                            <p class="font-body-sm text-body-sm text-on-surface-variant">
                                El scraper silencioso (headless Chromium) extraerá tus materias cursadas, inscripciones actuales y calificaciones oficiales desde <code class="font-code-num text-xs bg-surface-container px-1 py-0.5 rounded">insweb.ing.una.py</code> y las almacenará en tu base de datos SQLite asociada a tu C.I. <strong>{user.cedula}</strong>.
                            </p>

                            <form class="flex flex-col gap-space-md" onsubmit={handleLinkInsweb}>
                                <div class="grid grid-cols-1 md:grid-cols-2 gap-space-md">
                                    <div class="flex flex-col gap-space-xs">
                                        <label class="font-label-sm text-label-sm text-on-surface font-medium" for="sync-cedula">
                                            Cédula Asociada (Bloqueada)
                                        </label>
                                        <div class="relative flex items-center">
                                            <span class="material-symbols-outlined absolute left-3 text-outline text-lg pointer-events-none">
                                                lock
                                            </span>
                                            <input
                                                class="w-full bg-surface-container-lowest text-on-surface-variant font-code-num text-code-num pl-10 pr-3 py-2.5 rounded-lg border border-outline-variant/50 cursor-not-allowed opacity-80"
                                                id="sync-cedula"
                                                type="text"
                                                disabled
                                                value={user.cedula}
                                            />
                                        </div>
                                    </div>

                                    <div class="flex flex-col gap-space-xs">
                                        <label class="font-label-sm text-label-sm text-on-surface font-medium" for="sync-pin">
                                            PIN / Clave de InsWeb
                                        </label>
                                        <div class="relative flex items-center">
                                            <span class="material-symbols-outlined absolute left-3 text-outline text-lg pointer-events-none">
                                                key
                                            </span>
                                            <input
                                                class="w-full bg-surface-container-lowest text-on-surface font-code-num text-code-num pl-10 pr-3 py-2.5 rounded-lg border border-transparent focus:border-primary/40 focus:shadow-sm transition-all"
                                                id="sync-pin"
                                                placeholder="Tu PIN secreto de InsWeb"
                                                required
                                                type="password"
                                                bind:value={inswebPin}
                                            />
                                        </div>
                                    </div>
                                </div>

                                <div class="bg-surface-container/70 rounded-lg p-space-sm flex items-start gap-space-sm">
                                    <span class="material-symbols-outlined text-secondary text-base mt-0.5">verified_user</span>
                                    <p class="font-body-sm text-body-sm text-on-surface-variant">
                                        Tu PIN de InsWeb nunca se almacena en la base de datos local ni en servidores externos; solo se utiliza durante el proceso de extracción en memoria.
                                    </p>
                                </div>

                                <button
                                    class="w-full py-3 px-space-md text-on-primary rounded-lg font-label-md text-label-md uppercase tracking-wider flex items-center justify-center gap-space-sm transition-all shadow-md active:scale-[0.99] {syncSuccess
                                        ? 'bg-emerald-600'
                                        : 'bg-primary hover:bg-primary-container'}"
                                    disabled={isSyncing}
                                    type="submit"
                                >
                                    {#if isSyncing}
                                        <span class="material-symbols-outlined text-lg animate-spin">autorenew</span>
                                        <span>Extrayendo con Headless Playwright...</span>
                                    {:else if syncSuccess}
                                        <span class="material-symbols-outlined text-lg">check_circle</span>
                                        <span>¡Récord Académico Vinculado con Éxito!</span>
                                    {:else}
                                        <span class="material-symbols-outlined text-lg">cloud_download</span>
                                        <span>{user.isSynced ? "Actualizar Récord Académico" : "Vincular y Extraer Datos de InsWeb"}</span>
                                    {/if}
                                </button>

                                {#if syncSuccess && syncDetails}
                                    <div class="p-space-md rounded-lg bg-emerald-500/10 border border-emerald-500/30 text-emerald-800 dark:text-emerald-300 font-body-sm text-body-sm flex flex-col gap-1">
                                        <div class="flex items-center gap-2 font-bold">
                                            <span class="material-symbols-outlined text-base">check_circle</span>
                                            <span>Sincronización Completada en SQLite</span>
                                        </div>
                                        <p class="text-xs pl-6">
                                            Se registraron <strong>{syncDetails.inscripciones_count}</strong> inscripciones vigentes, <strong>{syncDetails.parciales_count}</strong> parciales y <strong>{syncDetails.notas_count}</strong> actas de materias aprobadas/cursadas.
                                        </p>
                                    </div>
                                {/if}

                                {#if syncError}
                                    <div class="p-space-sm rounded-lg bg-error/10 border border-error/30 text-error font-body-sm text-body-sm flex items-start gap-space-xs">
                                        <span class="material-symbols-outlined text-base mt-0.5">error</span>
                                        <span class="flex-1">{syncError}</span>
                                    </div>
                                {/if}
                            </form>
                        </div>
                    </div>
                {/if}

                <div class="flex items-center justify-between pt-space-xs border-t border-outline-variant/30">
                    <a
                        class="font-label-sm text-label-sm text-secondary hover:text-on-surface flex items-center gap-1 transition-colors"
                        href="#ayuda"
                    >
                        <span class="material-symbols-outlined text-sm">help</span>
                        ¿Problemas con tu PIN de InsWeb?
                    </a>
                    <span class="font-label-sm text-label-sm text-outline">
                        FIUNA Auth Node #3 (San Lorenzo)
                    </span>
                </div>
            </div>

            <div
                class="bg-surface-container rounded-xl p-space-lg flex items-center gap-space-md shadow-sm border border-outline-variant/30"
            >
                <div class="h-16 w-16 rounded-xl overflow-hidden shrink-0 shadow-inner">
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
                        Desacoplamiento Modular
                    </span>
                    <span
                        class="font-headline-sm text-headline-sm text-on-surface leading-tight font-bold"
                    >
                        Arquitectura Preparada para API Central UNA
                    </span>
                    <p
                        class="font-body-sm text-body-sm text-on-surface-variant mt-0.5"
                    >
                        El sistema de autenticación local vincula las materias mediante la Cédula de Identidad. En el futuro, podrá conectarse de manera transparente al backend institucional de la universidad.
                    </p>
                </div>
            </div>
        </div>

        <!-- Columna Derecha: Monitor de Scraping en Vivo -->
        <div class="lg:col-span-6 flex flex-col gap-space-lg">
            <div
                class="bg-surface-container-lowest rounded-xl shadow-sm p-4 sm:p-space-md lg:p-space-xl flex flex-col gap-space-lg border border-outline-variant/30"
            >
                <div
                    class="flex flex-col sm:flex-row sm:items-center justify-between gap-space-sm pb-space-xs"
                >
                    <div class="flex items-center gap-space-sm">
                        <div class="w-2.5 h-2.5 rounded-full bg-secondary"></div>
                        <div>
                            <h2
                                class="font-headline-sm text-headline-sm text-on-surface font-bold"
                            >
                                Monitor de Scraping en Vivo
                            </h2>
                            <span
                                class="font-body-sm text-body-sm text-on-surface-variant"
                            >
                                Diagnóstico de Pipeline &amp; Telemetría Headless
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
                        <span>Verificar Latencia</span>
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
                            <span class="material-symbols-outlined text-xs">check_circle</span>
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
                                Silencioso
                            </span>
                        </div>
                        <span
                            class="font-label-sm text-label-sm text-secondary flex items-center gap-0.5"
                        >
                            <span class="material-symbols-outlined text-xs">bolt</span>
                            Headless Chromium
                        </span>
                    </div>

                    <div
                        class="col-span-2 md:col-span-1 bg-surface-container-low rounded-lg p-space-sm flex flex-col gap-0.5"
                    >
                        <span
                            class="font-label-sm text-label-sm uppercase text-outline"
                            >Persistencia</span
                        >
                        <div class="flex items-baseline gap-1">
                            <span
                                class="font-code-num text-headline-sm font-bold text-on-surface"
                                >SQLite</span
                            >
                        </div>
                        <span
                            class="font-label-sm text-label-sm text-on-surface-variant flex items-center gap-0.5"
                        >
                            <span class="material-symbols-outlined text-xs">storage</span>
                            copilot.db
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
                        <div class="flex items-start gap-space-md relative pl-1">
                            <span
                                class="z-10 flex h-5 w-5 rounded-full bg-emerald-500 text-on-error items-center justify-center shadow-sm"
                            >
                                <span class="material-symbols-outlined text-xs">done</span>
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
                                        Validación de sesión con C.I. y PIN
                                    </span>
                                </div>
                                <div class="flex items-center gap-space-xs">
                                    <span
                                        class="px-2 py-0.5 rounded font-label-sm text-label-sm bg-emerald-100 text-emerald-800 font-semibold uppercase"
                                    >
                                        Listo
                                    </span>
                                </div>
                            </div>
                        </div>

                        <div class="flex items-start gap-space-md relative pl-1">
                            <span
                                class="z-10 flex h-5 w-5 rounded-full bg-emerald-500 text-on-error items-center justify-center shadow-sm"
                            >
                                <span class="material-symbols-outlined text-xs">done</span>
                            </span>
                            <div
                                class="flex-1 bg-surface-container-low p-space-sm rounded-lg flex flex-col sm:flex-row sm:items-center justify-between gap-1 shadow-sm"
                            >
                                <div class="flex flex-col">
                                    <span
                                        class="font-body-md text-body-md font-semibold text-on-surface leading-snug"
                                    >
                                        Extracción de Ficha Alumno
                                    </span>
                                    <span
                                        class="font-label-sm text-label-sm text-on-surface-variant"
                                    >
                                        Parsing de Cédula y carrera universitaria
                                    </span>
                                </div>
                                <div class="flex items-center gap-space-xs">
                                    <span
                                        class="px-2 py-0.5 rounded font-label-sm text-label-sm bg-emerald-100 text-emerald-800 font-semibold uppercase"
                                    >
                                        Listo
                                    </span>
                                </div>
                            </div>
                        </div>

                        <div class="flex items-start gap-space-md relative pl-1">
                            <span
                                class="z-10 flex h-5 w-5 rounded-full bg-emerald-500 text-on-error items-center justify-center shadow-sm"
                            >
                                <span class="material-symbols-outlined text-xs">done</span>
                            </span>
                            <div
                                class="flex-1 bg-surface-container-low p-space-sm rounded-lg flex flex-col sm:flex-row sm:items-center justify-between gap-1 shadow-sm"
                            >
                                <div class="flex flex-col">
                                    <span
                                        class="font-body-md text-body-md font-semibold text-on-surface leading-snug"
                                    >
                                        Scraping de Calificaciones Históricas
                                    </span>
                                    <span
                                        class="font-label-sm text-label-sm text-on-surface-variant"
                                    >
                                        Actas de exámenes, ponderaciones y estado de aprobación
                                    </span>
                                </div>
                                <div class="flex items-center gap-space-xs">
                                    <span
                                        class="px-2 py-0.5 rounded font-label-sm text-label-sm bg-emerald-100 text-emerald-800 font-semibold uppercase"
                                    >
                                        Listo
                                    </span>
                                </div>
                            </div>
                        </div>

                        <div class="flex items-start gap-space-md relative pl-1">
                            <span
                                class="z-10 flex h-5 w-5 rounded-full bg-secondary text-on-primary items-center justify-center shadow-sm"
                            >
                                <span class="material-symbols-outlined text-xs">database</span>
                            </span>
                            <div
                                class="flex-1 bg-surface-container-low p-space-sm rounded-lg flex flex-col sm:flex-row sm:items-center justify-between gap-1 shadow-sm"
                            >
                                <div class="flex flex-col">
                                    <span
                                        class="font-body-md text-body-md font-semibold text-on-surface leading-snug"
                                    >
                                        Persistencia Relacional SQLite
                                    </span>
                                    <span
                                        class="font-label-sm text-label-sm text-on-surface-variant"
                                    >
                                        Enlace de tablas por clave foránea <code>cedula</code>
                                    </span>
                                </div>
                                <div class="flex items-center gap-space-xs">
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
                            Seguridad &amp; Privacidad Local
                        </span>
                        <span
                            class="font-code-num text-code-num text-emerald-700 font-semibold"
                        >
                            100% Sin Ventana Headful
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
                        <span>Cifrado PBKDF2</span>
                        <span>Ejecución en segundo plano</span>
                    </div>
                </div>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-2 gap-space-md">
                <div
                    class="bg-surface-container-lowest p-space-md rounded-xl shadow-sm flex items-center gap-space-md border border-outline-variant/30"
                >
                    <div
                        class="h-12 w-12 rounded-lg bg-surface-container-low flex items-center justify-center text-primary shrink-0"
                    >
                        <span class="material-symbols-outlined text-2xl">dns</span>
                    </div>
                    <div class="flex flex-col min-w-0">
                        <span class="font-label-sm text-label-sm text-on-surface-variant">
                            Servidor Principal
                        </span>
                        <span class="font-body-md text-body-md font-semibold text-on-surface truncate">
                            insweb.ing.una.py:443
                        </span>
                        <span class="font-code-num text-code-num text-emerald-700">
                            Online / Silencioso
                        </span>
                    </div>
                </div>

                <div
                    class="bg-surface-container-lowest p-space-md rounded-xl shadow-sm flex items-center gap-space-md border border-outline-variant/30"
                >
                    <div
                        class="h-12 w-12 rounded-lg bg-surface-container-low flex items-center justify-center text-primary shrink-0"
                    >
                        <span class="material-symbols-outlined text-2xl">security_update_good</span>
                    </div>
                    <div class="flex flex-col min-w-0">
                        <span class="font-label-sm text-label-sm text-on-surface-variant">
                            API Backend
                        </span>
                        <span class="font-body-md text-body-md font-semibold text-on-surface truncate">
                            FastAPI /api/auth
                        </span>
                        <span class="font-code-num text-code-num text-secondary">
                            SQLite Vinculado
                        </span>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- Barra Inferior de Acción -->
    <div
        class="mt-space-xl p-space-lg bg-surface-container-low rounded-xl flex flex-col md:flex-row items-center justify-between gap-space-md border border-outline-variant/30"
    >
        <div class="flex items-center gap-space-md">
            <div
                class="w-10 h-10 rounded-full bg-primary flex items-center justify-center text-on-primary shrink-0"
            >
                <span class="material-symbols-outlined">auto_graph</span>
            </div>
            <div class="flex flex-col">
                <span class="font-label-md text-label-md font-bold text-on-surface">
                    Dashboard Académico &amp; Simulador Predictivo FIUNA
                </span>
                <span class="font-body-sm text-body-sm text-on-surface-variant">
                    Explora tus probabilidades de firma de actas, cálculo de ponderaciones y asistencia.
                </span>
            </div>
        </div>
        <div class="flex items-center gap-space-sm w-full md:w-auto">
            <button
                type="button"
                class="w-full md:w-auto px-space-lg py-2.5 bg-primary text-on-primary rounded font-label-md text-label-md uppercase tracking-wider font-semibold text-center hover:bg-primary-container transition-all shadow-sm inline-block"
                onclick={() => {
                    academicState.activeNav = "dashboard";
                    goto("/dashboard");
                }}
            >
                Acceder al Dashboard
            </button>
        </div>
    </div>
</div>
