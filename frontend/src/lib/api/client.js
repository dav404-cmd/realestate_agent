import { PUBLIC_API_BASE } from '$env/static/public';

/**
 * Thin fetch wrapper around the FastAPI backend.
 *
 * Kept deliberately dumb: one place to change base URL, credentials mode,
 * error shape, and JSON handling. Endpoint-specific modules (query.js,
 * auth.js, agent.js, pref.js) build on top of this instead of calling
 * fetch() directly, so swapping transport/auth strategy later only touches
 * this file.
 */

const BASE_URL = PUBLIC_API_BASE || 'http://localhost:8000';

export class ApiError extends Error {
	constructor(message, { status, detail } = {}) {
		super(message);
		this.name = 'ApiError';
		this.status = status;
		this.detail = detail;
	}
}

/**
 * @param {string} path - path beginning with '/', e.g. '/query/search'
 * @param {object} [options]
 * @param {string} [options.method]
 * @param {object|null} [options.body]
 * @param {Record<string,string>} [options.params] - query string params (falsy values skipped)
 * @param {AbortSignal} [options.signal]
 */
export async function apiFetch(path, { method = 'GET', body = null, params = null, signal } = {}) {
	const url = new URL(BASE_URL.replace(/\/$/, '') + path);

	if (params) {
		for (const [key, value] of Object.entries(params)) {
			if (value !== undefined && value !== null && value !== '') {
				url.searchParams.set(key, value);
			}
		}
	}

	let res;
	try {
		res = await fetch(url, {
			method,
			credentials: 'include', // backend issues a session cookie via /auth flow
			headers: body ? { 'Content-Type': 'application/json' } : undefined,
			body: body ? JSON.stringify(body) : undefined,
			signal
		});
	} catch (networkErr) {
		throw new ApiError('Could not reach the server. Is the backend running?', {
			status: 0,
			detail: networkErr?.message
		});
	}

	if (!res.ok) {
		let detail = null;
		try {
			detail = await res.json();
		} catch {
			// body wasn't JSON, ignore
		}
		throw new ApiError(detail?.detail || `Request failed (${res.status})`, {
			status: res.status,
			detail
		});
	}

	if (res.status === 204) return null;
	return res.json();
}
