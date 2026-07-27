const URL_BUILDERS = {
	'realestate.co': (listingId) => `https://realestate.co.jp/en/forsale/view/${listingId}`
};

export function getListingUrl(sourceListingId, source) {
	const build = URL_BUILDERS[source];
	if (!build || !sourceListingId) return null;
	return build(sourceListingId);
}