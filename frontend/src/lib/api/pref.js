import { apiFetch } from './client.js';

/**
 * Not wired into the UI yet (logged-in only feature, next phase).
 */

/** @param {object} pref - matches backend Preference model */
export function insertUserPref(pref) {
	return apiFetch('/pref/insert_user_pref', { method: 'POST', body: pref });
}

/** @param {object} pref */
export function updateUserPref(pref) {
	return apiFetch('/pref/update_user_pref', { method: 'POST', body: pref });
}

/** @param {string} userId */
export function getUserPref(userId) {
	return apiFetch('/pref/get_pref', { params: { user_id: userId } });
}
