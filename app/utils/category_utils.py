import unicodedata

def normalize_category_name(name: str) -> str:
    name = name.strip().casefold()
    name = unicodedata.normalize("NFKD", name)
    name = "".join(
        char for char in name
        if not unicodedata.combining(char)
    )
    return " ".join(name.split())