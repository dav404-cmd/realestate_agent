import { apiFetch } from './client.js';
import { PUBLIC_API_BASE } from '$env/static/public';

const BASE_URL = (PUBLIC_API_BASE || 'http://localhost:8000').replace(/\/$/, '');

export function redirectToLogin() {
	window.location.href = BASE_URL + '/auth/login';
}

export async function fetchCurrentUser() {
	try {
		return await apiFetch('/auth/me');
	} catch (err) {
		if (err.status === 401 || err.status === 403) return null;
		throw err;
	}
}

export function signOut() {
	return apiFetch('/auth/logout', { method: 'POST' });
}
