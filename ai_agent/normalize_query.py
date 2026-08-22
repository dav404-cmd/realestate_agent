from difflib import get_close_matches

def normalize_value(value: str, valid_values: list[str]):
    if not value:
        return None

    value = value.strip()

    # Exact match
    for valid in valid_values:
        if value.casefold() == valid.casefold():
            return valid

    matches = get_close_matches(
        value,
        valid_values,
        n=1,
        cutoff=0.75
    )

    return matches[0] if matches else None

def normalize_location(key:str ,value:str,valid_keys:list[str],db_conn):
    if not key or not value:
        return None
    check_1 = [row[0] for row in db_conn.get_options(key)]
    match_1 = normalize_value(value,check_1)
    if match_1:
        return key , match_1
    remaining_options = [k for k in valid_keys if k != key]
    for k in remaining_options:
        check = [row[0] for row in db_conn.get_options(k)]
        match = normalize_value(value,check)
        if match:
            return k , match
    return None