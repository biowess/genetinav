import sqlite3
import pytest

from genetinav.history import HistoryManager


@pytest.fixture
def conn():
    connection = sqlite3.connect(":memory:")
    connection.row_factory = sqlite3.Row
    yield connection
    connection.close()


def test_add_and_list(conn):
    manager = HistoryManager(conn)

    manager.add("BRCA1", "human", "chr17:43044295-43125483", 1000, False)
    manager.add("TP53", "human", "chr17:7668402-7687550", 500, True)

    records = manager.list()
    assert len(records) == 2
    assert records[0].gene_symbol == "TP53"
    assert records[1].gene_symbol == "BRCA1"


def test_list_with_query(conn):
    manager = HistoryManager(conn)

    manager.add("BRCA1", "human", "chr17", 1000, False)
    manager.add("BRCA2", "human", "chr13", 1000, False)
    manager.add("TP53", "human", "chr17", 500, True)

    records = manager.list(query="brca")
    assert len(records) == 2
    symbols = {r.gene_symbol for r in records}
    assert symbols == {"BRCA1", "BRCA2"}


def test_pruning(conn):
    manager = HistoryManager(conn, max_entries=3)

    for i in range(5):
        manager.add(f"GENE{i}", "human", "chr1", 100, False)

    records = manager.list()
    assert len(records) == 3
    assert records[0].gene_symbol == "GENE4"
    assert records[1].gene_symbol == "GENE3"
    assert records[2].gene_symbol == "GENE2"


def test_delete(conn):
    manager = HistoryManager(conn)

    id1 = manager.add("BRCA1", "human", "chr17", 1000, False)
    id2 = manager.add("TP53", "human", "chr17", 500, True)

    manager.delete(id1)

    records = manager.list()
    assert len(records) == 1
    assert records[0].id == id2


def test_clear(conn):
    manager = HistoryManager(conn)

    manager.add("BRCA1", "human", "chr17", 1000, False)
    manager.add("TP53", "human", "chr17", 500, True)

    manager.clear()

    records = manager.list()
    assert len(records) == 0
