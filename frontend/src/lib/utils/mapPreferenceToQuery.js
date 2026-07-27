/**
 * Preference (user_preference table) and PropertyQuery (/query/search body)
 * are different shapes — Preference has more fields (layout, direction_facing,
 * transaction_type, parking, land area, station info, etc.) than PropertyQuery
 * currently accepts. This only maps the overlapping fields.
 *
 * TODO: once PropertyQuery grows to accept more filters, add the matching
 * line here — e.g. `layout: pref.layout,` — and it'll flow into Your Feed
 * automatically.
 */
export function mapPreferenceToQuery(pref, overrides = {}) {
	const base = pref
		? {
				prefecture: pref.prefecture,
				city: pref.city,
				district: pref.district,
				structure: pref.structure,
				occupancy: pref.occupancy,
				min_price: pref.min_price,
				max_price: pref.max_price,
				target_price: pref.target_price,
				min_size: pref.min_size,
				max_size: pref.max_size
			}
		: {};

	const merged = {
		limit: 24,
		sort_by: 'price_yen',
		sort_order: 'asc',
		...base,
		...overrides
	};

	// drop null/undefined/'' so we don't send empty filters to the backend
	return Object.fromEntries(
		Object.entries(merged).filter(([, v]) => v !== null && v !== undefined && v !== '')
	);
}
