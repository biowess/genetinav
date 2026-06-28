from __future__ import annotations

class NavigationHistory:
    """A back/forward stack of visited (chromosome, window_start) locations."""
    
    def __init__(self):
        # Stack of previous locations
        self._history: list[tuple[str, int]] = []
        # Stack of forward locations
        self._future: list[tuple[str, int]] = []
        # Current location is tracked so that when we push a new location,
        # we can put the *previous* current location onto the history stack.
        self._current: tuple[str, int] | None = None

    def push(self, chromosome: str, window_start: int) -> None:
        """Record a jump to a new location. Clears future history."""
        new_loc = (chromosome, window_start)
        
        if self._current is not None:
            # Don't push if we are exactly at this location already
            if self._current == new_loc:
                return
            self._history.append(self._current)
            
        self._current = new_loc
        self._future.clear()

    def back(self, current_chromosome: str, current_window_start: int) -> tuple[str, int] | None:
        """
        Go back to the previous location. 
        Takes the actual current location in case the user scrolled away from the last pushed location.
        Returns (chromosome, window_start) or None if history is empty.
        """
        if not self._history:
            return None
            
        # Push the actual current location onto future so we can go forward to it
        actual_current = (current_chromosome, current_window_start)
        self._future.append(actual_current)
        
        # Pop the previous location
        prev_loc = self._history.pop()
        self._current = prev_loc
        return prev_loc

    def forward(self, current_chromosome: str, current_window_start: int) -> tuple[str, int] | None:
        """
        Go forward to the next location.
        Returns (chromosome, window_start) or None if future is empty.
        """
        if not self._future:
            return None
            
        # Push the actual current location onto history so we can go back to it
        actual_current = (current_chromosome, current_window_start)
        self._history.append(actual_current)
        
        # Pop the next location
        next_loc = self._future.pop()
        self._current = next_loc
        return next_loc
