<script>
	import Thumbnail from './Thumbnail.svelte';
	import PriceTag from './PriceTag.svelte';

	export let listing;

	$: data = listing?.data ?? {};
	$: title = data.building_name || `${data.city ?? ''} ${data.layout ?? ''}`.trim() || 'Untitled listing';
	$: locationLine = [data.prefecture, data.city, data.district].filter(Boolean).join(' · ');
	$: station =
		data.ns_name && data.ns_distance_min
			? `${data.ns_name} · ${data.ns_distance_min} min ${data.ns_mode ?? 'walk'}`
			: null;
</script>

<a class="card" href={`/property/${listing.id}`}>
	<div class="fold" aria-hidden="true"></div>
	<Thumbnail src={listing.thumbnail_src} alt={title} />

	<div class="body">
		<h3 class="title" title={title}>{title}</h3>
		{#if locationLine}
			<p class="location">{locationLine}</p>
		{/if}

		<div class="chips">
			{#if data.layout}<span class="chip">{data.layout}</span>{/if}
			{#if data.size}<span class="chip">{data.size} m²</span>{/if}
			{#if data.structure}<span class="chip">{data.structure}</span>{/if}
		</div>

		{#if station}
			<p class="station">
				<svg viewBox="0 0 16 16" width="12" height="12" fill="none" aria-hidden="true">
					<path d="M8 1v14M2 5l6-4 6 4M2 5v6l6 4 6-4V5" stroke="currentColor" stroke-width="1.3" stroke-linejoin="round" />
				</svg>
				{station}
			</p>
		{/if}

		<div class="footer">
			<PriceTag value={listing.price_yen} size="md" />
			{#if data.occupancy}
				<span class="occupancy" class:vacant={data.occupancy === 'Vacant'}>{data.occupancy}</span>
			{/if}
		</div>
	</div>
</a>

<style>
	.card {
		position: relative;
		display: block;
		background: var(--color-surface);
		border: 1px solid var(--color-border-soft);
		border-radius: var(--radius-lg);
		padding: 10px;
		overflow: hidden;
		transition:
			transform var(--dur-med) var(--ease-soft),
			border-color var(--dur-med) var(--ease-soft),
			box-shadow var(--dur-med) var(--ease-soft);
	}

	.card::before {
		content: '';
		position: absolute;
		left: 0;
		top: 0;
		bottom: 0;
		width: 3px;
		background: var(--color-accent);
		transform: scaleY(0);
		transform-origin: top;
		transition: transform var(--dur-med) var(--ease-soft);
	}

	.card:hover,
	.card:focus-visible {
		transform: translateY(-3px);
		border-color: var(--color-border);
		box-shadow: var(--shadow-soft);
	}

	.card:hover::before,
	.card:focus-visible::before {
		transform: scaleY(1);
	}

	/* Paper corner-fold: a nod to the printed listing slips (物件チラシ) this data comes from */
	.fold {
		position: absolute;
		top: 0;
		right: 0;
		width: 22px;
		height: 22px;
		background: linear-gradient(135deg, transparent 50%, var(--color-secondary-bg) 50%);
		border-bottom-left-radius: var(--radius-sm);
		z-index: 1;
		opacity: 0.9;
	}

	.body {
		padding: 14px 6px 4px;
	}

	.title {
		font-size: 15px;
		font-weight: 500;
		line-height: 1.3;
		overflow: hidden;
		text-overflow: ellipsis;
		display: -webkit-box;
		-webkit-line-clamp: 2;
		-webkit-box-orient: vertical;
	}

	.location {
		margin: 4px 0 0;
		font-size: 12.5px;
		color: var(--color-text-muted);
	}

	.chips {
		display: flex;
		flex-wrap: wrap;
		gap: 6px;
		margin-top: 10px;
	}

	.chip {
		font-size: 11.5px;
		padding: 3px 9px;
		border-radius: var(--radius-pill);
		background: var(--color-surface-2);
		color: var(--color-text-muted);
		border: 1px solid var(--color-border-soft);
	}

	.station {
		display: flex;
		align-items: center;
		gap: 5px;
		margin: 10px 0 0;
		font-size: 12px;
		color: var(--color-accent-strong);
	}

	.footer {
		display: flex;
		align-items: baseline;
		justify-content: space-between;
		margin-top: 14px;
		padding-top: 10px;
		border-top: 1px dashed var(--color-border-soft);
	}

	.occupancy {
		font-size: 11px;
		color: var(--color-text-faint);
	}

	.occupancy.vacant {
		color: var(--color-success);
	}
</style>
