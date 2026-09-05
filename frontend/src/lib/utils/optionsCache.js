import { writable, get } from 'svelte/store';
import { getColumnOptions } from '../api/query.js';

const TTL_MS = 60 * 60 * 1000;

const store = writable({});
const inFlight = new Map();

export const optionsStore = { subscribe: store.subscribe };

export function ensureOptions(column) {
	const state = get(store);
	const entry = state[column];
	if (entry && entry.expiresAt > Date.now() && entry.options.length > 0) {
		return Promise.resolve(entry.options);
	}

	if (inFlight.has(column)) {
		return inFlight.get(column);
	}

	const promise = getColumnOptions(column)
		.then((res) => {
			const options = res.options || [];
			if (options.length > 0) {
				store.update((s) => ({ ...s, [column]: { options, expiresAt: Date.now() + TTL_MS } }));
			}
			inFlight.delete(column);
			return options;
		})
		.catch((err) => {
			inFlight.delete(column);
			throw err;
		});

	inFlight.set(column, promise);
	return promise;
}