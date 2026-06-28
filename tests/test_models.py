from genetinav.models import CacheRecord, FavoriteRecord, GeneRecord, HistoryRecord


class TestGeneRecord:
    def test_round_trip(self) -> None:
        original = GeneRecord(
            symbol="BRCA1",
            display_name="Breast cancer 1",
            species="Homo sapiens",
            chromosome="17",
            start=43044295,
            end=43170245,
            strand="-",
            sequence_window_start=43044295,
            sequence_window_end=43170245,
            summary="DNA repair",
            source="NCBI",
            fetched_at="2026-01-01T00:00:00Z",
        )
        reconstructed = GeneRecord.from_dict(original.to_dict())
        assert reconstructed == original


class TestHistoryRecord:
    def test_round_trip(self) -> None:
        original = HistoryRecord(
            id=1,
            gene_symbol="TP53",
            species="Homo sapiens",
            viewed_at="2026-01-01T00:00:00Z",
            coordinates="17:7668402-7687550",
            window_size=1000,
            cached=True,
        )
        reconstructed = HistoryRecord.from_dict(original.to_dict())
        assert reconstructed == original


class TestFavoriteRecord:
    def test_round_trip(self) -> None:
        original = FavoriteRecord(
            id=42,
            gene_symbol="EGFR",
            species="Homo sapiens",
            added_at="2026-01-01T00:00:00Z",
        )
        reconstructed = FavoriteRecord.from_dict(original.to_dict())
        assert reconstructed == original


class TestCacheRecord:
    def test_round_trip(self) -> None:
        original = CacheRecord(
            key="gene:BRCA1:human",
            response_data='{"symbol": "BRCA1"}',
            created_at="2026-01-01T00:00:00Z",
            expires_at="2026-01-02T00:00:00Z",
        )
        reconstructed = CacheRecord.from_dict(original.to_dict())
        assert reconstructed == original

    def test_round_trip_with_none_expires(self) -> None:
        original = CacheRecord(
            key="gene:TP53:human",
            response_data='{"symbol": "TP53"}',
            created_at="2026-01-01T00:00:00Z",
            expires_at=None,
        )
        reconstructed = CacheRecord.from_dict(original.to_dict())
        assert reconstructed == original
