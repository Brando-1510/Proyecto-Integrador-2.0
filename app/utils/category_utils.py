def normalize_category_name(name: str) -> str:
    return " ".join(name.strip().casefold().split())