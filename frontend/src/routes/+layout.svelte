<script>
	import '../app.css';
	import { onMount } from 'svelte';
	import Nav from '$lib/components/Nav.svelte';
	import PreferenceModal from '$lib/components/PreferenceModal.svelte';
	import { auth } from '$lib/stores/auth.js';
	import { profile } from '$lib/stores/profile.js';
	import { preferenceModal } from '$lib/stores/preferenceModal.js';

	onMount(() => {
		auth.init();
	});

	// Once auth.init() (or a fresh login) resolves to 'authenticated', check
	// whether this user already has a Preference row.
	$: if ($auth.status === 'authenticated' && $profile.status === 'idle') {
		profile.check($auth.userId);
	} else if ($auth.status === 'guest') {
		profile.reset();
	}

	// Auto-prompt exactly once per session, right after that check comes
	// back 'missing' — not on every reactive re-run, so closing the modal
	// (see PreferenceModal's handleClose) doesn't just pop it back open.
	let autoPrompted = false;
	$: if ($profile.status === 'missing' && !autoPrompted) {
		autoPrompted = true;
		preferenceModal.openOnboarding();
	}
</script>

<Nav />

<main>
	<slot />
</main>

<PreferenceModal />

<style>
	main {
		min-height: calc(100vh - 62px);
	}
</style>
