from __future__ import annotations

import time

import pytest

from phys_pipeline.scheduler import LocalScheduler
from phys_pipeline.types import NodeResources


def test_local_scheduler_runs_jobs():
    scheduler = LocalScheduler(max_workers=2, max_cpu=2)
    handle = scheduler.submit("job1", lambda: 1, NodeResources())
    completed = scheduler.wait_any([handle])
    assert completed.future.result() == 1
    scheduler.shutdown()


def test_local_scheduler_resource_limits():
    scheduler = LocalScheduler(max_workers=2, max_cpu=1)
    start = time.perf_counter()

    def sleep_job():
        time.sleep(0.02)
        return 1

    handle1 = scheduler.submit("job1", sleep_job, NodeResources(cpu=1))
    handle2 = scheduler.submit("job2", sleep_job, NodeResources(cpu=1))
    scheduler.wait_any([handle1, handle2])
    scheduler.wait_any([handle1, handle2])
    elapsed = time.perf_counter() - start
    scheduler.shutdown()

    assert elapsed >= 0.02


def test_local_scheduler_gpu_limit_error():
    scheduler = LocalScheduler(max_workers=1, max_cpu=1, max_gpu=0)
    with pytest.raises(Exception):
        scheduler.submit("job1", lambda: 1, NodeResources(gpu=1))
    scheduler.shutdown()
