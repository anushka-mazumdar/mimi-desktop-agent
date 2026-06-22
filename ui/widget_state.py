from enum import Enum
from typing import Callable, List, Optional

class WidgetState(Enum):
    IDLE = "idle"
    INPUT_OPEN = "input_open"
    THINKING = "thinking"
    WORKING = "working"
    SUCCESS = "success"
    ERROR = "error"

class WidgetStateManager:
    def __init__(self, initial_state: WidgetState = WidgetState.IDLE):
        self._state: WidgetState = initial_state
        self._callbacks: List[Callable[[WidgetState], None]] = []

    def get_state(self) -> WidgetState:
        return self._state

    def set_state(self, state: WidgetState) -> None:
        if state == self._state:
            return
        self._state = state
        self._notify_callbacks()

    def register_callback(self, callback: Callable[[WidgetState], None]) -> None:
        if callback not in self._callbacks:
            self._callbacks.append(callback)

    def unregister_callback(self, callback: Callable[[WidgetState], None]) -> None:
        if callback in self._callbacks:
            self._callbacks.remove(callback)

    def _notify_callbacks(self) -> None:
        for callback in self._callbacks:
            callback(self._state)

if __name__ == "__main__":
    def on_state_change(state: WidgetState) -> None:
        print(f"State changed -> {state.value.upper()}")

    manager = WidgetStateManager()
    manager.register_callback(on_state_change)

    manager.set_state(WidgetState.INPUT_OPEN)
    manager.set_state(WidgetState.THINKING)
    manager.set_state(WidgetState.WORKING)
    manager.set_state(WidgetState.SUCCESS)