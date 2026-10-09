"""Application lifecycle state management."""

from enum import Enum, auto

from .exceptions import InvalidLifecycleTransitionError


class RuntimeState(Enum):
    """Finite states of the application runtime."""

    CREATED = auto()
    INITIALIZING = auto()
    CONFIGURED = auto()
    RUNNING = auto()
    STOPPING = auto()
    STOPPED = auto()
    FAILED = auto()


class ApplicationLifecycle:
    """Enforce deterministic runtime state transitions."""

    _TRANSITIONS = {
        RuntimeState.CREATED: {RuntimeState.INITIALIZING, RuntimeState.FAILED},
        RuntimeState.INITIALIZING: {RuntimeState.CONFIGURED, RuntimeState.FAILED},
        RuntimeState.CONFIGURED: {
            RuntimeState.STOPPING,
            RuntimeState.RUNNING,
            RuntimeState.FAILED,
        },
        RuntimeState.RUNNING: {RuntimeState.STOPPING, RuntimeState.FAILED},
        RuntimeState.STOPPING: {RuntimeState.STOPPED, RuntimeState.FAILED},
        RuntimeState.STOPPED: set(),
        RuntimeState.FAILED: set(),
    }

    def __init__(self) -> None:
        """Initialize the lifecycle in the created state."""
        self._state = RuntimeState.CREATED

    @property
    def state(self) -> RuntimeState:
        """Return the current lifecycle state."""
        return self._state

    def transition(self, state: RuntimeState) -> None:
        """Move to a permitted state.

        Args:
            state: The target runtime state.

        Raises:
            InvalidLifecycleTransitionError: If the transition is not permitted.
        """
        if state not in self._TRANSITIONS[self._state]:
            raise InvalidLifecycleTransitionError(
                f"Cannot transition from {self._state.name} to {state.name}."
            )
        self._state = state
