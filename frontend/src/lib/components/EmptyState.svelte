<script>
	export let title = 'Nothing here yet';
	export let message = '';
	export let tone = 'neutral'; // 'neutral' | 'error'
</script>

<div class="empty tone-{tone}">
	<svg viewBox="0 0 48 48" width="30" height="30" fill="none" aria-hidden="true">
		{#if tone === 'error'}
			<circle cx="24" cy="24" r="18" stroke="currentColor" stroke-width="2" />
			<path d="M24 15v12" stroke="currentColor" stroke-width="2" stroke-linecap="round" />
			<circle cx="24" cy="32" r="1.6" fill="currentColor" />
		{:else}
			<path d="M10 38V16l14-9 14 9v22" stroke="currentColor" stroke-width="2" stroke-linejoin="round" />
			<path d="M18 38v-9h12v9" stroke="currentColor" stroke-width="2" stroke-linejoin="round" />
		{/if}
	</svg>
	<h3>{title}</h3>
	{#if message}<p>{message}</p>{/if}
	<slot />
</div>

<style>
	.empty {
		display: flex;
		flex-direction: column;
		align-items: center;
		text-align: center;
		gap: 8px;
		padding: 56px 20px;
		color: var(--color-text-muted);
	}

	.empty svg {
		color: var(--color-text-faint);
		margin-bottom: 4px;
	}

	.tone-error svg {
		color: var(--color-danger);
	}

	h3 {
		font-size: 16px;
		color: var(--color-text);
	}

	p {
		margin: 0;
		font-size: 13px;
		max-width: 360px;
	}
</style>
