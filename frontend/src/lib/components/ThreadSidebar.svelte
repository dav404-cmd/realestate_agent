<script>
	import { createEventDispatcher } from 'svelte';

	export let threads = [];
	export let activeThreadId = null;
	export let status = 'idle';

	const dispatch = createEventDispatcher();

	$: sorted = [...threads].sort(
		(a, b) => new Date(b.updated_at ?? b.created_at) - new Date(a.updated_at ?? a.created_at)
	);
</script>

<aside class="sidebar">
	<button class="new-chat" on:click={() => dispatch('new')}>+ New chat</button>

	{#if status === 'loading'}
		<p class="hint">Loading conversations…</p>
	{:else if sorted.length === 0}
		<p class="hint">No conversations yet.</p>
	{:else}
		<ul>
			{#each sorted as t (t.id)}
				<li>
					<button
						class="thread-btn"
						class:active={t.id === activeThreadId}
						on:click={() => dispatch('select', t.id)}
					>
						{t.title || 'Untitled chat'}
					</button>
				</li>
			{/each}
		</ul>
	{/if}
</aside>

<style>
	.sidebar {
		display: flex;
		flex-direction: column;
		gap: 10px;
		border-right: 1px solid var(--color-border-soft);
		padding-right: 16px;
		height: 100%;
		overflow-y: auto;
	}

	.new-chat {
		border: 1px dashed var(--color-border);
		background: transparent;
		color: var(--color-text-muted);
		border-radius: var(--radius-sm);
		padding: 10px 12px;
		font-size: 13px;
		cursor: pointer;
		transition:
			border-color var(--dur-fast) var(--ease-soft),
			color var(--dur-fast) var(--ease-soft);
	}

	.new-chat:hover {
		border-color: var(--color-accent);
		color: var(--color-accent-strong);
	}

	.hint {
		font-size: 12.5px;
		color: var(--color-text-faint);
		padding: 8px 4px;
	}

	ul {
		list-style: none;
		margin: 0;
		padding: 0;
		display: flex;
		flex-direction: column;
		gap: 2px;
	}

	.thread-btn {
		width: 100%;
		text-align: left;
		background: transparent;
		border: none;
		border-radius: var(--radius-sm);
		padding: 9px 10px;
		font-size: 13px;
		color: var(--color-text-muted);
		cursor: pointer;
		overflow: hidden;
		text-overflow: ellipsis;
		white-space: nowrap;
		transition:
			background var(--dur-fast) var(--ease-soft),
			color var(--dur-fast) var(--ease-soft);
	}

	.thread-btn:hover {
		background: var(--color-surface-2);
		color: var(--color-text);
	}

	.thread-btn.active {
		background: var(--color-accent-bg);
		color: var(--color-accent-strong);
	}

	@media (max-width: 720px) {
		.sidebar {
			border-right: none;
			border-bottom: 1px solid var(--color-border-soft);
			padding-right: 0;
			padding-bottom: 12px;
		}
	}
</style>
