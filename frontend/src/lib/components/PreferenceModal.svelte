<script>
	import Modal from './Modal.svelte';
	import PreferenceForm from './PreferenceForm.svelte';
	import { preferenceModal } from '../stores/preferenceModal.js';
	import { profile } from '../stores/profile.js';
	import { auth } from '../stores/auth.js';

	let saving = false;
	let error = null;

	$: isNew = $profile.status !== 'ready';
	$: title =
		$preferenceModal.mode === 'onboarding' ? 'Welcome — tell us a bit about you' : 'Edit your profile';

	async function handleSubmit(e) {
		saving = true;
		error = null;
		try {
			await profile.save({ ...e.detail, user_id: $auth.userId }, { isNew });
			preferenceModal.close();
		} catch (err) {
			error = err.message || 'Could not save your preferences. Please try again.';
		} finally {
			saving = false;
		}
	}

	function handleClose() {
		// Per spec: closing does nothing but close — no navigation, no retry loop.
		error = null;
		preferenceModal.close();
	}
</script>

{#if $preferenceModal.open}
	<Modal {title} on:close={handleClose}>
		<PreferenceForm
			initial={$profile.pref}
			submitLabel="Save"
			{saving}
			on:submit={handleSubmit}
			on:cancel={handleClose}
		/>
		{#if error}<p class="error">{error}</p>{/if}
	</Modal>
{/if}

<style>
	.error {
		margin-top: 12px;
		font-size: 13px;
		color: var(--color-danger);
	}
</style>
