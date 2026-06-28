import pytest
import sqlite3
from unittest.mock import MagicMock

from genetinav.api_client import EnsemblClient
from genetinav.cache import CacheManager
from genetinav.history import HistoryManager
from genetinav.gene_service import GeneService

@pytest.fixture
def db_conn():
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    yield conn
    conn.close()

@pytest.fixture
def cache(db_conn):
    return CacheManager(db_conn)

@pytest.fixture
def history(db_conn):
    return HistoryManager(db_conn)

@pytest.fixture
def mock_api_client():
    client = MagicMock(spec=EnsemblClient)
    client.lookup_gene.return_value = {
        "start": 1000,
        "end": 2000,
        "strand": -1,
        "display_name": "TEST_GENE",
        "seq_region_name": "X",
        "description": "Test gene description"
    }
    return client

@pytest.fixture
def gene_service(mock_api_client, cache, history):
    return GeneService(api_client=mock_api_client, cache=cache, history=history)

def test_lookup_cache_miss_and_hit(gene_service, mock_api_client, history):
    # First lookup: cache miss
    record1 = gene_service.lookup("BRCA1", species="human", window_size=100)
    
    assert record1.symbol == "BRCA1"
    assert record1.chromosome == "X"
    assert record1.start == 1000
    assert record1.end == 2000
    assert record1.strand == "-"
    assert record1.sequence_window_start == 1450
    assert record1.sequence_window_end == 1550
    assert record1.summary == "Test gene description"
    
    mock_api_client.lookup_gene.assert_called_once_with("BRCA1", species="human")
    
    history_records = history.list()
    assert len(history_records) == 1
    assert history_records[0].cached is False
    assert history_records[0].gene_symbol == "BRCA1"
    
    mock_api_client.reset_mock()
    
    # Second lookup: cache hit
    record2 = gene_service.lookup("BRCA1", species="human", window_size=100)
    
    assert record2.symbol == "BRCA1"
    assert record2.start == 1000
    mock_api_client.lookup_gene.assert_not_called()
    
    history_records = history.list()
    assert len(history_records) == 2
    assert history_records[0].cached is True  # The most recent is first
    assert history_records[1].cached is False

def test_compute_gc_content(gene_service):
    assert gene_service.compute_gc_content("GCGC") == 100.0
    assert gene_service.compute_gc_content("ATAT") == 0.0
    assert gene_service.compute_gc_content("") == 0.0
    assert gene_service.compute_gc_content("gCcG") == 100.0
    assert gene_service.compute_gc_content("ATGC") == 50.0
    assert gene_service.compute_gc_content("aatgcccggg") == 70.0
