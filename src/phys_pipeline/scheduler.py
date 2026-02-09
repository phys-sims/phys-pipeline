from __future__ import annotations

import itertools
import threading
from collections.abc import Callable, Sequence
from concurrent.futures import Future, ThreadPoolExecutor, wait
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

from .errors import SchedulerError, SchedulerTimeoutError
from .types import NodeResources


@dataclass(slots=True)
class JobHandle:
    job_id: str
    node_id: str
    future: Future[Any]
    resources: NodeResources
    submitted_at: datetime
    attempt: int = 1


class Scheduler:
    """Scheduler interface for DAG execution."""

    def submit(
        self,
        node_id: str,
        fn: Callable[[], Any],
        resources: NodeResources,
        *,
        attempt: int = 1,
    ) -> JobHandle:
        raise NotImplementedError

    def wait_any(self, handles: Sequence[JobHandle], timeout_s: float | None = None) -> JobHandle:
        raise NotImplementedError

    def shutdown(self) -> None:
        raise NotImplementedError


class LocalScheduler(Scheduler):
    """Local thread-based scheduler with simple resource slots."""

    def __init__(self, *, max_workers: int = 4, max_cpu: int = 4, max_gpu: int = 0):
        self._executor = ThreadPoolExecutor(max_workers=max_workers)
        self._max_cpu = max_cpu
        self._max_gpu = max_gpu
        self._available_cpu = max_cpu
        self._available_gpu = max_gpu
        self._cond = threading.Condition()
        self._counter = itertools.count(1)

    def _acquire(self, resources: NodeResources) -> None:
        if resources.cpu > self._max_cpu or resources.gpu > self._max_gpu:
            raise SchedulerError(f"Requested resources exceed scheduler limits: {resources}")
        with self._cond:
            while resources.cpu > self._available_cpu or resources.gpu > self._available_gpu:
                self._cond.wait()
            self._available_cpu -= resources.cpu
            self._available_gpu -= resources.gpu

    def _release(self, resources: NodeResources) -> None:
        with self._cond:
            self._available_cpu += resources.cpu
            self._available_gpu += resources.gpu
            self._cond.notify_all()

    def submit(
        self,
        node_id: str,
        fn: Callable[[], Any],
        resources: NodeResources,
        *,
        attempt: int = 1,
    ) -> JobHandle:
        self._acquire(resources)
        future = self._executor.submit(fn)
        future.add_done_callback(lambda _: self._release(resources))
        job_id = f"local-{next(self._counter)}"
        return JobHandle(
            job_id=job_id,
            node_id=node_id,
            future=future,
            resources=resources,
            submitted_at=datetime.now(UTC),
            attempt=attempt,
        )

    def wait_any(self, handles: Sequence[JobHandle], timeout_s: float | None = None) -> JobHandle:
        futures = {handle.future: handle for handle in handles}
        done, _ = wait(futures.keys(), return_when="FIRST_COMPLETED", timeout=timeout_s)
        if not done:
            raise SchedulerTimeoutError("Scheduler wait timed out.")
        future = next(iter(done))
        return futures[future]

    def shutdown(self) -> None:
        self._executor.shutdown(wait=True)
