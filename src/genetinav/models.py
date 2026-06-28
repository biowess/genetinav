from __future__ import annotations

from dataclasses import dataclass, field, fields


@dataclass
class GeneRecord:
    symbol: str
    display_name: str | None
    species: str
    chromosome: str
    start: int
    end: int
    strand: str
    sequence_window_start: int
    sequence_window_end: int
    summary: str | None
    source: str
    fetched_at: str
    sequence: str | None = None
    gene_id: str | None = None
    assembly_name: str | None = None
    def to_dict(self) -> dict:
        return {f.name: getattr(self, f.name) for f in fields(self)}

    @classmethod
    def from_dict(cls, data: dict) -> GeneRecord:
        kwargs = {}
        for f in fields(cls):
            if f.name in data:
                kwargs[f.name] = data[f.name]
        return cls(**kwargs)


@dataclass
class HistoryRecord:
    id: int | None
    gene_symbol: str
    species: str
    viewed_at: str
    coordinates: str
    window_size: int
    cached: bool

    def to_dict(self) -> dict:
        return {f.name: getattr(self, f.name) for f in fields(self)}

    @classmethod
    def from_dict(cls, data: dict) -> HistoryRecord:
        return cls(**{f.name: data[f.name] for f in fields(cls)})


@dataclass
class FavoriteRecord:
    id: int | None
    gene_symbol: str
    species: str
    added_at: str

    def to_dict(self) -> dict:
        return {f.name: getattr(self, f.name) for f in fields(self)}

    @classmethod
    def from_dict(cls, data: dict) -> FavoriteRecord:
        return cls(**{f.name: data[f.name] for f in fields(cls)})


@dataclass
class CacheRecord:
    key: str
    response_data: str
    created_at: str
    expires_at: str | None

    def to_dict(self) -> dict:
        return {f.name: getattr(self, f.name) for f in fields(self)}

    @classmethod
    def from_dict(cls, data: dict) -> CacheRecord:
        return cls(**{f.name: data[f.name] for f in fields(cls)})
