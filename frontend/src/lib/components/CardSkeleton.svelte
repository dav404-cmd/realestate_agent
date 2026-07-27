<div class="skeleton-card" aria-hidden="true">
	<div class="thumb"></div>
	<div class="line w-70"></div>
	<div class="line w-40"></div>
	<div class="row">
		<div class="pill"></div>
		<div class="pill"></div>
	</div>
</div>

<style>
	.skeleton-card {
		background: var(--color-surface);
		border: 1px solid var(--color-border-soft);
		border-radius: var(--radius-lg);
		padding: 10px;
	}

	.thumb {
		aspect-ratio: 4 / 3;
		border-radius: var(--radius-md);
		background: linear-gradient(
			100deg,
			var(--color-surface-2) 30%,
			var(--color-border-soft) 50%,
			var(--color-surface-2) 70%
		);
		background-size: 200% 100%;
		animation: shimmer 1.6s ease-in-out infinite;
	}

	.line {
		height: 11px;
		margin-top: 14px;
		border-radius: var(--radius-sm);
		background: var(--color-surface-2);
	}

	.w-70 {
		width: 70%;
	}
	.w-40 {
		width: 40%;
		margin-top: 8px;
	}

	.row {
		display: flex;
		gap: 6px;
		margin-top: 12px;
	}

	.pill {
		width: 46px;
		height: 18px;
		border-radius: var(--radius-pill);
		background: var(--color-surface-2);
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
