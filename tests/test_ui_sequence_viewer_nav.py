import pytest
from genetinav.ui_textual.sequence_viewer_controller import SequenceViewerController

def test_controller_initialization():
    seq = "ATGC" * 25 # 100 length
    c = SequenceViewerController(seq, window_start=0, window_size=20, large_step=None)
    assert c.window_start == 0
    assert c.window_size == 20
    assert c.large_step == 20
    assert c.window_end == 20
    assert c.current_window_sequence() == seq[0:20]
    assert c.needs_refresh is False

def test_move_left_right():
    seq = "ATGC" * 25
    c = SequenceViewerController(seq, window_start=10, window_size=20, fine_step=5)
    
    c.move_right()
    assert c.window_start == 15
    assert c.window_end == 35
    
    c.move_left()
    assert c.window_start == 10
    
    # Boundary tests
    c.window_start = 90
    c.move_right()
    # It should clamp to sequence len (100) - window_size (20) = 80
    # Wait, start is 90, so it will shift forward by 5 (95) and then clamp to max_start = 80
    assert c.window_start == 80
    
    c.window_start = 0
    c.move_left()
    assert c.window_start == 0

def test_page_backward_forward():
    seq = "ATGC" * 25
    c = SequenceViewerController(seq, window_start=10, window_size=20, large_step=20)
    
    c.page_forward()
    assert c.window_start == 30
    
    c.page_backward()
    assert c.window_start == 10
    
    c.page_backward()
    assert c.window_start == 0
    
    c.window_start = 75
    c.page_forward()
    assert c.window_start == 80

def test_fine_step():
    seq = "ATGC" * 25
    c = SequenceViewerController(seq, window_start=10, window_size=20, fine_step=10) # fine_step is 10, but method should use 1
    
    c.fine_step_forward()
    assert c.window_start == 11
    
    c.fine_step_backward()
    assert c.window_start == 10

def test_increase_decrease_window():
    seq = "ATGC" * 50 # length 200
    c = SequenceViewerController(seq, window_start=180, window_size=20, min_window_size=10, max_window_size=50)
    
    # Increase window, it should clamp
    c.increase_window(10)
    assert c.window_size == 30
    # If start is 180, size is 30, end is 210, but length is 200, so it clamps start to 170
    assert c.window_start == 170
    
    c.decrease_window(10)
    assert c.window_size == 20
    # decreasing from 170, max_start becomes 180, so 170 is fine
    assert c.window_start == 170
    
    # Increase beyond max
    c.increase_window(100)
    assert c.window_size == 50
    assert c.window_start == 150 # 200 - 50
    
    # Decrease beyond min
    c.decrease_window(100)
    assert c.window_size == 10
    assert c.window_start == 150

def test_refresh_toggle():
    c = SequenceViewerController("ATGC", window_start=0, window_size=10)
    assert c.needs_refresh is False
    c.mark_refresh_requested()
    assert c.needs_refresh is True
    c.acknowledge_refresh()
    assert c.needs_refresh is False

def test_current_window_sequence():
    seq = "ATGC" * 5
    c = SequenceViewerController(seq, window_start=2, window_size=4, min_window_size=1)
    assert c.current_window_sequence() == "GCAT"
    c.move_right() # default fine_step = 1
    assert c.current_window_sequence() == "CATG"

def test_jump_methods():
    seq = "ATGC" * 25
    c = SequenceViewerController(seq, window_start=10, window_size=20)
    
    c.jump_to_start()
    assert c.window_start == 0
    
    c.jump_to_end()
    assert c.window_start == 80  # 100 - 20
    
    c.jump_to_coordinate(50)
    assert c.window_start == 50
    
    # Boundary clamp
    c.jump_to_coordinate(150)
    assert c.window_start == 80

def test_search_and_match_cycling():
    seq = "ATGCTAGCATGCTAGC"  # length 16
    c = SequenceViewerController(seq, window_start=0, window_size=4, min_window_size=1)
    
    c.search("TGC")
    assert c.search_query == "TGC"
    assert c.search_matches == [1, 9]
    
    # Initial start is 0
    c.next_match()
    assert c.window_start == 1
    
    c.next_match()
    assert c.window_start == 9
    
    # Wrap around
    c.next_match()
    assert c.window_start == 1
    
    c.prev_match()
    assert c.window_start == 9
    
    c.prev_match()
    assert c.window_start == 1
    
    # Wrap around
    c.prev_match()
    assert c.window_start == 9

