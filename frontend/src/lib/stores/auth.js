import { writable } from 'svelte/store';
import { browser } from '$app/environment';
import { fetchCurrentUser, redirectToLogin, signOut } from '../api/auth.js';
import { profile } from './profile.js';
import { threads } from './threads.js';

function createAuthStore() {
	const { subscribe, set } = writable({
		status: 'loading', // 'loading' | 'guest' | 'authenticated'
		userId: null
	});

	async function init() {
		if (!browser) return;
		const user = await fetchCurrentUser().catch(() => null);
		if (user?.user_id) {
			set({ status: 'authenticated', userId: user.user_id });
		} else {
			set({ status: 'guest', userId: null });
		}
	}

	async function logout() {
		try {
			await signOut();
		} finally {
			profile.reset();
			threads.reset();
			window.location.href = '/';
		}
	}

	return {
		subscribe,
		init,
		login: () => redirectToLogin(),
		logout
	};
}

export const auth = createAuthStore();
