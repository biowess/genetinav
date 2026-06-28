class GenetinavError(Exception):
    def __init__(self, message: str, suggestion: str | None = None):
        super().__init__(message)
        self.message = message
        self.suggestion = suggestion or "A general error occurred."

    def __str__(self):
        return self.message

class GeneNotFoundError(GenetinavError):
    def __init__(self, message: str, suggestion: str | None = None):
        super().__init__(message, suggestion or "Check the spelling or try another species.")

class NetworkUnavailableError(GenetinavError):
    def __init__(self, message: str, suggestion: str | None = None):
        super().__init__(message, suggestion or "Check your internet connection.")

class ApiRateLimitError(GenetinavError):
    def __init__(self, message: str, suggestion: str | None = None):
        super().__init__(message, suggestion or "Please wait a moment before trying again.")

class InvalidSpeciesError(GenetinavError):
    def __init__(self, message: str, suggestion: str | None = None):
        super().__init__(message, suggestion or "Ensure the species name is correctly formatted.")

class SequenceFetchError(GenetinavError):
    def __init__(self, message: str, suggestion: str | None = None):
        super().__init__(message, suggestion or "Try fetching a smaller sequence window.")

class CacheError(GenetinavError):
    def __init__(self, message: str, suggestion: str | None = None):
        super().__init__(message, suggestion or "Try clearing the local cache.")

class DatabaseError(GenetinavError):
    def __init__(self, message: str, suggestion: str | None = None):
        super().__init__(message, suggestion or "Ensure the database file is not corrupted or locked.")
