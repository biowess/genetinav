import threading
from collections import OrderedDict
from concurrent.futures import ThreadPoolExecutor
from typing import Optional

from genetinav.api_client import EnsemblClient
from genetinav.utils.errors import GeneNotFoundError, NetworkUnavailableError, SequenceFetchError


class ChunkCache:
    def __init__(self, api_client: EnsemblClient, chunk_size: int = 5000, max_chunks: int = 100):
        self.api_client = api_client
        self.chunk_size = chunk_size
        self.max_chunks = max_chunks
        
        self._cache: OrderedDict[tuple[str, str, int], str] = OrderedDict()
        self._lock = threading.Lock()
        self._executor = ThreadPoolExecutor(max_workers=3)
        self._fetching: set[tuple[str, str, int]] = set()
        self._errors: dict[tuple[str, str], Exception] = {}

    def get_chunk_start(self, coord: int) -> int:
        """Ensembl coordinates are 1-indexed. We align to chunk_size boundaries.
        Example for chunk_size=5000:
        coord=1 -> 1
        coord=5000 -> 1
        coord=5001 -> 5001
        """
        return ((coord - 1) // self.chunk_size) * self.chunk_size + 1

    def get_sequence_slice(self, species: str, chromosome: str, start_coord: int, end_coord: int) -> Optional[str]:
        """
        Returns the sequence string if fully cached, else None.
        start_coord and end_coord are absolute 1-indexed coordinates.
        end_coord is inclusive.
        """
        req_chunks = []
        c_start = self.get_chunk_start(start_coord)
        while c_start <= end_coord:
            req_chunks.append(c_start)
            c_start += self.chunk_size
            
        with self._lock:
            for c in req_chunks:
                key = (species, chromosome, c)
                if key not in self._cache:
                    return None
                    
            pieces = []
            for c in req_chunks:
                key = (species, chromosome, c)
                self._cache.move_to_end(key)
                pieces.append(self._cache[key])
                
        full_str = "".join(pieces)
        
        # Calculate offsets into the joined string
        first_chunk_start = req_chunks[0]
        offset_start = start_coord - first_chunk_start
        length = end_coord - start_coord + 1
        
        return full_str[offset_start : offset_start + length]

    def fetch_blocking(self, species: str, chromosome: str, start_coord: int, end_coord: int) -> str:
        """Synchronously fetches missing chunks for the requested range, returns the slice."""
        req_chunks = []
        c_start = self.get_chunk_start(start_coord)
        while c_start <= end_coord:
            req_chunks.append(c_start)
            c_start += self.chunk_size
            
        for c in req_chunks:
            key = (species, chromosome, c)
            with self._lock:
                if key in self._cache:
                    continue
            self._fetch_chunk(species, chromosome, c)
            
        # Clear any recent errors for this species/chrom since we succeeded
        with self._lock:
            self._errors.pop((species, chromosome), None)
            
        res = self.get_sequence_slice(species, chromosome, start_coord, end_coord)
        if res is None:
            # Fallback if something went extremely wrong, shouldn't happen.
            return "N" * (end_coord - start_coord + 1)
        return res

    def prefetch(self, species: str, chromosome: str, start_coord: int, end_coord: int) -> None:
        """Kicks off background fetch for the view and its neighbors."""
        current_c = self.get_chunk_start(start_coord)
        
        chunks_to_fetch = [
            current_c - self.chunk_size,
            current_c,
            current_c + self.chunk_size,
            current_c + 2 * self.chunk_size,
            current_c + 3 * self.chunk_size
        ]
        
        for c in chunks_to_fetch:
            if c < 1:
                continue
            key = (species, chromosome, c)
            with self._lock:
                if key in self._cache or key in self._fetching:
                    continue
                self._fetching.add(key)
                
            self._executor.submit(self._fetch_chunk_bg, species, chromosome, c)

    def _fetch_chunk_bg(self, species: str, chromosome: str, chunk_start: int) -> None:
        try:
            self._fetch_chunk(species, chromosome, chunk_start)
        except Exception as e:
            # Store error so it can be surfaced non-fatally
            with self._lock:
                self._errors[(species, chromosome)] = e
        finally:
            with self._lock:
                self._fetching.discard((species, chromosome, chunk_start))

    def _fetch_chunk(self, species: str, chromosome: str, chunk_start: int) -> None:
        chunk_end = chunk_start + self.chunk_size - 1
        region = f"{chromosome}:{chunk_start}..{chunk_end}"
        try:
            seq = self.api_client.fetch_sequence(region, species=species)
        except GeneNotFoundError:
            # Region is completely out of bounds or missing. Pad entirely with Ns.
            seq = ""
            
        expected_len = self.chunk_size
        if len(seq) < expected_len:
            seq += "N" * (expected_len - len(seq))
            
        with self._lock:
            key = (species, chromosome, chunk_start)
            self._cache[key] = seq
            if len(self._cache) > self.max_chunks:
                self._cache.popitem(last=False)

    def get_latest_error(self, species: str, chromosome: str) -> Optional[Exception]:
        with self._lock:
            return self._errors.get((species, chromosome))

    def get_cached_bytes(self) -> int:
        with self._lock:
            return len(self._cache) * self.chunk_size
