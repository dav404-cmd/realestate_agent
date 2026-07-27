<script>
	import { fade, scale } from 'svelte/transition';
	import Thumbnail from './Thumbnail.svelte';

	export let images = []; // [{id, image_url, image_order}], already sorted
	export let alt = '';

	let activeIndex = 0;
	let lightboxOpen = false;

	$: current = images[activeIndex] ?? null;

	function open(i) {
		activeIndex = i;
		lightboxOpen = true;
	}

	function close() {
		lightboxOpen = false;
	}

	function next() {
		activeIndex = (activeIndex + 1) % images.length;
	}

	function prev() {
		activeIndex = (activeIndex - 1 + images.length) % images.length;
	}

	function onKeydown(e) {
		if (!lightboxOpen) return;
		if (e.key === 'Escape') close();
		if (e.key === 'ArrowRight' && images.length > 1) next();
		if (e.key === 'ArrowLeft' && images.length > 1) prev();
	}
</script>

<svelte:window on:keydown={onKeydown} />

<div class="gallery">
	<div
		class="main"
		on:click={() => open(activeIndex)}
		on:keydown={(e) => e.key === 'Enter' && open(activeIndex)}
		role="button"
		tabindex="0"
		aria-label="View full size"
	>
		<Thumbnail src={current?.image_url} {alt} />
		{#if images.length > 1}
			<button class="nav prev" on:click|stopPropagation={prev} aria-label="Previous photo">‹</button>
			<button class="nav next" on:click|stopPropagation={next} aria-label="Next photo">›</button>
			<span class="counter">{activeIndex + 1} / {images.length}</span>
		{/if}
	</div>

	{#if images.length > 1}
		<div class="strip">
			{#each images as img, i (img.id)}
				<button
					class="thumb-btn"
					class:active={i === activeIndex}
					on:click={() => (activeIndex = i)}
					aria-label={`Photo ${i + 1}`}
				>
					<img src={img.image_url} alt="" loading="lazy" />
				</button>
			{/each}
		</div>
	{/if}
</div>

{#if lightboxOpen && current}
	<div class="overlay" transition:fade={{ duration: 160 }} on:click={close}>
		<button class="close" on:click={close} aria-label="Close">
			<svg viewBox="0 0 16 16" width="16" height="16" fill="none">
				<path d="M3 3l10 10M13 3L3 13" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" />
			</svg>
		</button>

		{#if images.length > 1}
			<button class="lb-nav lb-prev" on:click|stopPropagation={prev} aria-label="Previous photo">‹</button>
			<button class="lb-nav lb-next" on:click|stopPropagation={next} aria-label="Next photo">›</button>
		{/if}

		<img
			class="lb-image"
			src={current.image_url}
			{alt}
			transition:scale={{ duration: 180, start: 0.97 }}
			on:click|stopPropagation
		/>

		{#if images.length > 1}
			<span class="lb-counter">{activeIndex + 1} / {images.length}</span>
		{/if}
	</div>
{/if}

<style>
	.gallery {
        display: flex;
        flex-direction: column;
        gap: 8px;
        min-width: 0;
    }

    .main {
        position: relative;
        display: block;
        width: 100%;
        min-width: 0;
        cursor: zoom-in;
    }

	.nav {
		position: absolute;
		top: 50%;
		transform: translateY(-50%);
		width: 32px;
		height: 32px;
		display: flex;
		align-items: center;
		justify-content: center;
		border-radius: var(--radius-pill);
		background: rgba(10, 11, 14, 0.55);
		color: #f2efe6;
		font-size: 20px;
		line-height: 1;
		cursor: pointer;
		border: none;
		padding: 0;
		font-family: inherit;
	}

	.nav.prev {
		left: 10px;
	}

	.nav.next {
		right: 10px;
	}

	.counter {
		position: absolute;
		bottom: 10px;
		right: 10px;
		font-family: var(--font-mono);
		font-size: 11px;
		padding: 3px 8px;
		border-radius: var(--radius-pill);
		background: rgba(10, 11, 14, 0.55);
		color: #f2efe6;
	}

	.strip {
		display: flex;
		gap: 8px;
		overflow-x: auto;
		padding-bottom: 2px;
	}

	.thumb-btn {
		flex: 0 0 auto;
		width: 64px;
		height: 48px;
		border-radius: var(--radius-sm);
		overflow: hidden;
		padding: 0;
		border: 2px solid transparent;
		cursor: pointer;
		opacity: 0.6;
		transition:
			opacity var(--dur-fast) var(--ease-soft),
			border-color var(--dur-fast) var(--ease-soft);
	}

	.thumb-btn img {
		width: 100%;
		height: 100%;
		object-fit: cover;
		display: block;
	}

	.thumb-btn:hover {
		opacity: 0.85;
	}

	.thumb-btn.active {
		opacity: 1;
		border-color: var(--color-accent);
	}

	.overlay {
		position: fixed;
		inset: 0;
		z-index: 200;
		background: rgba(6, 7, 9, 0.9);
		display: flex;
		align-items: center;
		justify-content: center;
		padding: 40px;
	}

	.lb-image {
		max-width: 100%;
		max-height: 100%;
		border-radius: var(--radius-sm);
		cursor: default;
	}

	.close {
		position: absolute;
		top: 20px;
		right: 20px;
		width: 36px;
		height: 36px;
		display: flex;
		align-items: center;
		justify-content: center;
		border-radius: var(--radius-pill);
		border: 1px solid rgba(255, 255, 255, 0.25);
		background: rgba(255, 255, 255, 0.08);
		color: #f2efe6;
		cursor: pointer;
	}

	.lb-nav {
		position: absolute;
		top: 50%;
		transform: translateY(-50%);
		width: 44px;
		height: 44px;
		display: flex;
		align-items: center;
		justify-content: center;
		border-radius: var(--radius-pill);
		border: 1px solid rgba(255, 255, 255, 0.25);
		background: rgba(255, 255, 255, 0.08);
		color: #f2efe6;
		font-size: 24px;
		line-height: 1;
		cursor: pointer;
	}

	.lb-prev {
		left: 20px;
	}

	.lb-next {
		right: 20px;
	}

	.lb-counter {
		position: absolute;
		bottom: 20px;
		left: 50%;
		transform: translateX(-50%);
		font-family: var(--font-mono);
		font-size: 12px;
		padding: 4px 10px;
		border-radius: var(--radius-pill);
		background: rgba(255, 255, 255, 0.1);
		color: #f2efe6;
	}
</style>