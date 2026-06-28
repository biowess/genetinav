import json
import threading
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from typing import Callable

from genetinav.api_client import EnsemblClient
from genetinav.cache import CacheManager
from genetinav.chunk_cache import ChunkCache
from genetinav.history import HistoryManager
from genetinav.models import GeneRecord
from genetinav.utils.validation import normalize_gene_symbol, validate_species, validate_window_size

# Granularity of the overlap cache bucket (500 kbp).  Two viewports that fall
# in the same bucket reuse the cached overlap result without a new API call.
_OVERLAP_BUCKET_SIZE = 500_000


class GeneService:
    def __init__(
        self,
        api_client: EnsemblClient,
        cache: CacheManager | None,
        history: HistoryManager | None,
    ):
        self.api_client = api_client
        self.cache = cache
        self.history = history
        self.chunk_cache = ChunkCache(api_client=self.api_client, chunk_size=5000, max_chunks=100)

        # In-memory cache for overlap (gene-at-coords) results.
        # Key: (species, chromosome, bucket) where bucket = coord // _OVERLAP_BUCKET_SIZE
        # Value: list of dicts returned by api_client.overlap_genes(), or None on error
        self._overlap_cache: dict[tuple, list[dict] | None] = {}
        self._overlap_lock = threading.Lock()
        self._overlap_executor = ThreadPoolExecutor(max_workers=2, thread_name_prefix="overlap")
        self._overlap_fetching: set[tuple] = set()

    def lookup(self, raw_symbol: str, species: str = "human", window_size: int = 60) -> GeneRecord:
        symbol = normalize_gene_symbol(raw_symbol)
        species = validate_species(species)
        window_size = validate_window_size(window_size)

        cache_key = f"gene:{species}:{symbol}"
        cached_result = False
        record = None

        if self.cache is not None:
            cached_data = self.cache.get(cache_key)
            if cached_data is not None:
                record = GeneRecord.from_dict(json.loads(cached_data))
                if record.gene_id is not None and record.assembly_name is not None:
                    cached_result = True
                else:
                    # Cache is missing fields (likely from an older version); force a refetch
                    record = None
                    cached_result = False

        if not cached_result:
            api_data = self.api_client.lookup_gene(symbol, species=species)
            
            start = api_data["start"]
            end = api_data["end"]
            midpoint = (start + end) // 2
            half_window = window_size // 2

            strand_val = api_data.get("strand", 1)
            strand = "+" if strand_val == 1 else "-"
            
            record = GeneRecord(
                symbol=symbol,
                display_name=api_data.get("display_name"),
                species=species,
                chromosome=api_data.get("seq_region_name", ""),
                start=start,
                end=end,
                strand=strand,
                sequence_window_start=midpoint - half_window,
                sequence_window_end=midpoint + half_window,
                summary=api_data.get("description"),
                source="Ensembl",
                fetched_at=datetime.now(timezone.utc).isoformat(),
                gene_id=api_data.get("id"),
                assembly_name=api_data.get("assembly_name"),
            )
            
            if self.cache is not None:
                self.cache.set(cache_key, json.dumps(record.to_dict()))

        if self.history is not None:
            coordinates = f"{record.chromosome}:{record.start}-{record.end}"
            self.history.add(
                gene_symbol=record.symbol,
                species=record.species,
                coordinates=coordinates,
                window_size=window_size,
                cached=cached_result
            )

        return record

    def compute_gc_content(self, sequence: str) -> float:
        if not sequence:
            return 0.0
        gc_count = sum(1 for c in sequence if c in "GCgc")
        return round((gc_count / len(sequence)) * 100, 1)

    def fetch_sequence(self, record: GeneRecord) -> str:
        if record.sequence:
            return record.sequence

        region = f"{record.chromosome}:{record.sequence_window_start}..{record.sequence_window_end}"
        sequence = self.api_client.fetch_sequence(region, species=record.species)
        record.sequence = sequence

        if self.cache is not None:
            cache_key = f"gene:{record.species}:{record.symbol}"
            self.cache.set(cache_key, json.dumps(record.to_dict()))

        return sequence

    def get_chunked_sequence(self, species: str, chromosome: str, start: int, end: int) -> str | None:
        return self.chunk_cache.get_sequence_slice(species, chromosome, start, end)

    def fetch_chunked_sequence_blocking(self, species: str, chromosome: str, start: int, end: int) -> str:
        return self.chunk_cache.fetch_blocking(species, chromosome, start, end)

    def prefetch_chunks(self, species: str, chromosome: str, start: int, end: int) -> None:
        self.chunk_cache.prefetch(species, chromosome, start, end)

    def get_prefetch_error(self, species: str, chromosome: str) -> Exception | None:
        return self.chunk_cache.get_latest_error(species, chromosome)

    def get_cached_bytes(self) -> int:
        return self.chunk_cache.get_cached_bytes()

    # ------------------------------------------------------------------
    # Overlap / gene-at-coords helpers
    # ------------------------------------------------------------------

    def _overlap_bucket_key(self, species: str, chromosome: str, coord: int) -> tuple:
        """Return a coarse cache key covering a _OVERLAP_BUCKET_SIZE-wide band."""
        bucket = coord // _OVERLAP_BUCKET_SIZE
        return (species, chromosome, bucket)

    def lookup_gene_at_coords(
        self,
        species: str,
        chromosome: str,
        start: int,
        end: int,
    ) -> list[dict] | None:
        """Return genes overlapping [start, end] from cache, or None if not yet fetched.

        Uses the midpoint of [start, end] for bucket assignment.  If the result
        is not cached yet, kicks off a background prefetch and returns None so
        the caller can display a placeholder immediately.

        Returns:
            list[dict] - zero or more gene dicts (may be empty for intergenic regions)
            None       - data not yet available; background fetch started
        """
        mid = (start + end) // 2
        key = self._overlap_bucket_key(species, chromosome, mid)

        with self._overlap_lock:
            if key in self._overlap_cache:
                return self._overlap_cache[key]
            if key in self._overlap_fetching:
                return None  # fetch already in flight
            self._overlap_fetching.add(key)

        # Kick off background fetch
        bucket_start = (mid // _OVERLAP_BUCKET_SIZE) * _OVERLAP_BUCKET_SIZE
        bucket_end   = bucket_start + _OVERLAP_BUCKET_SIZE - 1
        self._overlap_executor.submit(
            self._fetch_overlap_bg, species, chromosome, bucket_start, bucket_end, key
        )
        return None

    def _fetch_overlap_bg(
        self,
        species: str,
        chromosome: str,
        bucket_start: int,
        bucket_end: int,
        key: tuple,
    ) -> None:
        """Background worker: fetches overlap data and stores it in the cache."""
        try:
            results = self.api_client.overlap_genes(
                chromosome, bucket_start, bucket_end, species=species
            )
        except Exception:
            results = []  # treat errors as intergenic — don't crash the UI
        finally:
            with self._overlap_lock:
                self._overlap_cache[key] = results
                self._overlap_fetching.discard(key)

    def find_gene_at_pos(
        self,
        species: str,
        chromosome: str,
        abs_start: int,
        abs_end: int,
    ) -> dict | None:
        """Return the most prominent gene overlapping [abs_start, abs_end], or None.

        Calls lookup_gene_at_coords(); if the cache is warm returns the best
        match (longest overlap), else returns None (fetch in progress).
        """
        genes = self.lookup_gene_at_coords(species, chromosome, abs_start, abs_end)
        if genes is None:
            return None  # not cached yet
        if not genes:
            return {}   # empty list = confirmed intergenic

        mid = (abs_start + abs_end) // 2
        # Prefer genes that contain the viewport midpoint; otherwise take the
        # one with the largest overlap with the viewport.
        def _overlap(g: dict) -> int:
            return min(g.get("end", 0), abs_end) - max(g.get("start", 0), abs_start)

        containing = [g for g in genes if g.get("start", 0) <= mid <= g.get("end", 0)]
        if containing:
            return max(containing, key=_overlap)
        return max(genes, key=_overlap)

    def get_canonical_transcript(self, gene_id: str) -> str | None:
        if not gene_id:
            return None

        cache_key = f"transcripts:{gene_id}"
        if self.cache is not None:
            cached_data = self.cache.get(cache_key)
            if cached_data is not None:
                return cached_data

        data = self.api_client.lookup_gene_by_id(gene_id)
        transcripts = data.get("Transcript", [])
        if not transcripts:
            return None

        canonical = next((t for t in transcripts if t.get("is_canonical")), transcripts[0])
        t_id = canonical["id"]

        if self.cache is not None:
            self.cache.set(cache_key, t_id)
        return t_id

    def get_transcript_sequence(self, transcript_id: str, is_cds: bool = False) -> str:
        seq_type = "cds" if is_cds else "cdna"
        cache_key = f"seq:{transcript_id}:{seq_type}"
        
        if self.cache is not None:
            cached_data = self.cache.get(cache_key)
            if cached_data is not None:
                return cached_data

        sequence = self.api_client.fetch_transcript_sequence(transcript_id, is_cds=is_cds)
        
        if self.cache is not None:
            self.cache.set(cache_key, sequence)
        return sequence
