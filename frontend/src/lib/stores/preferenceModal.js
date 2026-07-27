import { writable } from 'svelte/store';

/**
 * Global open/close state for the preference (profile) modal, so any
 * component — Nav's profile button, the post-login auto-prompt in
 * +layout.svelte, or the "Your Feed" re-prompt — can trigger it without
 * prop-drilling.
 *
 * mode only changes the modal's title text; the form itself is identical
 * either way ('onboarding' right after signup vs 'edit' from the profile
 * button).
 */
function createPreferenceModalStore() {
	const { subscribe, set } = writable({ open: false, mode: 'onboarding' });

	return {
		subscribe,
		openOnboarding: () => set({ open: true, mode: 'onboarding' }),
		openEdit: () => set({ open: true, mode: 'edit' }),
		close: () => set({ open: false, mode: 'onboarding' })
	};
}

export const preferenceModal = createPreferenceModalStore();
