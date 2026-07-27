<script>
	import { createEventDispatcher } from 'svelte';
	import { fade, scale } from 'svelte/transition';

	export let title = '';

	const dispatch = createEventDispatcher();

	function close() {
		dispatch('close');
	}

	function onKeydown(e) {
		if (e.key === 'Escape') close();
	}
</script>

<svelte:window on:keydown={onKeydown} />

<div class="overlay" transition:fade={{ duration: 160 }} on:click={close}>
	<div
		class="panel"
		role="dialog"
		aria-modal="true"
		aria-label={title}
		transition:scale={{ duration: 200, start: 0.97 }}
		on:click|stopPropagation
	>
		<div class="head">
			<h2>{title}</h2>
			<button class="close" on:click={close} aria-label="Close">
				<svg viewBox="0 0 16 16" width="14" height="14" fill="none">
					<path d="M3 3l10 10M13 3L3 13" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" />
				</svg>
			</button>
		</div>
		<div class="body">
			<slot />
		</div>
	</div>
</div>

<style>
	.overlay {
		position: fixed;
		inset: 0;
		z-index: 100;
		background: rgba(8, 9, 12, 0.55);
		backdrop-filter: blur(3px);
		display: flex;
		align-items: center;
		justify-content: center;
		padding: 20px;
	}

	.panel {
		width: 100%;
		max-width: 560px;
		max-height: min(720px, 88vh);
		display: flex;
		flex-direction: column;
		background: var(--color-surface);
		border: 1px solid var(--color-border);
		border-radius: var(--radius-lg);
		box-shadow: var(--shadow-lift);
	}

	.head {
		display: flex;
		align-items: center;
		justify-content: space-between;
		padding: 18px 20px;
		border-bottom: 1px solid var(--color-border-soft);
	}

	.head h2 {
		font-size: 17px;
	}

	.close {
		display: flex;
		align-items: center;
		justify-content: center;
		width: 30px;
		height: 30px;
		border-radius: var(--radius-pill);
		border: 1px solid var(--color-border);
		background: transparent;
		color: var(--color-text-muted);
		cursor: pointer;
		transition:
			color var(--dur-fast) var(--ease-soft),
			border-color var(--dur-fast) var(--ease-soft);
	}

	.close:hover {
		color: var(--color-text);
		border-color: var(--color-text-faint);
	}

	.body {
		padding: 20px;
		overflow-y: auto;
	}
</style>
