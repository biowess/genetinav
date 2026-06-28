import pytest
from genetinav.navigation_history import NavigationHistory

def test_push_and_back():
    hist = NavigationHistory()
    
    # Push initial
    hist.push("chr1", 100)
    assert hist._current == ("chr1", 100)
    assert len(hist._history) == 0
    
    # Push next
    hist.push("chr1", 500)
    assert hist._current == ("chr1", 500)
    assert len(hist._history) == 1
    
    # Go back
    prev = hist.back("chr1", 500)
    assert prev == ("chr1", 100)
    assert hist._current == ("chr1", 100)
    assert len(hist._future) == 1
    assert hist._future[0] == ("chr1", 500)
    
def test_forward():
    hist = NavigationHistory()
    hist.push("chr1", 100)
    hist.push("chr1", 500)
    hist.push("chr2", 1000)
    
    # User scrolled to chr2, 1050 and then hit back
    prev1 = hist.back("chr2", 1050)
    assert prev1 == ("chr1", 500)
    
    # User hits forward
    next1 = hist.forward("chr1", 500)
    assert next1 == ("chr2", 1050) # It should remember where we actually were
    
def test_push_clears_future():
    hist = NavigationHistory()
    hist.push("chr1", 100)
    hist.push("chr1", 500)
    
    hist.back("chr1", 500)
    assert len(hist._future) == 1
    
    hist.push("chr3", 100)
    assert len(hist._future) == 0

def test_empty_back_forward():
    hist = NavigationHistory()
    assert hist.back("chr1", 100) is None
    assert hist.forward("chr1", 100) is None
