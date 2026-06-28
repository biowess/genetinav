import pytest
from genetinav.utils.validation import (
    normalize_gene_symbol,
    validate_species,
    validate_window_size,
    DEFAULT_ALLOWED_SPECIES,
)

def test_normalize_gene_symbol():
    assert normalize_gene_symbol("brca1") == "BRCA1"
    assert normalize_gene_symbol("Brca1") == "BRCA1"
    assert normalize_gene_symbol(" BRCA1 ") == "BRCA1"
    
    with pytest.raises(ValueError, match="Gene symbol cannot be empty"):
        normalize_gene_symbol("")
    with pytest.raises(ValueError, match="Gene symbol cannot be empty"):
        normalize_gene_symbol("   ")

def test_validate_species():
    # Test valid species (case-insensitive and whitespace)
    assert validate_species("human") == "human"
    assert validate_species("Human ") == "human"
    assert validate_species("  MOUSE  ") == "mouse"
    
    # Test invalid species
    with pytest.raises(ValueError, match="is not allowed"):
        validate_species("dog")
        
    # Test custom allowed list
    custom_allowed = ["dog", "cat"]
    assert validate_species("dog", allowed=custom_allowed) == "dog"
    with pytest.raises(ValueError, match="is not allowed"):
        validate_species("human", allowed=custom_allowed)

def test_validate_window_size():
    # Test valid boundaries and mid-range
    assert validate_window_size(10) == 10
    assert validate_window_size(5000) == 5000
    assert validate_window_size(2500) == 2500
    
    # Test out of bounds
    with pytest.raises(ValueError):
        validate_window_size(9)
    with pytest.raises(ValueError):
        validate_window_size(5001)
        
    # Test non-integer types
    with pytest.raises(ValueError):
        validate_window_size(10.5)
    with pytest.raises(ValueError):
        validate_window_size("10")
    with pytest.raises(ValueError):
        validate_window_size(True)
