<script>
	import { createEventDispatcher } from 'svelte';

	export let disabled = false;

	const dispatch = createEventDispatcher();
	let value = '';

	function submit() {
		const trimmed = value.trim();
		if (!trimmed || disabled) return;
		dispatch('send', trimmed);
		value = '';
	}

	function onKeydown(e) {
		if (e.key === 'Enter' && !e.shiftKey) {
			e.preventDefault();
			submit();
		}
	}
</script>

<form class="composer" on:submit|preventDefault={submit}>
	<textarea
		bind:value
		on:keydown={onKeydown}
		placeholder="Ask about listings, areas, or your search…"
		rows="1"
		{disabled}
	></textarea>
	<button type="submit" disabled={disabled || !value.trim()}>Send</button>
</form>

<style>
	.composer {
		display: flex;
		gap: 10px;
		align-items: flex-end;
		border-top: 1px solid var(--color-border-soft);
		padding-top: 14px;
	}

	textarea {
		flex: 1;
		resize: none;
		max-height: 140px;
		font-family: var(--font-body);
		font-size: 13.5px;
		color: var(--color-text);
		background: var(--color-surface-2);
		border: 1px solid var(--color-border);
		border-radius: var(--radius-md);
		padding: 11px 12px;
		outline: none;
		transition: border-color var(--dur-fast) var(--ease-soft);
	}

	textarea:focus-visible {
		border-color: var(--color-accent);
	}

	button {
		border: none;
		cursor: pointer;
		border-radius: var(--radius-sm);
		font-size: 13.5px;
		padding: 11px 18px;
		background: var(--color-accent);
		color: var(--color-bg);
		font-weight: 500;
		transition:
			background var(--dur-fast) var(--ease-soft),
			opacity var(--dur-fast) var(--ease-soft);
	}

	button:hover:not(:disabled) {
		background: var(--color-accent-strong);
	}

	button:disabled {
		opacity: 0.5;
		cursor: default;
	}
</style>
