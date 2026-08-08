def distance_cleaner(value):
    if isinstance(value, str):
        value = value.strip()
    if value == "string" or value == 0:
        return None
    else:
        return value