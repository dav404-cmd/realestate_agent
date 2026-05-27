


url_builders = {
    "realestate.co" :
        lambda listing_id: f"https://realestate.co.jp/en/forsale/view/{listing_id}"
}

def get_url(source_listing_id,source):
    build = url_builders.get(source)
    if not build :
        return None
    return build(source_listing_id)