<script lang="ts">
	import { tick } from 'svelte';
	import type { ChatMessage, SubjectSimulation } from '../../types/simulator';
	import type { GeminiChatMessage } from '../../services/types';
	import { chat as geminiChat } from '../../services/gemini';
	import { initialChatMessages } from '../../data/simulator-mock';

	export interface Props {
		subject: SubjectSimulation;
		quickPrompts: string[];
		onSetP2: (p2: number) => void;
		onSwitchSubject?: (subjectId: string) => void;
	}

	let { subject, quickPrompts, onSetP2, onSwitchSubject }: Props = $props();

	let messages = $state<ChatMessage[]>([...initialChatMessages]);
	let inputText = $state('');
	let isTyping = $state(false);
	let chatContainer = $state<HTMLDivElement | null>(null);
	let errorMessage = $state('');
	let currentSessionId = $state<string | null>(null);

	/** Historial de conversación en memoria de la UI */
	let geminiHistory = $state<GeminiChatMessage[]>([]);

	async function scrollToBottom() {
		await tick();
		if (chatContainer) {
			chatContainer.scrollTop = chatContainer.scrollHeight;
		}
	}

	function resetChat() {
		messages = [...initialChatMessages];
		geminiHistory = [];
		currentSessionId = null;
		errorMessage = '';
		scrollToBottom();
	}

	function handleQuickPrompt(promptText: string) {
		inputText = promptText;
		sendMessage();
	}

	async function sendMessage() {
		const text = inputText.trim();
		if (!text || isTyping) return;

		// 1. Añadir mensaje del usuario a la UI
		const userMsg: ChatMessage = {
			id: `user-${Date.now()}`,
			sender: 'user',
			text,
			timestamp: `Ahora • Alejandro Benítez`
		};

		messages = [...messages, userMsg];
		inputText = '';
		errorMessage = '';
		scrollToBottom();

		// 2. Construir contexto para el Agente
		const contextPrefix = `[Contexto actual del simulador — Materia: ${subject.name} (${subject.catedra}), ` +
			`Prof: ${subject.professor}, P1: ${subject.p1}/${subject.p1Max}, Lab: ${subject.lab}/${subject.labMax}, ` +
			`Asistencia: ${subject.attendanceRate}%, Tema crítico: ${subject.criticalTopic}]\n\n`;

		// Solo inyectar contexto institucional en el primer mensaje de la sesión
		const userContent = geminiHistory.length === 0
			? contextPrefix + text
			: text;

		geminiHistory = [...geminiHistory, { role: 'user', content: userContent }];

		// 3. Llamar al Agente FastAPI con memoria en SQLite
		isTyping = true;

		try {
			const result = await geminiChat(userContent, currentSessionId);
			currentSessionId = result.sessionId;
			const responseText = result.reply;

			// Guardar respuesta en historial de la UI
			geminiHistory = [...geminiHistory, { role: 'model', content: responseText }];

			// Crear mensaje de UI del asistente
			const aiMsg: ChatMessage = {
				id: `ai-${Date.now()}`,
				sender: 'assistant',
				text: responseText,
				timestamp: 'Ahora • Copiloto FIUNA (FastAPI + SQLite)'
			};

			messages = [...messages, aiMsg];
		} catch (err) {
			const errText = err instanceof Error ? err.message : 'Error desconocido';
			errorMessage = errText;

			// Eliminar el último mensaje si falló
			geminiHistory = geminiHistory.slice(0, -1);

			const errorMsg: ChatMessage = {
				id: `error-${Date.now()}`,
				sender: 'assistant',
				text: `⚠️ No pude conectar con el Agente FastAPI. Detalle: ${errText}`,
				timestamp: 'Ahora • Sistema'
			};

			messages = [...messages, errorMsg];
		} finally {
			isTyping = false;
			scrollToBottom();
		}
	}
</script>

<div
	class="col-span-12 xl:col-span-5 flex flex-col bg-surface-container-lowest rounded-xl shadow-md overflow-hidden xl:sticky xl:top-20"
