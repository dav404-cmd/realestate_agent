<script>
	import { onMount, tick } from 'svelte';
	import { auth } from '$lib/stores/auth.js';
	import { threads } from '$lib/stores/threads.js';
	import ThreadSidebar from '$lib/components/ThreadSidebar.svelte';
	import ChatComposer from '$lib/components/ChatComposer.svelte';
	import EmptyState from '$lib/components/EmptyState.svelte';
	import { marked } from 'marked';
    import DOMPurify from 'dompurify';

	let scrollEl;

	async function scrollToBottom() {
		await tick();
		if (scrollEl) scrollEl.scrollTop = scrollEl.scrollHeight;
	}

	function handleNew() {
		threads.startNewThread();
	}

	function handleSelect(e) {
		threads.selectThread(e.detail).then(scrollToBottom);
	}

	async function handleSend(e) {
		await threads.send(e.detail, $auth.userId);
		scrollToBottom();
	}

	onMount(() => {
		if ($auth.status === 'authenticated') {
			threads.loadThreads($auth.userId);
		}
	});

	$: if ($auth.status === 'authenticated' && $threads.threadsStatus === 'idle') {
		threads.loadThreads($auth.userId);
	}
</script>

<svelte:head>
	<title>Agent — Tsubonote</title>
</svelte:head>

{#if $auth.status !== 'authenticated'}
	<div class="container page">
		<EmptyState title="Sign in to use the agent" message="The AI agent is available to signed-in users." />
	</div>
{:else}
	<div class="container page layout">
		<ThreadSidebar
			threads={$threads.threads}
			activeThreadId={$threads.activeThreadId}
			status={$threads.threadsStatus}
			on:new={handleNew}
			on:select={handleSelect}
		/>

		<div class="chat">
			<div class="messages" bind:this={scrollEl}>
				{#if $threads.messagesStatus === 'loading'}
					<p class="hint">Loading messages…</p>
				{:else if $threads.messages.length === 0}
					<div class="welcome">
						<h2>What are you looking for?</h2>
						<p>Ask about neighborhoods, price ranges, or specific listings.</p>
					</div>
				{:else}
					{#each $threads.messages as msg, i (i)}
						<div class="bubble user">{msg.user_input}</div>
						{#if msg.pending}
							<div class="bubble agent pending">Thinking…</div>
						{:else if msg.response}
							<div class="bubble agent">
								{@html DOMPurify.sanitize(marked.parse(msg.response).toString())}
							</div>
						{/if}
					{/each}
				{/if}

				{#if $threads.error}
					<p class="error">{$threads.error}</p>
				{/if}
			</div>

			<ChatComposer disabled={$threads.sending} on:send={handleSend} />
		</div>
	</div>
{/if}

<style>
	.page {
		padding: 28px 24px 40px;
	}

	.layout {
	display: grid;
	grid-template-columns: 220px minmax(0, 1fr);
	gap: 24px;
	height: calc(100vh - 62px - 68px);
	}

	.chat {
	display: flex;
	flex-direction: column;
	min-height: 0;
	min-width: 0;
	}

	.messages {
		flex: 1;
		overflow-y: auto;
		display: flex;
		flex-direction: column;
		gap: 10px;
		padding-bottom: 16px;
		min-width: 0;
	}

	.welcome {
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		height: 100%;
		text-align: center;
		color: var(--color-text-muted);
		gap: 6px;
	}

	.welcome h2 {
		font-size: 20px;
		color: var(--color-text);
	}

	.welcome p {
		margin: 0;
		font-size: 13.5px;
	}

	.bubble {
		max-width: min(800px, 75%);
		padding: 10px 14px;
		border-radius: var(--radius-md);
		font-size: 13.5px;
		line-height: 1.55;
		overflow-wrap: anywhere;
		word-break: break-word;
		min-width: 0;
	}
	.bubble.user {
		margin-left: auto;
		margin-right: 12px;
		background: var(--color-accent);
		color: var(--color-bg);
		border-bottom-right-radius: 4px;
	}

	.bubble.agent {
		align-self: flex-start;
		background: var(--color-surface-2);
		color: var(--color-text);
		border: 1px solid var(--color-border-soft);
		border-bottom-left-radius: 4px;
	}

	.bubble.pending {
		color: var(--color-text-faint);
	}

	.bubble :global(table) {
    display: block;
    overflow-x: auto;
    width: 100%;
    border-collapse: collapse;
	}

	.bubble :global(th),
	.bubble :global(td) {
		border: 1px solid var(--color-border-soft);
		padding: .5rem;
		white-space: nowrap;
		text-align: left;
	}

	.bubble pre {
    overflow-x: auto;
    padding: 12px;
    border-radius: 8px;
    background: #111;
	}

	.bubble code {
		font-family: monospace;
	}

	.bubble img {
    max-width: 100%;
    border-radius: 8px;
	}

	.hint {
		font-size: 12.5px;
		color: var(--color-text-faint);
	}

	.error {
		font-size: 12.5px;
		color: var(--color-danger);
	}

	@media (max-width: 720px) {
		.layout {
			grid-template-columns: 1fr;
			height: auto;
		}
	}
</style>
