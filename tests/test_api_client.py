import pytest
import httpx
from unittest.mock import MagicMock

from genetinav.api_client import EnsemblClient
from genetinav.utils.errors import (
    GeneNotFoundError,
    NetworkUnavailableError,
    ApiRateLimitError,
    SequenceFetchError,
)

def test_lookup_gene_success():
    client = EnsemblClient()
    mock_transport = httpx.MockTransport(lambda request: httpx.Response(200, json={"id": "ENSG00000139618", "display_name": "BRCA2"}))
    client._client = httpx.Client(transport=mock_transport)
    
    result = client.lookup_gene("BRCA2")
    assert result == {"id": "ENSG00000139618", "display_name": "BRCA2"}

def test_lookup_gene_404():
    client = EnsemblClient()
    mock_transport = httpx.MockTransport(lambda request: httpx.Response(404, json={"error": "Not found"}))
    client._client = httpx.Client(transport=mock_transport)
    
    with pytest.raises(GeneNotFoundError) as exc:
        client.lookup_gene("UNKNOWN")
    assert "No gene found for 'UNKNOWN'." in str(exc.value)

def test_lookup_gene_429():
    client = EnsemblClient()
    mock_transport = httpx.MockTransport(lambda request: httpx.Response(429, json={"error": "Rate limit"}))
    client._client = httpx.Client(transport=mock_transport)
    
    with pytest.raises(ApiRateLimitError):
        client.lookup_gene("BRCA2")

def test_lookup_gene_network_error():
    client = EnsemblClient()
    def raise_connect_error(request):
        raise httpx.ConnectError("Network is unreachable")
    mock_transport = httpx.MockTransport(raise_connect_error)
    client._client = httpx.Client(transport=mock_transport)
    
    with pytest.raises(NetworkUnavailableError):
        client.lookup_gene("BRCA2")

def test_fetch_sequence_success():
    client = EnsemblClient()
    mock_transport = httpx.MockTransport(lambda request: httpx.Response(200, text="ATGC\nGTCA\n"))
    client._client = httpx.Client(transport=mock_transport)
    
    result = client.fetch_sequence("17:43044295-43125483")
    assert result == "ATGCGTCA"

def test_fetch_sequence_404():
    client = EnsemblClient()
    mock_transport = httpx.MockTransport(lambda request: httpx.Response(404, text="Not found"))
    client._client = httpx.Client(transport=mock_transport)
    
    with pytest.raises(GeneNotFoundError) as exc:
        client.fetch_sequence("17:43044295-43125483")
    assert "No gene found for '17:43044295-43125483'." in str(exc.value)

def test_fetch_sequence_network_error():
    client = EnsemblClient()
    def raise_timeout(request):
        raise httpx.TimeoutException("Timeout")
    mock_transport = httpx.MockTransport(raise_timeout)
    client._client = httpx.Client(transport=mock_transport)
    
    with pytest.raises(NetworkUnavailableError):
        client.fetch_sequence("17:43044295-43125483")

def test_client_context_manager():
    with EnsemblClient() as client:
        assert client._client is None
        # Accessing client property creates the underlying httpx client
        assert isinstance(client.client, httpx.Client)
    
    # Exiting context manager should close and set to None
    assert client._client is None

def test_sequence_fetch_error():
    client = EnsemblClient()
    mock_transport = httpx.MockTransport(lambda request: httpx.Response(500, text="Internal Server Error"))
    client._client = httpx.Client(transport=mock_transport)
    
    with pytest.raises(SequenceFetchError) as exc:
        client.lookup_gene("BRCA2")
    assert "API request failed with status code 500." in str(exc.value)
