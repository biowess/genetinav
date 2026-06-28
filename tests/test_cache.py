import sqlite3
import time
import pytest
import datetime

from genetinav.cache import CacheManager

@pytest.fixture
def cache_manager():
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    return CacheManager(conn)

def test_set_and_get_no_ttl(cache_manager):
    cache_manager.set("test_key", "test_data")
    assert cache_manager.get("test_key") == "test_data"

def test_set_and_get_with_ttl_expired(cache_manager):
    # Set with 0 ttl
    cache_manager.set("test_key", "test_data", ttl_seconds=0)
    # Sleep to ensure we are strictly past the expiration time
    time.sleep(0.01)
    assert cache_manager.get("test_key") is None

def test_clear(cache_manager):
    cache_manager.set("key1", "data1")
    cache_manager.set("key2", "data2")
    cache_manager.clear()
    assert cache_manager.get("key1") is None
    assert cache_manager.get("key2") is None

def test_delete(cache_manager):
    cache_manager.set("key1", "data1")
    cache_manager.set("key2", "data2")
    cache_manager.delete("key1")
    assert cache_manager.get("key1") is None
    assert cache_manager.get("key2") == "data2"

def test_delete_missing_key(cache_manager):
    # Should not raise an error
    cache_manager.delete("missing_key")
    assert cache_manager.get("missing_key") is None

def test_cache_error_on_sqlite_error(cache_manager):
    from genetinav.utils.errors import CacheError
    import sqlite3
    from unittest.mock import MagicMock
    
    mock_conn = MagicMock()
    mock_conn.execute.side_effect = sqlite3.OperationalError("database is locked")
    cache_manager.conn = mock_conn
    
    with pytest.raises(CacheError, match="Cache read/write failed"):
        cache_manager.get("test_key")
