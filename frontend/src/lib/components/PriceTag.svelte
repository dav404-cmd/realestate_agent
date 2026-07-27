<script>
	/** price in 万円 (man-yen) units, matching backend's price_yen field name but
	 * treat as the raw number the backend returns — displayed as-is with a ¥ mark.
	 * Adjust the multiplier below if your backend's price_yen is actually full yen. */
	export let value;
	export let size = 'md'; // 'sm' | 'md' | 'lg'

	$: formatted = typeof value === 'number' ? new Intl.NumberFormat('en-US').format(value) : '—';
</script>

<span class="price price-{size}">
	<span class="mark">¥</span><span class="num">{formatted}</span><span class="unit">万</span>
</span>

<style>
	.price {
		font-family: var(--font-mono);
		display: inline-flex;
		align-items: baseline;
		gap: 2px;
		color: var(--color-text);
	}

	.mark {
		color: var(--color-secondary);
		font-size: 0.75em;
	}

	.unit {
		color: var(--color-text-muted);
		font-size: 0.6em;
		margin-left: 1px;
	}

	.price-sm {
		font-size: 14px;
	}
	.price-md {
		font-size: 20px;
		font-weight: 500;
	}
	.price-lg {
		font-size: 30px;
		font-weight: 500;
	}
</style>
