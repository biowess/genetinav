import pytest
from genetinav.sequence import (
    clamp_window,
    shift_window,
    base_counts,
    gc_percentage,
    build_ruler,
)

def test_clamp_window():
    # clamping at the start (negative start)
    assert clamp_window(-5, 10, 100) == (0, 10)
    # clamping at the end (window exceeding sequence length)
    assert clamp_window(95, 10, 100) == (90, 100)
    # window larger than sequence
    assert clamp_window(0, 150, 100) == (0, 100)
    # normal case
    assert clamp_window(50, 10, 100) == (50, 60)
    # zero sequence length
    assert clamp_window(10, 10, 0) == (0, 0)

def test_shift_window():
    # moving forward
    assert shift_window(50, 10, 100, 5) == (55, 65)
    # moving backward
    assert shift_window(50, 10, 100, -5) == (45, 55)
    # backward shift that would go negative
    assert shift_window(2, 10, 100, -5) == (0, 10)
    # forward shift exceeding end
    assert shift_window(90, 10, 100, 15) == (90, 100)

def test_base_counts():
    # mixed sequence including non-ACGT character
    seq = "ATGCatgcNnXyZ"
    counts = base_counts(seq)
    assert counts["A"] == 2
    assert counts["T"] == 2
    assert counts["G"] == 2
    assert counts["C"] == 2
    assert counts["N"] == 5 # N, n, X, y, Z

def test_gc_percentage():
    assert gc_percentage("") == 0.0
    assert gc_percentage("ATGC") == 50.0
    assert gc_percentage("atgc") == 50.0
    assert gc_percentage("GCGC") == 100.0
    assert gc_percentage("ATAT") == 0.0
    assert gc_percentage("ATGCATGC") == 50.0
    # 1 decimal precision
    assert gc_percentage("ATG") == 33.3

def test_build_ruler():
    # producing correct offset/coordinate pairs for a known window and interval
    # start_coord=10, window_size=10, interval=5
    # offsets: 0 (coord 10), 5 (coord 15)
    assert build_ruler(10, 10, 5) == [(0, 10), (5, 15)]
    
    # start_coord=12, window_size=10, interval=5
    # offsets: 3 (coord 15), 8 (coord 20)
    assert build_ruler(12, 10, 5) == [(3, 15), (8, 20)]
