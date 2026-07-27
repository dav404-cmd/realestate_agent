import { apiFetch } from './client.js';

/**
 * POST /query/search
 * @param {object} propertyQuery - matches backend PropertyQuery model
 *   { min_price, max_price, target_price, min_size, max_size, zoning,
 *     structure, occupancy, prefecture, city, district, limit, sort_by, sort_order }
 */
export function searchProperties(propertyQuery = {}) {
	return apiFetch('/query/search', { method: 'POST', body: propertyQuery });
}

/**
 * GET /query/property/{property_id}
 * @param {number|string} propertyId
 */
export function getProperty(propertyId) {
	return apiFetch(`/query/property/${propertyId}`);
}

/**
 * GET /query/options/{column_name}
 * @param {string} columnName - e.g. 'prefecture', 'city', 'structure'
 * @returns {Promise<{column_name: string, options: string[]}>}
 */
export function getColumnOptions(columnName) {
	return apiFetch(`/query/options/${encodeURIComponent(columnName)}`);
}
