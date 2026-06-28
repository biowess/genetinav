"""Command routing and registry for GenetiNav."""
from typing import Callable, Dict, Tuple

# Registry entry: (handler, description, keybinding_shortcut)
CommandRegistry = Dict[str, Tuple[Callable[[], None], str, str]]


class CommandRouter:
    """Dispatches commands to their appropriate handlers.

    The *live* argument accepts any object with ``stop()`` and ``start()``
    methods — used by the Textual app with a ``DummyLive`` stub that is a
    no-op, since Textual manages its own render loop.
    """

    def __init__(self, registry: CommandRegistry, live) -> None:
        self._registry = registry
        self._live = live

    @property
    def registry(self) -> CommandRegistry:
        """Access the command registry."""
        return self._registry

    def dispatch(self, command: str) -> None:
        handler_info = self._registry.get(command)
        if handler_info:
            handler = handler_info[0]
            self._live.stop()
            try:
                handler()
            finally:
                self._live.start()
