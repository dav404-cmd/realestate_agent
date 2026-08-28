import { getColumnOptions } from '../api/query.js';

const TTL_MS = 60 * 60 * 1000;

const cache = new Map();
const inFlight = new Map();

export async function getCachedOptions(column) {
	const entry = cache.get(column);
	if (entry && entry.expiresAt > Date.now()) {
		return entry.options;
	}

	if (inFlight.has(column)) {
		return inFlight.get(column);
	}

	const promise = getColumnOptions(column)
		.then((res) => {
			const options = res.options || [];
			cache.set(column, { options, expiresAt: Date.now() + TTL_MS });
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
