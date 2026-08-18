<script>
	import { page } from '$app/stores';
	import { onMount } from 'svelte';
	import { fade } from 'svelte/transition';
import Thumbnail from '$lib/components/Thumbnail.svelte';
import ImageGallery from '$lib/components/ImageGallery.svelte';
import PriceTag from '$lib/components/PriceTag.svelte';
import EmptyState from '$lib/components/EmptyState.svelte';
import { getProperty } from '$lib/api/query.js';
import { getListingUrl } from '$lib/utils/listingUrl.js';

let status = 'loading';
let error = null;
let listing = null;

$: data = listing?.data ?? {};
$: allImages = Array.isArray(listing?.images) ? listing.images : [];
$: galleryImages = allImages
	.sort((a, b) => a.image_order - b.image_order);
$: sourceUrl = listing ? getListingUrl(listing.source_listing_id, listing.source) : null;

	const DETAIL_FIELDS = [
		['layout', 'Layout'],
		['size', 'Size (m²)'],
		['structure', 'Structure'],
		['occupancy', 'Occupancy'],
		['unit_floor', 'Floor'],
		['total_floors', 'Total floors'],
		['direction_facing', 'Facing'],
		['transaction_type', 'Transaction'],
		['land_rights', 'Land rights'],
		['parking', 'Parking'],
		['maintenance_fee', 'Maintenance fee'],
		['repair_reserve_fund', 'Repair reserve fund'],
		['available_from', 'Available from'],
		['construction_completed', 'Built'],
		['manage_type', 'Management']
	];

	async function load() {
		status = 'loading';
		try {
			listing = await getProperty($page.params.id);
			status = 'ready';
		} catch (err) {
			error = err.message || 'Could not load this listing.';
			status = 'error';
		}
	}

	onMount(load);
</script>

<svelte:head>
	<title>{data.building_name || 'Listing'} — Tsubonote</title>
</svelte:head>

<div class="container page">
	<a href="/" class="back">← Back to search</a>

	{#if status === 'loading'}
		<div class="skeleton-hero" aria-hidden="true"></div>
	{:else if status === 'error'}
		<EmptyState tone="error" title="Couldn't load this listing" message={error} />
	{:else}
		<div class="layout" in:fade={{ duration: 220 }}>
			<div class="media">
			{#if galleryImages.length > 0}
				<ImageGallery images={galleryImages} alt={data.building_name} />
			{:else}
				<Thumbnail src={listing.thumbnail_src} alt={data.building_name} />
			{/if}
		</div>

			<div class="summary">
				<p class="eyebrow">{[data.prefecture, data.city, data.district].filter(Boolean).join(' · ')}</p>
				<h1>{data.building_name || `${data.city ?? ''} listing`}</h1>

				{#if data.ns_name}
					<p class="station">{data.ns_name} · {data.ns_distance_min} min {data.ns_mode ?? 'walk'} · {data.ns_line}</p>
				{/if}

				<div class="price-block">
					<PriceTag value={listing.price_yen} size="lg" />
					<span class="status" class:active={listing.status === 'active'}>{listing.status}</span>
					{#if sourceUrl}
						<a class="source-link" href={sourceUrl} target="_blank" rel="noopener noreferrer">
							View original listing ↗
						</a>
					{/if}
				</div>
			</div>
		</div>

		<div class="details">
			<h2>Details</h2>
			<dl class="detail-grid">
				{#each DETAIL_FIELDS as [key, label]}
					{#if data[key] !== undefined && data[key] !== null && data[key] !== ''}
						<div class="detail-row">
							<dt>{label}</dt>
							<dd>{data[key]}</dd>
						</div>
					{/if}
				{/each}
			</dl>
		</div>

		{#if data.building_description}
			<div class="description">
				<h2>About this building</h2>
				<p>{data.building_description}</p>
			</div>
		{/if}

		{#if data.landmarks}
			<div class="description">
				<h2>Access &amp; landmarks</h2>
				<p>{data.landmarks}</p>
			</div>
		{/if}
	{/if}
</div>

<style>
	.page {
		padding: 28px 24px 80px;
		max-width: 880px;
	}

	.back {
		display: inline-block;
		font-size: 13px;
		color: var(--color-text-muted);
		margin-bottom: 22px;
		transition: color var(--dur-fast) var(--ease-soft);
	}

	.back:hover {
		color: var(--color-accent-strong);
	}

	.skeleton-hero {
		height: 320px;
		border-radius: var(--radius-lg);
		background: linear-gradient(
			100deg,
			var(--color-surface-2) 30%,
			var(--color-border-soft) 50%,
			var(--color-surface-2) 70%
		);
		background-size: 200% 100%;
		animation: shimmer 1.6s ease-in-out infinite;
	}

	@keyframes shimmer {
		0% {
			background-position: 200% 0;
		}
		100% {
			background-position: -200% 0;
		}
	}

	.layout {
		display: grid;
		grid-template-columns: 1.1fr 1fr;
		gap: 28px;
		align-items: start;
	}

	.media :global(.thumb) {
		border-radius: var(--radius-lg);
	}

	.eyebrow {
		font-family: var(--font-mono);
		font-size: 11.5px;
		letter-spacing: 0.06em;
		text-transform: uppercase;
		color: var(--color-secondary);
		margin: 0 0 8px;
	}

	h1 {
		font-size: 26px;
		line-height: 1.25;
	}

	.station {
		margin: 12px 0 0;
		font-size: 13.5px;
		color: var(--color-accent-strong);
	}

	.price-block {
		display: flex;
		align-items: center;
		gap: 14px;
		margin-top: 24px;
		padding-top: 18px;
		border-top: 1px dashed var(--color-border-soft);
	}

	.status {
		font-size: 11.5px;
		padding: 4px 10px;
		border-radius: var(--radius-pill);
		background: var(--color-surface-2);
		color: var(--color-text-faint);
		text-transform: capitalize;
	}

	.status.active {
		color: var(--color-success);
		background: color-mix(in srgb, var(--color-success) 12%, transparent);
	}

	.source-link {
		margin-left: auto;
		font-size: 12.5px;
		color: var(--color-accent-strong);
		transition: color var(--dur-fast) var(--ease-soft);
	}

	.source-link:hover {
		color: var(--color-accent);
		text-decoration: underline;
	}

	.details,
	.description {
		margin-top: 40px;
	}
	.floorplan {
		margin-top: 40px;
	}

	h2 {
		font-size: 16px;
		margin-bottom: 14px;
	}

	.detail-grid {
		display: grid;
		grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
		gap: 0;
		margin: 0;
		border-top: 1px solid var(--color-border-soft);
	}

	.detail-row {
		display: flex;
		justify-content: space-between;
		gap: 12px;
		padding: 11px 4px;
		border-bottom: 1px solid var(--color-border-soft);
		font-size: 13px;
	}

	dt {
		color: var(--color-text-muted);
	}

	dd {
		margin: 0;
		color: var(--color-text);
		font-family: var(--font-mono);
		font-size: 12.5px;
		text-align: right;
	}

	.floorplan-frame {
		max-width: 380px;
	}

	.description p {
		font-size: 14px;
		color: var(--color-text-muted);
		line-height: 1.7;
		white-space: pre-line;
	}
	.media {
		min-width: 0;
	}

	.media :global(.thumb) {
		border-radius: var(--radius-lg);
	}
	@media (max-width: 720px) {
		.layout {
			grid-template-columns: 1fr;
		}
	}
</style>
