def clamp_window(start: int, window_size: int, sequence_length: int) -> tuple[int, int]:
    """
    Given a desired 0-indexed start offset and window_size, returns (start, end) clamped so that
    0 <= start and end <= sequence_length, and end - start == min(window_size, sequence_length).
    """
    if sequence_length <= 0:
        return 0, 0
        
    actual_window_size = min(max(0, window_size), sequence_length)
    
    # Clamp start so that start + actual_window_size <= sequence_length
    max_start = sequence_length - actual_window_size
    
    clamped_start = max(0, min(start, max_start))
    clamped_end = clamped_start + actual_window_size
    
    return clamped_start, clamped_end

def shift_window(start: int, window_size: int, sequence_length: int, offset: int) -> tuple[int, int]:
    """
    Shifts start by offset (positive = forward, negative = backward) and re-clamps via clamp_window.
    """
    return clamp_window(start + offset, window_size, sequence_length)

def base_counts(sequence: str) -> dict[str, int]:
    """
    Returns counts of A, T, G, C (uppercase keys), ignoring/counting any other character under an "N" key, case-insensitive.
    """
    counts = {"A": 0, "T": 0, "G": 0, "C": 0, "N": 0}
    for char in sequence.upper():
        if char in counts and char != "N":
            counts[char] += 1
        else:
            counts["N"] += 1
    return counts

def gc_percentage(sequence: str) -> float:
    """
    Percentage of G/C, 1 decimal, 0.0 for empty string.
    """
    if not sequence:
        return 0.0
        
    sequence = sequence.upper()
    gc_count = sum(1 for char in sequence if char in ("G", "C"))
    percentage = (gc_count / len(sequence)) * 100
    return round(percentage, 1)

def build_ruler(start_coord: int, window_size: int, interval: int) -> list[tuple[int, int]]:
    """
    Returns a list of (offset_within_window, absolute_coordinate) pairs for every position that is a
    multiple of interval within the window, where absolute_coordinate = start_coord + offset.
    """
    if interval <= 0 or window_size <= 0:
        return []
        
    ruler = []
    for offset in range(window_size):
        abs_coord = start_coord + offset
        if abs_coord % interval == 0:
            ruler.append((offset, abs_coord))
            
    return ruler
