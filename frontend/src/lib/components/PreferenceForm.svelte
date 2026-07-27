<script>
	import { createEventDispatcher, onMount } from 'svelte';
	import { getColumnOptions } from '../api/query.js';

	/** Existing Preference row, or null for a brand-new user. */
	export let initial = null;
	export let submitLabel = 'Save';
	export let saving = false;

	const dispatch = createEventDispatcher();

	// Fields with no server-driven options use simple text inputs — the
	// column is free-text on the backend, these are just hints.
	const USER_TYPE_OPTIONS = ['investor', 'buyer', 'agent'];
	const PROPERTY_TYPE_SUGGESTIONS = ['House', 'Land', 'Apartment', 'Mansion'];
	const INVESTMENT_GOAL_SUGGESTIONS = ['rental_apartment', 'resell'];
	const LIVING_GOAL_SUGGESTIONS = ['live_alone', 'small_family'];

	function blank() {
		return {
			user_name: '',
			user_type: '',
			property_type: '',
			prefecture: '',
			city: '',
			district: '',
			structure: '',
			layout: '',
			direction_facing: '',
			occupancy: '',
			transaction_type: '',
			parking: '',
			min_price: null,
			max_price: null,
			target_price: null,
			min_size: null,
			max_size: null,
			investment_goal: '',
			living_goal: ''
		};
	}

	let form = { ...blank(), ...(initial ?? {}) };
	let nameError = '';

	let optionCache = {};
	async function loadOptions(column) {
		if (optionCache[column]) return;
		try {
			const res = await getColumnOptions(column);
			optionCache = { ...optionCache, [column]: res.options || [] };
		} catch {
			optionCache = { ...optionCache, [column]: [] };
		}
	}

	onMount(() => {
		loadOptions('prefecture');
		loadOptions('structure');
		loadOptions('occupancy');
	});

	function submit(e) {
		e.preventDefault();
		const name = (form.user_name || '').trim();
		if (!name) {
			nameError = 'Name is required.';
			return;
		}
		nameError = '';
		dispatch('submit', { ...form, user_name: name });
	}

	function cancel() {
		dispatch('cancel');
	}
</script>

