import pytest
from genetinav.utils.errors import (
    GenetinavError,
    GeneNotFoundError,
    NetworkUnavailableError,
    ApiRateLimitError,
    InvalidSpeciesError,
    SequenceFetchError,
    CacheError,
    DatabaseError
)

@pytest.mark.parametrize("error_cls, default_suggestion", [
    (GeneNotFoundError, "Check the spelling or try another species."),
    (NetworkUnavailableError, "Check your internet connection."),
    (ApiRateLimitError, "Please wait a moment before trying again."),
    (InvalidSpeciesError, "Ensure the species name is correctly formatted."),
    (SequenceFetchError, "Try fetching a smaller sequence window."),
    (CacheError, "Try clearing the local cache."),
    (DatabaseError, "Ensure the database file is not corrupted or locked.")
])
def test_custom_errors_defaults(error_cls, default_suggestion):
    msg = "Test message"
    error = error_cls(msg)
    
    # Assert string representation is just the message
    assert str(error) == msg
    
    # Assert suggestion is a non-empty string and matches default
    assert isinstance(error.suggestion, str)
    assert len(error.suggestion) > 0
    assert error.suggestion == default_suggestion
    
    # Assert inheritance
    assert isinstance(error, GenetinavError)
    assert isinstance(error, Exception)

@pytest.mark.parametrize("error_cls", [
    GeneNotFoundError,
    NetworkUnavailableError,
    ApiRateLimitError,
    InvalidSpeciesError,
    SequenceFetchError,
    CacheError,
    DatabaseError
])
def test_custom_errors_with_suggestion(error_cls):
    msg = "Test message"
    custom_suggestion = "Custom suggestion."
    error = error_cls(msg, suggestion=custom_suggestion)
    
    assert str(error) == msg
    assert error.suggestion == custom_suggestion

def test_base_error():
    msg = "Base message"
    error = GenetinavError(msg)
    assert str(error) == msg
    assert isinstance(error.suggestion, str)
    assert len(error.suggestion) > 0
    assert isinstance(error, Exception)