>
	<!-- Copilot Header -->
	<div class="p-space-md bg-primary text-on-primary flex items-center justify-between">
		<div class="flex items-center gap-space-sm">
			<div class="relative">
				<div
					class="w-10 h-10 rounded-lg bg-primary-container text-secondary-fixed dark:text-[#b1c7f0] flex items-center justify-center font-bold"
				>
					<span class="material-symbols-outlined text-2xl">psychology</span>
				</div>
				<span
					class="absolute -bottom-0.5 -right-0.5 w-3 h-3 bg-emerald-400 rounded-full ring-2 ring-primary"
				></span>
			</div>
			<div class="flex flex-col">
				<div class="flex items-center gap-1.5">
					<span class="font-headline-sm text-headline-sm text-on-primary leading-tight font-bold">
						Copiloto Académico
					</span>
					<span
						class="px-1.5 py-0.5 rounded text-[10px] font-bold bg-secondary text-on-secondary uppercase"
					>
						FastAPI + Gemini
					</span>
				</div>
				<span class="font-label-sm text-label-sm text-secondary-fixed opacity-90">
					Asistencia Académica con IA Generativa
				</span>
			</div>
		</div>

		<div class="flex items-center gap-1 text-on-primary">
			<button
				type="button"
				class="p-1 rounded hover:bg-white/10 text-on-primary transition-colors cursor-pointer"
				title="Reiniciar Sesión"
				onclick={resetChat}
			>
				<span class="material-symbols-outlined text-lg">restart_alt</span>
			</button>
			<button
				type="button"
				class="p-1 rounded hover:bg-white/10 text-on-primary transition-colors cursor-pointer"
				title="Parámetros del Agente"
			>
				<span class="material-symbols-outlined text-lg">more_vert</span>
			</button>
		</div>
	</div>

	<!-- Chat Stream Container -->
	<div
		bind:this={chatContainer}
		class="p-space-md flex flex-col gap-space-md overflow-y-auto max-h-[580px] min-h-[420px] bg-background"
	>
		<!-- Timestamp divider -->
		<div class="flex items-center justify-center my-1">
			<span
				class="font-label-sm text-label-sm text-outline bg-surface-container-high px-3 py-0.5 rounded-full font-code-num"
			>
				Hoy • Chat con Gemini AI
			</span>
		</div>

		<!-- Messages loop -->
		{#each messages as msg (msg.id)}
			{#if msg.sender === 'assistant'}
				<div class="flex items-start gap-space-sm">
					<div
						class="w-8 h-8 rounded-md bg-secondary text-on-secondary flex items-center justify-center shrink-0 mt-0.5 shadow-xs"
					>
						<span class="material-symbols-outlined text-base">smart_toy</span>
					</div>

					<div class="flex flex-col gap-1 max-w-[85%]">
						<div
							class="bg-surface-container-lowest p-space-md rounded-xl rounded-tl-none shadow-sm text-on-surface text-body-md leading-relaxed font-body-md"
						>
							<p class="whitespace-pre-line">{msg.text}</p>

							{#if msg.alertBox}
								<div
									class="p-2.5 my-2 rounded bg-amber-50 text-amber-950 dark:bg-amber-950/80 dark:text-amber-200 border border-amber-300 dark:border-amber-700/50 font-body-sm text-body-sm flex items-start gap-2"
								>
									<span class="material-symbols-outlined text-amber-800 dark:text-amber-300 text-lg shrink-0">
										priority_high
									</span>
									<span>{msg.alertBox.text}</span>
								</div>
							{/if}

							{#if msg.actionButton}
								<div
									class="mt-3 pt-2.5 bg-surface-container-low p-2 rounded flex flex-wrap items-center justify-between gap-2 text-body-sm font-body-sm"
								>
									<span class="text-on-surface-variant">¿Deseas probar en el simulador?</span>
									<button
										type="button"
										class="px-2.5 py-1 bg-primary text-on-primary hover:bg-primary-container font-label-sm text-label-sm font-semibold rounded shadow-sm transition-colors cursor-pointer"
										onclick={() => msg.actionButton && onSetP2(msg.actionButton.targetP2)}
									>
										{msg.actionButton.label}
									</button>
								</div>
							{/if}

							{#if msg.recommendationCard}
								<div
									class="mt-2.5 bg-surface-container-high/60 p-space-sm rounded-lg flex flex-col gap-1 border border-outline-variant/30"
								>
									<div class="flex items-center gap-1.5 text-secondary">
										<span class="material-symbols-outlined text-base">lightbulb</span>
										<span class="font-label-sm text-label-sm font-bold uppercase tracking-wider">
											{msg.recommendationCard.title}
										</span>
									</div>
									<p class="font-body-sm text-body-sm text-on-surface">
										{msg.recommendationCard.text}
									</p>
								</div>
							{/if}
						</div>
						<span class="font-code-num text-[11px] text-outline pl-1">{msg.timestamp}</span>
					</div>
				</div>
			{:else}
				<div class="flex items-start justify-end gap-space-sm">
					<div class="flex flex-col items-end gap-1 max-w-[85%]">
						<div
							class="bg-primary text-on-primary p-space-md rounded-xl rounded-tr-none shadow-sm font-body-md text-body-md leading-relaxed"
						>
							{msg.text}
						</div>
						<span class="font-code-num text-[11px] text-outline pr-1">{msg.timestamp}</span>
					</div>
					<img
						alt="Alejandro Benítez"
						class="w-8 h-8 rounded-full object-cover shrink-0 mt-0.5 ring-1 ring-surface-container-high"
						src="https://lh3.googleusercontent.com/aida-public/AB6AXuB8kJ8FISwkV6OknOgU0T7j3qRhwrIH2U1kypIEEFDa--01sG9zkVj7oWJ_5WG452Ig4i94JueK2YPEYHgLASnwTCcUJYc7MSbtBjI4ymazMa1wiMt_seGP6F1dWEs56_3IcHZ0-sF40L3lkzpQwgLkNB6MqFJ79KcVHgdN040oqJg0pbttWoL0sRVJ6qfIbtqpuA0_iIVKCGY1bX5GffM55HRS_PnCZWF9VvY8Adwi10slrChZ_3cA"
					/>
				</div>
			{/if}
		{/each}

		{#if isTyping}
			<div class="flex items-start gap-space-sm">
				<div
					class="w-8 h-8 rounded-md bg-secondary text-on-secondary flex items-center justify-center shrink-0 mt-0.5 shadow-xs"
				>
					<span class="material-symbols-outlined text-base animate-pulse">smart_toy</span>
				</div>
				<div class="flex flex-col gap-1">
					<div
						class="bg-surface-container-lowest p-space-md rounded-xl rounded-tl-none shadow-sm text-on-surface-variant text-body-md font-body-md"
					>
						<div class="flex items-center gap-2">
							<span class="material-symbols-outlined animate-spin text-base text-secondary">sync</span>
							<span>Copiloto analizando tu consulta...</span>
						</div>
						<div class="flex gap-1 mt-2">
							<span class="w-2 h-2 bg-secondary rounded-full animate-bounce" style="animation-delay: 0ms"></span>
							<span class="w-2 h-2 bg-secondary rounded-full animate-bounce" style="animation-delay: 150ms"></span>
							<span class="w-2 h-2 bg-secondary rounded-full animate-bounce" style="animation-delay: 300ms"></span>
						</div>
					</div>
				</div>
			</div>
		{/if}

		{#if errorMessage}
			<div class="flex items-center justify-center my-1">
				<span
					class="font-label-sm text-label-sm text-error bg-error-container px-3 py-1 rounded-full"
				>
					Error de conexión con el modelo
				</span>
			</div>
		{/if}
	</div>

	<!-- Quick Action Prompt Chips -->
	<div class="px-space-md py-space-sm bg-surface-container-low flex flex-wrap gap-1.5">
		{#each quickPrompts as promptText}
			<button
				type="button"
				class="px-3 py-1.5 bg-surface-container-lowest hover:bg-surface-container text-primary font-label-sm text-label-sm font-medium rounded-full shadow-2xs transition-all text-left flex items-center gap-1.5 cursor-pointer border border-outline-variant/20 disabled:opacity-50 disabled:cursor-not-allowed"
				onclick={() => handleQuickPrompt(promptText)}
				disabled={isTyping}
			>
				<span class="material-symbols-outlined text-sm text-secondary">
					{promptText.includes('plan')
						? 'calendar_add_on'
						: promptText.includes('ejercicios')
							? 'quiz'
							: 'swap_horiz'}
				</span>
				{promptText}
			</button>
		{/each}
	</div>

	<!-- Interactive Input Area -->
	<div class="p-space-md bg-surface-container-lowest flex flex-col gap-space-xs">
		<form
			class="flex items-center gap-space-xs relative"
			onsubmit={(e) => {
				e.preventDefault();
				sendMessage();
			}}
		>
			<input
				type="text"
				class="w-full bg-surface-container-low text-on-surface font-body-md text-body-md py-2.5 pl-3.5 pr-24 rounded-lg focus:outline-none focus:ring-2 focus:ring-secondary placeholder:text-outline shadow-sm border border-outline-variant/30"
				placeholder="Haz una consulta académica al Copiloto IA..."
				bind:value={inputText}
				disabled={isTyping}
			/>
			<div class="absolute right-1.5 flex items-center gap-1">
				<button
					type="submit"
					class="p-2 bg-primary text-on-primary hover:bg-primary-container rounded transition-colors flex items-center justify-center shadow-xs cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
					title="Enviar mensaje"
					disabled={isTyping || !inputText.trim()}
				>
					<span class="material-symbols-outlined text-base">send</span>
				</button>
			</div>
		</form>

		<div class="flex items-center justify-between px-1">
			<span class="font-label-sm text-[10px] text-outline">
				Impulsado por Gemini — Solo texto. Las respuestas son orientativas.
			</span>
			<span class="font-code-num text-[10px] text-secondary font-semibold flex items-center gap-0.5">
				<span class="inline-block w-1.5 h-1.5 rounded-full bg-emerald-500"></span>
				Online
			</span>
		</div>
	</div>
</div>
