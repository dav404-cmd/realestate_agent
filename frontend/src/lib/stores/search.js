import { writable } from 'svelte/store';

/** @typedef {import('../api/query.js')} */

export const defaultFilters = {
	prefecture: '',
	city: '',
	district: '',
	structure: '',
	occupancy: '',
	zoning: '',
	min_price: null,
	max_price: null,
	min_size: null,
	max_size: null,
	limit: 24,
	sort_by: 'price_yen',
	sort_order: 'asc'
};

export const filters = writable({ ...defaultFilters });
export const results = writable([]);
export const searchStatus = writable('idle'); // 'idle' | 'loading' | 'ready' | 'error'
export const searchError = writable(null);
