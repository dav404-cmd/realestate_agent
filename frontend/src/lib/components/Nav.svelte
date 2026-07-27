<script>
	import { goto } from '$app/navigation';
	import { theme } from '../stores/theme.js';
	import { auth } from '../stores/auth.js';
	import { profile, isPreferenceEmpty } from '../stores/profile.js';
	import { preferenceModal } from '../stores/preferenceModal.js';

	let loggingIn = false;

	function handleLogin() {
		if (loggingIn) return;
		loggingIn = true;
		auth.login();
	}

	function openProfile() {
		preferenceModal.openEdit();
	}

	function handleFeedClick() {
		if ($profile.status !== 'ready' || isPreferenceEmpty($profile.pref)) {
			preferenceModal.openOnboarding();
			return;
		}
		goto('/feed');
	}

	function handleLogout() {
		auth.logout();
	}

	$: isDark = $theme === 'dark';
	$: isAuthed = $auth.status === 'authenticated';
</script>

<header class="nav">
	<div class="container inner">
		<a href="/" class="brand">
			<span class="mark">邸</span>
			<span class="wordmark">Tsubo<em>note</em></span>
		</a>

		<nav class="links">
			<a href="/" class="link">Explore</a>
			{#if isAuthed}
				<button class="link linklike" on:click={handleFeedClick}>Your Feed</button>
				<a href="/agent" class="link">Agent</a>
			{/if}
		</nav>

		<div class="actions">
			<button
				class="theme-toggle"
				aria-label="Toggle color theme"
				on:click={() => theme.toggle()}
				title={isDark ? 'Switch to light' : 'Switch to dark'}
			>
				{#if isDark}
					<svg viewBox="0 0 20 20" width="16" height="16" fill="none" aria-hidden="true">
						<path
							d="M17 10.5A7 7 0 019.5 3a7 7 0 100 14 7 7 0 007.5-6.5z"
							stroke="currentColor"
							stroke-width="1.4"
							stroke-linejoin="round"
						/>
					</svg>
				{:else}
					<svg viewBox="0 0 20 20" width="16" height="16" fill="none" aria-hidden="true">
						<circle cx="10" cy="10" r="4" stroke="currentColor" stroke-width="1.4" />
						<path
							d="M10 2v2M10 16v2M18 10h-2M4 10H2M15.5 4.5l-1.4 1.4M5.9 14.1l-1.4 1.4M15.5 15.5l-1.4-1.4M5.9 5.9L4.5 4.5"
							stroke="currentColor"
							stroke-width="1.4"
							stroke-linecap="round"
						/>
					</svg>
				{/if}
			</button>

			{#if isAuthed}
				<button class="profile-btn" on:click={openProfile} title="Edit your profile">
					<svg viewBox="0 0 20 20" width="15" height="15" fill="none" aria-hidden="true">
						<circle cx="10" cy="7" r="3.2" stroke="currentColor" stroke-width="1.4" />
						<path d="M3.5 17c1.2-3.2 4-4.8 6.5-4.8s5.3 1.6 6.5 4.8" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" />
					</svg>
					{$profile.pref?.user_name ?? 'Profile'}
				</button>
				<button class="signout-btn" on:click={handleLogout} title="Sign out" aria-label="Sign out">
					<svg viewBox="0 0 20 20" width="15" height="15" fill="none" aria-hidden="true">
						<path d="M8 4H5a1 1 0 00-1 1v10a1 1 0 001 1h3M13 14l4-4-4-4M17 10H8" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round" />
					</svg>
				</button>
			{:else}
				<button class="login-btn" on:click={handleLogin} disabled={loggingIn}>
					{loggingIn ? 'Redirecting…' : 'Sign in'}
				</button>
			{/if}
		</div>
	</div>
</header>

<style>
	.nav {
		position: sticky;
		top: 0;
		z-index: 20;
		backdrop-filter: blur(10px);
		background: color-mix(in srgb, var(--color-bg) 82%, transparent);
		border-bottom: 1px solid var(--color-border-soft);
	}

	.inner {
		display: flex;
		align-items: center;
		gap: 24px;
		height: 62px;
	}

	.brand {
		display: flex;
		align-items: center;
		gap: 8px;
	}

	.mark {
		font-family: var(--font-display);
		font-size: 18px;
		width: 30px;
		height: 30px;
		display: flex;
		align-items: center;
		justify-content: center;
		border-radius: var(--radius-sm);
		background: var(--color-accent-bg);
		color: var(--color-accent-strong);
	}

	.wordmark {
		font-family: var(--font-display);
		font-size: 17px;
		letter-spacing: -0.01em;
		color: var(--color-text);
	}

	.wordmark em {
		font-style: normal;
		color: var(--color-text-muted);
	}

	.links {
		display: flex;
		align-items: center;
		gap: 18px;
		flex: 1;
	}

	.link {
		font-size: 13.5px;
		color: var(--color-text-muted);
		transition: color var(--dur-fast) var(--ease-soft);
	}

	.link:hover {
		color: var(--color-text);
	}

	.linklike {
		background: none;
		border: none;
		font-family: inherit;
		cursor: pointer;
		padding: 0;
	}

	.actions {
		display: flex;
		align-items: center;
		gap: 10px;
	}

	.theme-toggle {
		display: flex;
		align-items: center;
		justify-content: center;
		width: 34px;
		height: 34px;
		border-radius: var(--radius-pill);
		border: 1px solid var(--color-border);
		background: var(--color-surface);
		color: var(--color-text-muted);
		cursor: pointer;
		transition:
			color var(--dur-fast) var(--ease-soft),
			border-color var(--dur-fast) var(--ease-soft),
			transform var(--dur-fast) var(--ease-soft);
	}

	.theme-toggle:hover {
		color: var(--color-accent-strong);
		border-color: var(--color-accent);
		transform: rotate(-8deg);
	}

	.login-btn {
		font-size: 13px;
		padding: 8px 16px;
		border-radius: var(--radius-pill);
		border: 1px solid var(--color-border);
		background: var(--color-surface);
		color: var(--color-text);
		cursor: pointer;
		transition:
			border-color var(--dur-fast) var(--ease-soft),
			background var(--dur-fast) var(--ease-soft);
	}

	.login-btn:hover {
		border-color: var(--color-accent);
		background: var(--color-accent-bg);
	}

	.login-btn:disabled {
		opacity: 0.6;
		cursor: default;
		pointer-events: none;
	}

	.profile-btn {
		display: flex;
		align-items: center;
		gap: 7px;
		font-size: 13px;
		padding: 7px 14px 7px 10px;
		border-radius: var(--radius-pill);
		border: 1px solid var(--color-border);
		background: var(--color-surface);
		color: var(--color-text);
		cursor: pointer;
		transition:
			border-color var(--dur-fast) var(--ease-soft),
			background var(--dur-fast) var(--ease-soft);
	}

	.profile-btn:hover {
		border-color: var(--color-accent);
		background: var(--color-accent-bg);
	}

	.signout-btn {
		display: flex;
		align-items: center;
		justify-content: center;
		width: 34px;
		height: 34px;
		border-radius: var(--radius-pill);
		border: 1px solid var(--color-border);
		background: var(--color-surface);
		color: var(--color-text-muted);
		cursor: pointer;
		transition:
			color var(--dur-fast) var(--ease-soft),
			border-color var(--dur-fast) var(--ease-soft);
	}

	.signout-btn:hover {
		color: var(--color-danger);
		border-color: var(--color-danger);
	}
</style>
