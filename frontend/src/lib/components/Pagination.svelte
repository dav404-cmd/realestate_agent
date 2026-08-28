<script>
	import { createEventDispatcher } from 'svelte';

	export let page = 1;
	export let hasNext = true;
	export let disabled = false;

	const dispatch = createEventDispatcher();
</script>

<div class="pagination">
	<button on:click={() => dispatch('change', page - 1)} disabled={disabled || page <= 1}>
		← Prev
	</button>
	<span class="page-num">Page {page}</span>
	<button on:click={() => dispatch('change', page + 1)} disabled={disabled || !hasNext}>
		Next →
	</button>
</div>

<style>
	.pagination {
		display: flex;
		align-items: center;
		justify-content: center;
		gap: 16px;
		padding: 20px 0 4px;
	}

	.page-num {
		font-family: var(--font-mono);
		font-size: 12.5px;
		color: var(--color-text-muted);
		min-width: 64px;
		text-align: center;
	}

	button {
		border: 1px solid var(--color-border);
		background: var(--color-surface);
		color: var(--color-text);
		border-radius: var(--radius-pill);
		font-size: 13px;
		padding: 8px 16px;
		cursor: pointer;
		transition:
			border-color var(--dur-fast) var(--ease-soft),
			background var(--dur-fast) var(--ease-soft),
			opacity var(--dur-fast) var(--ease-soft);
	}

	button:hover:not(:disabled) {
		border-color: var(--color-accent);
		background: var(--color-accent-bg);
	}

	button:disabled {
		opacity: 0.4;
		cursor: default;
	}
</style>
