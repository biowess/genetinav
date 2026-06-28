import sqlite3
import pytest
import time

from genetinav.favorites import FavoritesManager
from genetinav.models import FavoriteRecord

@pytest.fixture
def conn():
    connection = sqlite3.connect(":memory:")
    connection.row_factory = sqlite3.Row
    yield connection
    connection.close()

@pytest.fixture
def manager(conn):
    return FavoritesManager(conn)

def test_add_and_is_favorite(manager):
    assert not manager.is_favorite("BRCA1", "homo_sapiens")
    fav_id = manager.add("BRCA1", "homo_sapiens")
    assert manager.is_favorite("BRCA1", "homo_sapiens")
    assert isinstance(fav_id, int)

def test_add_duplicate(manager):
    id1 = manager.add("TP53", "homo_sapiens")
    id2 = manager.add("TP53", "homo_sapiens")
    assert id1 == id2
    
    favorites = manager.list()
    assert len(favorites) == 1

def test_remove(manager):
    manager.add("EGFR", "homo_sapiens")
    assert manager.is_favorite("EGFR", "homo_sapiens")
    
    manager.remove("EGFR", "homo_sapiens")
    assert not manager.is_favorite("EGFR", "homo_sapiens")
    
    manager.remove("EGFR", "homo_sapiens")

def test_list_order(manager):
    manager.add("ZNF12", "homo_sapiens")
    time.sleep(0.01)
    manager.add("A1BG", "homo_sapiens")
    time.sleep(0.01)
    manager.add("MTOR", "homo_sapiens")
    
    alpha_favs = manager.list(order="alpha")
    assert [f.gene_symbol for f in alpha_favs] == ["A1BG", "MTOR", "ZNF12"]
    
    recent_favs = manager.list(order="recent")
    assert [f.gene_symbol for f in recent_favs] == ["MTOR", "A1BG", "ZNF12"]

def test_invalid_order(manager):
    with pytest.raises(ValueError):
        manager.list(order="invalid")
