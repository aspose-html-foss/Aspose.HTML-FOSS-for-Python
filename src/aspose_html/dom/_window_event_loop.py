"""Internal event-loop/task-source boundary for Window lifecycle orchestration."""
from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from typing import Callable


@dataclass(slots=True)
class _ScheduledTask:
    source_name: str
    phase: str
    token: object | None
    callback: Callable[[], None]


class WindowEventLoop:
    """Internal task-source scheduler used by ``Window``/``BrowsingContext``.

    Current mode is deterministic and synchronous via :meth:`drain`, but the
    contract keeps scheduling as an explicit boundary so queued/deferred modes
    can be introduced without redesigning callers.
    """

    __slots__ = (
        "_task_sources",
        "_microtask_phases",
        "_queue",
        "_cancelled_tokens",
        "_cleaned_tokens",
        "_active_timers",
        "_timer_task_queue",
        "_next_timer_id",
    )

    def __init__(self) -> None:
        self._task_sources: set[str] = set()
        self._microtask_phases: set[str] = {"microtask-checkpoint"}
        self._queue: deque[_ScheduledTask] = deque()
        self._cancelled_tokens: set[object] = set()
        self._cleaned_tokens: set[object] = set()
        self._active_timers: dict[int, tuple[Callable[..., object], tuple[object, ...], bool]] = {}
        self._timer_task_queue: deque[int] = deque()
        self._next_timer_id: int = 1
        self.register_task_source("microtask")

    def register_task_source(self, source_name: str) -> None:
        if not source_name:
            raise ValueError("source_name must be non-empty")
        self._task_sources.add(source_name)

    def schedule(
        self,
        source_name: str,
        phase: str,
        token: object | None = None,
        callback: Callable[[], None] | None = None,
    ) -> None:
        if source_name not in self._task_sources:
            raise ValueError(f"unregistered task source: {source_name}")
        if source_name == "microtask" and phase not in self._microtask_phases:
            raise ValueError(f"unsupported microtask phase: {phase}")
        if callback is None:
            raise ValueError("callback is required for schedule()")
        self._queue.append(_ScheduledTask(source_name, phase, token, callback))

    def schedule_microtask_checkpoint(
        self,
        callback: Callable[[], None],
        *,
        token: object | None = None,
    ) -> None:
        """Schedule a microtask-checkpoint intent on the event-loop boundary.

        This is a contract seam for future Promise/queueMicrotask behavior.
        It intentionally does not add a runtime microtask engine here.
        """
        self.schedule(
            "microtask",
            "microtask-checkpoint",
            token=token,
            callback=callback,
        )

    def cancel(self, token: object) -> None:
        self._cancelled_tokens.add(token)

    def cleanup(self, token: object) -> None:
        self._cleaned_tokens.add(token)
        self._cancelled_tokens.discard(token)

    def drain(self) -> None:
        while self._queue:
            task = self._queue.popleft()
            if task.token is not None and task.token in self._cancelled_tokens:
                self.cleanup(task.token)
                continue
            task.callback()
            if task.token is not None:
                self.cleanup(task.token)

    def schedule_timer(
        self,
        callback: Callable[..., object],
        args: tuple[object, ...],
        *,
        repeating: bool,
    ) -> int:
        handle = self._next_timer_id
        self._next_timer_id += 1
        self._active_timers[handle] = (callback, args, repeating)
        self._timer_task_queue.append(handle)
        return handle

    def cancel_timer(self, handle: int) -> None:
        self._active_timers.pop(handle, None)

    def clear_timer_work(self) -> None:
        self._active_timers.clear()
        self._timer_task_queue.clear()

    def dispatch_timer_tasks(self, max_tasks: int | None = None) -> int:
        executed = 0
        limit = len(self._timer_task_queue) if max_tasks is None else max(0, max_tasks)

        while self._timer_task_queue and executed < limit:
            handle = self._timer_task_queue.popleft()
            timer = self._active_timers.get(handle)
            if timer is None:
                continue

            callback, args, repeating = timer
            callback(*args)
            executed += 1

            if repeating and handle in self._active_timers:
                self._timer_task_queue.append(handle)
            else:
                self._active_timers.pop(handle, None)

        return executed
