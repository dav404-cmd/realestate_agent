<script>
	export let src = null;
	export let alt = 'Property photo';

	let loaded = false;
	let errored = false;
</script>

<div class="thumb">
	{#if src && !errored}
		<img
			{src}
			{alt}
			loading="lazy"
			class:loaded
			on:load={() => (loaded = true)}
			on:error={() => (errored = true)}
		/>
		{#if !loaded}
			<div class="skeleton-shimmer" aria-hidden="true"></div>
		{/if}
	{:else}
		<div class="placeholder" aria-hidden="true">
			<svg viewBox="0 0 64 64" width="34" height="34" fill="none">
				<path
					d="M14 54V24l18-12 18 12v30"
					stroke="currentColor"
					stroke-width="2"
					stroke-linejoin="round"
				/>
				<path d="M26 54V38h12v16" stroke="currentColor" stroke-width="2" stroke-linejoin="round" />
				<path d="M20 30h4M40 30h4M20 38h4M40 38h4" stroke="currentColor" stroke-width="2" stroke-linecap="round" />
			</svg>
			<span>No photo yet</span>
		</div>
	{/if}
</div>

<style>
	.thumb {
		position: relative;
		width: 100%;
		aspect-ratio: 4 / 3;
		border-radius: var(--radius-md);
		overflow: hidden;
		background: var(--color-surface-2);
	}

	img {
		width: 100%;
		height: 100%;
		object-fit: cover;
		display: block;
		opacity: 0;
		transition: opacity var(--dur-slow) var(--ease-soft);
	}

	img.loaded {
		opacity: 1;
	}

	.skeleton-shimmer {
		position: absolute;
		inset: 0;
		background: linear-gradient(
			100deg,
			var(--color-surface-2) 30%,
			var(--color-border-soft) 50%,
			var(--color-surface-2) 70%
		);
		background-size: 200% 100%;
		animation: shimmer 1.6s ease-in-out infinite;
	}

	.placeholder {
		width: 100%;
		height: 100%;
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		gap: 6px;
		color: var(--color-text-faint);
		background: repeating-linear-gradient(
			135deg,
			var(--color-surface-2),
			var(--color-surface-2) 10px,
			var(--color-surface) 10px,
			var(--color-surface) 20px
		);
	}

	.placeholder span {
		font-size: 11px;
		letter-spacing: 0.02em;
	}

	@keyframes shimmer {
		0% {
			background-position: 200% 0;
		}
		100% {
			background-position: -200% 0;
		}
	}
</style>
