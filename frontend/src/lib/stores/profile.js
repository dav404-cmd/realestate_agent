import { writable } from 'svelte/store';
import { getUserPref, insertUserPref, updateUserPref } from '../api/pref.js';

/**
 * Tracks the logged-in user's Preference row (from user_preference table).
 * Guests never touch this — it's only checked once auth.js resolves to
 * 'authenticated' (see +layout.svelte, which calls profile.check(userId)).
 *
 * status:
 *   'idle'    — nothing checked yet (guest, or not checked)
 *   'loading' — a check() is in flight
 *   'missing' — checked, backend has no Preference row for this user
 *   'ready'   — checked, pref holds the row
 *   'error'   — the check itself failed (network/server error, NOT "no row")
 */
function createProfileStore() {
	const { subscribe, set } = writable({ status: 'idle', pref: null });

	async function check(userId) {
		if (!userId) {
			set({ status: 'idle', pref: null });
			return;
		}
		set({ status: 'loading', pref: null });
		try {
			const data = await getUserPref(userId);
			if (data && data.user_name) {
				set({ status: 'ready', pref: data });
			} else {
				// backend returned something falsy/empty rather than a real row
				set({ status: 'missing', pref: null });
			}
		} catch (err) {
			if (err.status === 404) {
				set({ status: 'missing', pref: null });
			} else {
				set({ status: 'error', pref: null });
			}
		}
	}

	/**
	 * @param {object} pref - full Preference object (must include user_id, user_name)
	 * @param {{isNew: boolean}} opts - isNew=true calls insert_user_pref, else update_user_pref
	 */
	async function save(pref, { isNew }) {
		const saved = isNew ? await insertUserPref(pref) : await updateUserPref(pref);
		set({ status: 'ready', pref: saved && saved.user_name ? saved : pref });
		return saved;
	}

	function reset() {
		set({ status: 'idle', pref: null });
	}

	return { subscribe, check, save, reset };
}

export const profile = createProfileStore();

/**
 * A Preference row can exist (has user_name) but carry no actual filter
 * signal yet — e.g. right after onboarding if the user only typed their
 * name and skipped everything else. "Your Feed" treats that the same as
 * no preference at all and re-prompts.
 */
export function isPreferenceEmpty(pref) {
	if (!pref) return true;
	const ignoreKeys = new Set([
		'user_id',
		'user_name',
		'user_type',
		'preference_weight',
		'custom_pref'
	]);
	return Object.entries(pref).every(
		([key, value]) => ignoreKeys.has(key) || value === null || value === undefined || value === ''
	);
}
