from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

from genetinav.db import get_connection, get_db_path, initialize_schema


class TestGetDbPath:
    def test_returns_path_in_home_dotgenetinav(self, tmp_path: Path, monkeypatch):
        monkeypatch.setattr("pathlib.Path.home", lambda: tmp_path)
        db_path = get_db_path()
        assert db_path == tmp_path / ".genetinav" / "genetinav.db"
        assert db_path.parent.exists()

    def test_creates_parent_directory(self, tmp_path: Path, monkeypatch):
        monkeypatch.setattr("pathlib.Path.home", lambda: tmp_path)
        get_db_path()
        assert (tmp_path / ".genetinav").is_dir()


class TestGetConnection:
    def test_opens_connection_to_given_path(self, tmp_path: Path):
        db_file = tmp_path / "test.db"
        conn = get_connection(db_file)
        try:
            assert conn is not None
        finally:
            conn.close()

    def test_row_factory_is_row(self, tmp_path: Path):
        db_file = tmp_path / "test.db"
        conn = get_connection(db_file)
        try:
            assert conn.row_factory is sqlite3.Row
        finally:
            conn.close()

    def test_foreign_keys_enabled(self, tmp_path: Path):
        db_file = tmp_path / "test.db"
        conn = get_connection(db_file)
        try:
            row = conn.execute("PRAGMA foreign_keys").fetchone()
            assert row is not None and dict(row)["foreign_keys"] == 1
        finally:
            conn.close()

    def test_creates_db_file_if_missing(self, tmp_path: Path):
        db_file = tmp_path / "test.db"
        conn = get_connection(db_file)
        try:
            assert db_file.exists()
        finally:
            conn.close()

    def test_raises_database_error_on_locked_db(self, monkeypatch, tmp_path: Path):
        """Simulate a locked database by patching sqlite3.connect to raise OperationalError."""
        from genetinav.utils.errors import DatabaseError
        import sqlite3
        
        def mock_connect(*args, **kwargs):
            raise sqlite3.OperationalError("database is locked")
            
        monkeypatch.setattr("sqlite3.connect", mock_connect)
        db_file = tmp_path / "test.db"
        
        with pytest.raises(DatabaseError, match="Unable to open the database. The file may be locked or corrupted."):
            get_connection(db_file)


class TestInitializeSchema:
    def test_creates_all_three_tables(self, tmp_path: Path):
        db_file = tmp_path / "test.db"
        conn = get_connection(db_file)
        try:
            initialize_schema(conn)

            rows = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            ).fetchall()

            table_names = {dict(r)["name"] for r in rows}
            # sqlite_sequence is an internal table created by AUTOINCREMENT
            assert table_names >= {"history", "favorites", "cache"}
        finally:
            conn.close()

    def test_idempotent(self, tmp_path: Path):
        """Running initialize_schema twice must not raise or duplicate tables."""
        db_file = tmp_path / "test.db"
        conn = get_connection(db_file)
        try:
            initialize_schema(conn)
            initialize_schema(conn)

            rows = conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
            table_names = [dict(r)["name"] for r in rows]
            # Must contain exactly our three tables (plus possible sqlite_sequence)
            assert "history" in table_names
            assert "favorites" in table_names
            assert "cache" in table_names
            assert table_names.count("history") == 1
            assert table_names.count("favorites") == 1
            assert table_names.count("cache") == 1
        finally:
            conn.close()

    def test_history_table_columns(self, tmp_path: Path):
        db_file = tmp_path / "test.db"
        conn = get_connection(db_file)
        try:
            initialize_schema(conn)
            cols = conn.execute("PRAGMA table_info(history)").fetchall()
            col_names = {dict(c)["name"] for c in cols}
            assert col_names == {
                "id", "gene_symbol", "species",
                "viewed_at", "coordinates", "window_size", "cached",
            }
        finally:
            conn.close()

    def test_favorites_table_columns(self, tmp_path: Path):
        db_file = tmp_path / "test.db"
        conn = get_connection(db_file)
        try:
            initialize_schema(conn)
            cols = conn.execute("PRAGMA table_info(favorites)").fetchall()
            col_names = {dict(c)["name"] for c in cols}
            assert col_names == {"id", "gene_symbol", "species", "added_at"}
        finally:
            conn.close()

    def test_favorites_unique_constraint(self, tmp_path: Path):
        db_file = tmp_path / "test.db"
        conn = get_connection(db_file)
        try:
            initialize_schema(conn)
            conn.execute(
                "INSERT INTO favorites (gene_symbol, species, added_at) VALUES (?, ?, ?)",
                ("BRCA1", "human", "2026-01-01T00:00:00Z"),
            )
            conn.commit()

            with pytest.raises(sqlite3.IntegrityError):
                conn.execute(
                    "INSERT INTO favorites (gene_symbol, species, added_at) VALUES (?, ?, ?)",
                    ("BRCA1", "human", "2026-01-02T00:00:00Z"),
                )
                conn.commit()
        finally:
            conn.close()

    def test_cache_table_columns(self, tmp_path: Path):
        db_file = tmp_path / "test.db"
        conn = get_connection(db_file)
        try:
            initialize_schema(conn)
            cols = conn.execute("PRAGMA table_info(cache)").fetchall()
            col_names = {dict(c)["name"] for c in cols}
            assert col_names == {"key", "response_data", "created_at", "expires_at"}
        finally:
            conn.close()

    def test_cache_key_is_primary_key(self, tmp_path: Path):
        db_file = tmp_path / "test.db"
        conn = get_connection(db_file)
        try:
            initialize_schema(conn)
            cols = conn.execute("PRAGMA table_info(cache)").fetchall()
            pk_col = [dict(c) for c in cols if dict(c)["pk"] == 1]
            assert len(pk_col) == 1
            assert pk_col[0]["name"] == "key"
        finally:
            conn.close()
