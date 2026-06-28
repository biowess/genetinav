DEFAULT_ALLOWED_SPECIES = ["human", "mouse", "rat", "zebrafish"]

def normalize_gene_symbol(raw: str) -> str:
    normalized = raw.strip().upper()
    if not normalized:
        raise ValueError("Gene symbol cannot be empty")
    return normalized

def validate_species(species: str, allowed: list[str] | None = None) -> str:
    if allowed is None:
        allowed = DEFAULT_ALLOWED_SPECIES
    
    normalized = species.strip().lower()
    if normalized not in allowed:
        raise ValueError(f"Species '{normalized}' is not allowed. Allowed species are: {', '.join(allowed)}")
    return normalized

def validate_window_size(size: int, minimum: int = 10, maximum: int = 5000) -> int:
    if not isinstance(size, int) or isinstance(size, bool):
        raise ValueError("Window size must be an integer")
    if size < minimum or size > maximum:
        raise ValueError(f"Window size must be between {minimum} and {maximum}")
    return size
