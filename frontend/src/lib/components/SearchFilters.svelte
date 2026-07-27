<script>
	import { createEventDispatcher, onMount } from 'svelte';
	import { filters, defaultFilters } from '../stores/search.js';
	import { getColumnOptions } from '../api/query.js';

	const dispatch = createEventDispatcher();

	let expanded = false;
	let optionCache = {};

	const SORT_OPTIONS = [
		{ value: 'price_yen:asc', label: 'Price, low to high' },
		{ value: 'price_yen:desc', label: 'Price, high to low' },
		{ value: 'scraped_at:desc', label: 'Newest first' }
	];

	async function loadOptions(column) {
		if (optionCache[column]) return optionCache[column];
		try {
			const res = await getColumnOptions(column);
			optionCache[column] = res.options || [];
		} catch {
			optionCache[column] = [];
		}
		optionCache = optionCache; // eslint-disable-line no-self-assign
		return optionCache[column];
	}

	onMount(() => {
		loadOptions('prefecture');
		loadOptions('structure');
		loadOptions('occupancy');
	});

	function handleSortChange(e) {
		const [sort_by, sort_order] = e.target.value.split(':');
		$filters = { ...$filters, sort_by, sort_order };
	}

	function submit() {
		dispatch('search');
	}

	function reset() {
		$filters = { ...defaultFilters };
		dispatch('search');
	}

	function onSubmit(e) {
		e.preventDefault();
		submit();
	}
</script>

<form class="filters" on:submit={onSubmit}>
	<div class="row primary">
		<label class="field grow">
			<span>Prefecture</span>
			<select bind:value={$filters.prefecture}>
				<option value="">Any</option>
				{#each optionCache.prefecture ?? [] as opt}
					<option value={opt}>{opt}</option>
				{/each}
			</select>
		</label>

		<label class="field grow">
			<span>City</span>
			<input type="text" placeholder="e.g. Minato-ku" bind:value={$filters.city} />
		</label>

		<label class="field">
			<span>Sort</span>
			<select value={`${$filters.sort_by}:${$filters.sort_order}`} on:change={handleSortChange}>
				{#each SORT_OPTIONS as opt}
					<option value={opt.value}>{opt.label}</option>
				{/each}
			</select>
		</label>

		<button type="button" class="ghost toggle" on:click={() => (expanded = !expanded)}>
			{expanded ? 'Fewer filters' : 'More filters'}
		</button>

		<button type="submit" class="primary-btn">Search</button>
	</div>

	{#if expanded}
		<div class="row secondary">
			<label class="field">
				<span>District</span>
				<input type="text" placeholder="e.g. Kaigan" bind:value={$filters.district} />
			</label>

			<label class="field">
				<span>Structure</span>
				<select bind:value={$filters.structure}>
					<option value="">Any</option>
					{#each optionCache.structure ?? [] as opt}
						<option value={opt}>{opt}</option>
					{/each}
				</select>
			</label>

			<label class="field">
				<span>Occupancy</span>
				<select bind:value={$filters.occupancy}>
					<option value="">Any</option>
					{#each optionCache.occupancy ?? [] as opt}
						<option value={opt}>{opt}</option>
					{/each}
				</select>
			</label>

			<label class="field">
				<span>Min price (万円)</span>
				<input type="number" min="0" bind:value={$filters.min_price} />
			</label>

			<label class="field">
				<span>Max price (万円)</span>
				<input type="number" min="0" bind:value={$filters.max_price} />
			</label>

			<label class="field">
				<span>Min size (m²)</span>
				<input type="number" min="0" bind:value={$filters.min_size} />
			</label>

			<label class="field">
				<span>Max size (m²)</span>
				<input type="number" min="0" bind:value={$filters.max_size} />
			</label>

			<button type="button" class="ghost" on:click={reset}>Reset</button>
		</div>
	{/if}
</form>

<style>
	.filters {
		display: flex;
		flex-direction: column;
		gap: 10px;
	}

	.row {
		display: flex;
		flex-wrap: wrap;
		align-items: flex-end;
		gap: 10px;
	}

	.field {
		display: flex;
		flex-direction: column;
		gap: 5px;
		font-size: 12px;
		color: var(--color-text-muted);
		min-width: 130px;
	}

	.field.grow {
		flex: 1 1 200px;
	}

	input,
	select {
		font-family: var(--font-body);
		font-size: 13.5px;
		color: var(--color-text);
		background: var(--color-surface-2);
		border: 1px solid var(--color-border);
		border-radius: var(--radius-sm);
		padding: 9px 10px;
		outline: none;
		transition:
			border-color var(--dur-fast) var(--ease-soft),
			background var(--dur-fast) var(--ease-soft);
	}

	input:hover,
	select:hover {
		border-color: var(--color-text-faint);
	}

	input:focus-visible,
	select:focus-visible {
		border-color: var(--color-accent);
	}

	button {
		border: none;
		cursor: pointer;
		border-radius: var(--radius-sm);
		font-size: 13.5px;
		padding: 10px 16px;
		transition:
			transform var(--dur-fast) var(--ease-soft),
			background var(--dur-fast) var(--ease-soft),
			opacity var(--dur-fast) var(--ease-soft);
	}

	button:active {
		transform: scale(0.97);
	}

	.primary-btn {
		background: var(--color-accent);
		color: var(--color-bg);
		font-weight: 500;
	}

	.primary-btn:hover {
		background: var(--color-accent-strong);
	}

	.ghost {
		background: transparent;
		color: var(--color-text-muted);
		border: 1px solid var(--color-border);
	}

	.ghost:hover {
		color: var(--color-text);
		border-color: var(--color-text-faint);
	}

	.toggle {
		white-space: nowrap;
	}

	@media (max-width: 640px) {
		.row {
			flex-direction: column;
			align-items: stretch;
		}
		.field {
			min-width: 0;
		}
	}
</style>