<form on:submit={submit}>
	<fieldset>
		<legend>Basics</legend>

		<label class="field">
			<span>Your name <em>(required)</em></span>
			<input type="text" bind:value={form.user_name} placeholder="e.g. Kenji" />
			{#if nameError}<small class="error">{nameError}</small>{/if}
		</label>

		<div class="grid-2">
			<label class="field">
				<span>I am a…</span>
				<select bind:value={form.user_type}>
					<option value="">Not set</option>
					{#each USER_TYPE_OPTIONS as opt}
						<option value={opt}>{opt}</option>
					{/each}
				</select>
			</label>

			<label class="field">
				<span>Property type</span>
				<input list="property-type-list" type="text" bind:value={form.property_type} />
				<datalist id="property-type-list">
					{#each PROPERTY_TYPE_SUGGESTIONS as opt}<option value={opt} />{/each}
				</datalist>
			</label>
		</div>
	</fieldset>

	<fieldset>
		<legend>Location</legend>
		<div class="grid-3">
			<label class="field">
				<span>Prefecture</span>
				<select bind:value={form.prefecture}>
					<option value="">Any</option>
					{#each optionCache.prefecture ?? [] as opt}
						<option value={opt}>{opt}</option>
					{/each}
				</select>
			</label>
			<label class="field">
				<span>City</span>
				<input type="text" bind:value={form.city} placeholder="e.g. Minato-ku" />
			</label>
			<label class="field">
				<span>District</span>
				<input type="text" bind:value={form.district} placeholder="e.g. Kaigan" />
			</label>
		</div>
	</fieldset>

	<fieldset>
		<legend>Property details</legend>
		<div class="grid-3">
			<label class="field">
				<span>Structure</span>
				<select bind:value={form.structure}>
					<option value="">Any</option>
					{#each optionCache.structure ?? [] as opt}
						<option value={opt}>{opt}</option>
					{/each}
				</select>
			</label>
			<label class="field">
				<span>Occupancy</span>
				<select bind:value={form.occupancy}>
					<option value="">Any</option>
					{#each optionCache.occupancy ?? [] as opt}
						<option value={opt}>{opt}</option>
					{/each}
				</select>
			</label>
			<label class="field">
				<span>Layout</span>
				<input type="text" bind:value={form.layout} placeholder="e.g. 2LDK" />
			</label>
			<label class="field">
				<span>Direction facing</span>
				<input type="text" bind:value={form.direction_facing} placeholder="e.g. South" />
			</label>
			<label class="field">
				<span>Transaction type</span>
				<input type="text" bind:value={form.transaction_type} />
			</label>
			<label class="field">
				<span>Parking</span>
				<input type="text" bind:value={form.parking} placeholder="e.g. Available" />
			</label>
		</div>
	</fieldset>

	<fieldset>
		<legend>Budget &amp; size</legend>
		<div class="grid-3">
			<label class="field">
				<span>Min price (万円)</span>
				<input type="number" min="0" bind:value={form.min_price} />
			</label>
			<label class="field">
				<span>Max price (万円)</span>
				<input type="number" min="0" bind:value={form.max_price} />
			</label>
			<label class="field">
				<span>Target price (万円)</span>
				<input type="number" min="0" bind:value={form.target_price} />
			</label>
			<label class="field">
				<span>Min size (m²)</span>
				<input type="number" min="0" bind:value={form.min_size} />
			</label>
			<label class="field">
				<span>Max size (m²)</span>
				<input type="number" min="0" bind:value={form.max_size} />
			</label>
		</div>
	</fieldset>

	<fieldset>
		<legend>Goals</legend>
		<div class="grid-2">
			<label class="field">
				<span>Investment goal</span>
				<input list="investment-goal-list" type="text" bind:value={form.investment_goal} />
				<datalist id="investment-goal-list">
					{#each INVESTMENT_GOAL_SUGGESTIONS as opt}<option value={opt} />{/each}
				</datalist>
			</label>
			<label class="field">
				<span>Living goal</span>
				<input list="living-goal-list" type="text" bind:value={form.living_goal} />
				<datalist id="living-goal-list">
					{#each LIVING_GOAL_SUGGESTIONS as opt}<option value={opt} />{/each}
				</datalist>
			</label>
		</div>
	</fieldset>

	<div class="actions">
		<button type="button" class="ghost" on:click={cancel} disabled={saving}>Cancel</button>
		<button type="submit" class="primary-btn" disabled={saving}>
			{saving ? 'Saving…' : submitLabel}
		</button>
	</div>
</form>

<style>
	fieldset {
		border: none;
		padding: 0;
		margin: 0 0 22px;
	}

	legend {
		font-family: var(--font-mono);
		font-size: 11px;
		letter-spacing: 0.06em;
		text-transform: uppercase;
		color: var(--color-secondary);
		margin-bottom: 10px;
		padding: 0;
	}

	.grid-2 {
		display: grid;
		grid-template-columns: 1fr 1fr;
		gap: 12px;
	}

	.grid-3 {
		display: grid;
		grid-template-columns: repeat(3, 1fr);
		gap: 12px;
	}

	.field {
		display: flex;
		flex-direction: column;
		gap: 5px;
		font-size: 12px;
		color: var(--color-text-muted);
		margin-bottom: 12px;
	}

	.field em {
		font-style: normal;
		color: var(--color-text-faint);
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
		transition: border-color var(--dur-fast) var(--ease-soft);
	}

	input:focus-visible,
	select:focus-visible {
		border-color: var(--color-accent);
	}

	.error {
		color: var(--color-danger);
	}

	.actions {
		display: flex;
		justify-content: flex-end;
		gap: 10px;
		padding-top: 4px;
		border-top: 1px dashed var(--color-border-soft);
		margin-top: 4px;
	}

	button {
		border: none;
		cursor: pointer;
		border-radius: var(--radius-sm);
		font-size: 13.5px;
		padding: 10px 18px;
		transition:
			transform var(--dur-fast) var(--ease-soft),
			background var(--dur-fast) var(--ease-soft),
			opacity var(--dur-fast) var(--ease-soft);
	}

	button:active {
		transform: scale(0.97);
	}

	button:disabled {
		opacity: 0.6;
		cursor: default;
	}

	.primary-btn {
		background: var(--color-accent);
		color: var(--color-bg);
		font-weight: 500;
	}

	.primary-btn:hover:not(:disabled) {
		background: var(--color-accent-strong);
	}

	.ghost {
		background: transparent;
		color: var(--color-text-muted);
		border: 1px solid var(--color-border);
	}

	.ghost:hover:not(:disabled) {
		color: var(--color-text);
		border-color: var(--color-text-faint);
	}

	@media (max-width: 480px) {
		.grid-2,
		.grid-3 {
			grid-template-columns: 1fr;
		}
	}
</style>
