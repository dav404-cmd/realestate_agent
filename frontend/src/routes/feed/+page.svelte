<script>
	import { onMount } from 'svelte';
	import { fly } from 'svelte/transition';
	import PropertyCard from '$lib/components/PropertyCard.svelte';
	import CardSkeleton from '$lib/components/CardSkeleton.svelte';
	import EmptyState from '$lib/components/EmptyState.svelte';
	import { auth } from '$lib/stores/auth.js';
	import { profile, isPreferenceEmpty } from '$lib/stores/profile.js';
	import { preferenceModal } from '$lib/stores/preferenceModal.js';
	import { searchProperties } from '$lib/api/query.js';
	import { mapPreferenceToQuery } from '$lib/utils/mapPreferenceToQuery.js';

	let status = 'idle'; // 'idle' | 'loading' | 'ready' | 'error'
	let error = null;
	let results = [];

	// Direct-URL visits (not routed through Nav's gate) get the same rule:
	// no meaningful preference yet -> stay here, show a prompt, don't fetch.
	$: needsPreference = $profile.status !== 'ready' || isPreferenceEmpty($profile.pref);

	async function run() {
		status = 'loading';
		error = null;
		try {
			const query = mapPreferenceToQuery($profile.pref);
			results = await searchProperties(query);
			status = 'ready';
		} catch (err) {
			error = err.message || 'Could not load your feed.';
			status = 'error';
		}
	}

	$: if ($auth.status === 'authenticated' && !needsPreference && status === 'idle') {
		run();
	}

	onMount(() => {
		if ($auth.status === 'authenticated' && !needsPreference) run();
	});
</script>

<svelte:head>
	<title>Your Feed — Tsubonote</title>
</svelte:head>

<section class="container page">
	<p class="eyebrow">Your feed</p>
	<h1>Matches based on what you told us</h1>

	{#if $auth.status !== 'authenticated'}
		<EmptyState title="Sign in to see your feed" message="Your feed is built from your saved preferences." />
	{:else if needsPreference}
		<EmptyState
			title="Tell us what you're looking for"
			message="Your feed needs at least one preference set — price range, area, or property type."
		>
			<button class="primary-btn" on:click={() => preferenceModal.openOnboarding()}>
				Set preferences
			</button>
		</EmptyState>
	{:else if status === 'loading'}
		<div class="grid">
			{#each Array(8) as _, i (i)}
				<CardSkeleton />
			{/each}
		</div>
	{:else if status === 'error'}
		<EmptyState tone="error" title="Couldn't load your feed" message={error} />
	{:else if results.length === 0}
		<EmptyState
			title="No matches yet"
			message="Nothing fits your current preferences right now — try widening them from your profile."
		/>
	{:else}
		<p class="count">{results.length} match{results.length === 1 ? '' : 'es'}</p>
		<div class="grid">
			{#each results as listing, i (listing.id)}
				<div in:fly={{ y: 12, duration: 320, delay: Math.min(i * 30, 240) }}>
					<PropertyCard {listing} />
				</div>
			{/each}
		</div>
	{/if}
</section>

<style>
	.page {
		padding: 40px 24px 70px;
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
		font-size: clamp(24px, 3.6vw, 32px);
		margin-bottom: 26px;
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

	.primary-btn {
		margin-top: 10px;
		border: none;
		cursor: pointer;
		border-radius: var(--radius-sm);
		font-size: 13.5px;
		padding: 10px 18px;
		background: var(--color-accent);
		color: var(--color-bg);
		font-weight: 500;
		transition: background var(--dur-fast) var(--ease-soft);
	}

	.primary-btn:hover {
		background: var(--color-accent-strong);
	}
</style>
