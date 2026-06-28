import httpx
from typing import Optional, Dict

from genetinav.utils.errors import (
    GeneNotFoundError,
    NetworkUnavailableError,
    ApiRateLimitError,
    SequenceFetchError,
)

class EnsemblClient:
    def __init__(self, base_url: str = "https://rest.ensembl.org", timeout: float = 10.0):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self._client: Optional[httpx.Client] = None

    @property
    def client(self) -> httpx.Client:
        if self._client is None:
            self._client = httpx.Client(timeout=self.timeout)
        return self._client

    def close(self) -> None:
        if self._client is not None:
            self._client.close()
            self._client = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def _handle_exceptions(self, response: httpx.Response, symbol_or_region: str):
        if response.status_code == 404:
            raise GeneNotFoundError(f"No gene found for '{symbol_or_region}'.")
        elif response.status_code == 400:
            raise GeneNotFoundError(f"Bad request or out of bounds for '{symbol_or_region}'.")
        elif response.status_code == 429:
            raise ApiRateLimitError("API rate limit exceeded.")
        elif not response.is_success:
            raise SequenceFetchError(f"API request failed with status code {response.status_code}.")

    def lookup_gene(self, symbol: str, species: str = "human") -> dict:
        url = f"{self.base_url}/lookup/symbol/{species}/{symbol}?content-type=application/json"
        
        try:
            response = self.client.get(url)
        except (httpx.ConnectError, httpx.TimeoutException) as e:
            raise NetworkUnavailableError(f"Network error: {e}") from e

        self._handle_exceptions(response, symbol)

        return response.json()

    def fetch_sequence(self, region: str, species: str = "human") -> str:
        url = f"{self.base_url}/sequence/region/{species}/{region}?content-type=text/plain"
        
        try:
            response = self.client.get(url)
        except (httpx.ConnectError, httpx.TimeoutException) as e:
            raise NetworkUnavailableError(f"Network error: {e}") from e

        self._handle_exceptions(response, region)

        # Strip all whitespace/newlines from the sequence
        return "".join(response.text.split())

    def lookup_gene_by_id(self, gene_id: str) -> dict:
        url = f"{self.base_url}/lookup/id/{gene_id}?expand=1&content-type=application/json"
        
        try:
            response = self.client.get(url)
        except (httpx.ConnectError, httpx.TimeoutException) as e:
            raise NetworkUnavailableError(f"Network error: {e}") from e

        self._handle_exceptions(response, gene_id)

        return response.json()

    def overlap_genes(self, chromosome: str, start: int, end: int, species: str = "human") -> list[dict]:
        """Return a list of genes overlapping the given genomic range.

        Queries ``GET /overlap/region/{species}/{chromosome}:{start}-{end}?feature=gene``
        and returns the raw JSON list (each element has at least ``external_name``,
        ``start``, ``end``, ``strand``, and ``id`` fields).

        Returns an empty list on 404 / out-of-bounds rather than raising.
        """
        url = (
            f"{self.base_url}/overlap/region/{species}/{chromosome}:{start}-{end}"
            f"?feature=gene&content-type=application/json"
        )
        try:
            response = self.client.get(url)
        except (httpx.ConnectError, httpx.TimeoutException) as e:
            raise NetworkUnavailableError(f"Network error: {e}") from e

        if response.status_code == 404 or response.status_code == 400:
            return []
        elif response.status_code == 429:
            raise ApiRateLimitError("API rate limit exceeded.")
        elif not response.is_success:
            raise SequenceFetchError(f"API request failed with status code {response.status_code}.")

        data = response.json()
        # The endpoint returns either a list or an error dict
        if isinstance(data, list):
            return data
        return []

    def fetch_transcript_sequence(self, transcript_id: str, is_cds: bool = False) -> str:
        seq_type = "cds" if is_cds else "cdna"
        url = f"{self.base_url}/sequence/id/{transcript_id}?type={seq_type}&content-type=text/plain"
        
        try:
            response = self.client.get(url)
        except (httpx.ConnectError, httpx.TimeoutException) as e:
            raise NetworkUnavailableError(f"Network error: {e}") from e

        self._handle_exceptions(response, transcript_id)

        # Strip all whitespace/newlines from the sequence
        return "".join(response.text.split())
