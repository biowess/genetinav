import pytest
from genetinav.command_parser import parse_command

@pytest.mark.parametrize("input_str, expected", [
    ("/settings", ("settings", "", None)),
    ("/search BRCA1", ("search", "BRCA1", None)),
    ("/favorites ", ("favorites", "", None)),
    ("/help   ", ("help", "", None)),
    ("BRCA1", (None, "BRCA1", None)),
    (" tp53 ", (None, "tp53", None)),
    ("", (None, "", None)),
    ("  ", (None, "", None)),
])
def test_parse_command_basic(input_str, expected):
    assert parse_command(input_str) == expected

def test_parse_command_with_valid_commands():
    valid = ["search", "settings", "setup", "favorites", "help"]
    
    # Exact match
    assert parse_command("/settings", valid) == ("settings", "", None)
    
    # Prefix match (single)
    assert parse_command("/sear BRCA1", valid) == ("search", "BRCA1", None)
    
    # Prefix match (ambiguous)
    cmd, args, err = parse_command("/set", valid)
    assert cmd is None
    assert "Ambiguous command. Did you mean:" in err
    assert "/settings" in err
    assert "/setup" in err
    
    # Unknown
    cmd, args, err = parse_command("/foo", valid)
    assert cmd is None
    assert "Unknown command: /foo" in err

