<script>
	import { onMount } from 'svelte';
	import { fly } from 'svelte/transition';
	import SearchFilters from '$lib/components/SearchFilters.svelte';
	import PropertyCard from '$lib/components/PropertyCard.svelte';
	import CardSkeleton from '$lib/components/CardSkeleton.svelte';
	import EmptyState from '$lib/components/EmptyState.svelte';
	import { filters, results, searchStatus, searchError } from '$lib/stores/search.js';
	import { searchProperties } from '$lib/api/query.js';

	async function runSearch() {
		$searchStatus = 'loading';
		$searchError = null;
		try {
			const query = Object.fromEntries(
				Object.entries($filters).filter(([, v]) => v !== '' && v !== null && v !== undefined)
			);
			const data = await searchProperties(query);
			$results = Array.isArray(data) ? data : [];
			$searchStatus = 'ready';
		} catch (err) {
			$searchError = err.message || 'Something went wrong while searching.';
			$searchStatus = 'error';
		}
	}

	onMount(runSearch);
</script>

<svelte:head>
	<title>Explore listings — Tsubonote</title>
</svelte:head>

<section class="hero container">
	<p class="eyebrow">Guest explore</p>
	<h1>Browse Japan's listings, unfiltered by anyone but you.</h1>
	<p class="sub">
		Search live scraped inventory across prefectures. Sign in to save preferences and talk it
		through with the agent.
	</p>
</section>

<section class="filter-bar container">
	<SearchFilters on:search={runSearch} />
</section>

<section class="results container">
	{#if $searchStatus === 'loading'}
		<div class="grid">
			{#each Array(8) as _, i (i)}
				<CardSkeleton />
			{/each}
		</div>
	{:else if $searchStatus === 'error'}
		<EmptyState tone="error" title="Couldn't load listings" message={$searchError} />
	{:else if $results.length === 0}
		<EmptyState
			title="No listings match those filters"
			message="Try widening your price range or clearing a filter."
		/>
	{:else}
		<p class="count">{$results.length} listing{$results.length === 1 ? '' : 's'}</p>
		<div class="grid">
			{#each $results as listing, i (listing.id)}
				<div in:fly={{ y: 12, duration: 320, delay: Math.min(i * 30, 240) }}>
					<PropertyCard {listing} />
				</div>
			{/each}
		</div>
	{/if}
</section>

<style>
	.hero {
		padding: 48px 24px 8px;
	}

	.eyebrow {
		font-family: var(--font-mono);
		font-size: 11.5px;
		letter-spacing: 0.08em;
		text-transform: uppercase;
		color: var(--color-secondary);
		margin: 0 0 10px;
	}

	h1 {
		font-size: clamp(26px, 4vw, 38px);
		max-width: 18ch;
		line-height: 1.15;
	}

	.sub {
		margin: 14px 0 0;
		max-width: 56ch;
		color: var(--color-text-muted);
		font-size: 14.5px;
	}

	.filter-bar {
		margin-top: 30px;
		padding: 16px;
		background: var(--color-surface);
		border: 1px solid var(--color-border-soft);
		border-radius: var(--radius-lg);
	}

	.results {
		margin-top: 28px;
		padding-bottom: 60px;
	}

	.count {
		font-size: 12.5px;
		color: var(--color-text-faint);
		margin: 0 0 14px;
	}

	.grid {
		display: grid;
		grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
		gap: 16px;
	}
</style>
