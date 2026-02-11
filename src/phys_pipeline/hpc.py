from __future__ import annotations

import itertools
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any


class HpcJobStatus(str, Enum):
    QUEUED = "queued"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


@dataclass(slots=True)
class HpcJob:
    job_id: str
    script_path: Path
    status: HpcJobStatus = HpcJobStatus.QUEUED
    metadata: dict[str, Any] = field(default_factory=dict)


class HpcSchedulerAdapter:
    """Base adapter interface for HPC schedulers."""

    def submit(self, script: str) -> HpcJob:
        raise NotImplementedError

    def poll(self, job: HpcJob) -> HpcJobStatus:
        raise NotImplementedError


class MockHpcScheduler(HpcSchedulerAdapter):
    """In-memory scheduler adapter for tests."""

    def __init__(self, root: Path):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)
        self._counter = itertools.count(1)

    def submit(self, script: str) -> HpcJob:
        job_id = f"mock-{next(self._counter)}"
        script_path = self.root / f"{job_id}.sh"
        script_path.write_text(script, encoding="utf-8")
        return HpcJob(job_id=job_id, script_path=script_path, status=HpcJobStatus.QUEUED)

    def poll(self, job: HpcJob) -> HpcJobStatus:
        if job.status == HpcJobStatus.QUEUED:
            job.status = HpcJobStatus.RUNNING
        elif job.status == HpcJobStatus.RUNNING:
            job.status = HpcJobStatus.SUCCEEDED
        return job.status


class SlurmScheduler(HpcSchedulerAdapter):
    """Minimal Slurm adapter (script generation only)."""

    def __init__(self, root: Path):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)
        self._counter = itertools.count(1)

    def submit(self, script: str) -> HpcJob:
        job_id = f"slurm-{next(self._counter)}"
        script_path = self.root / f"{job_id}.sbatch"
        script_path.write_text(script, encoding="utf-8")
        return HpcJob(job_id=job_id, script_path=script_path, status=HpcJobStatus.QUEUED)

    def poll(self, job: HpcJob) -> HpcJobStatus:
        return job.status


class PbsScheduler(HpcSchedulerAdapter):
    """Minimal PBS adapter (script generation only)."""

    def __init__(self, root: Path):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)
        self._counter = itertools.count(1)

    def submit(self, script: str) -> HpcJob:
        job_id = f"pbs-{next(self._counter)}"
        script_path = self.root / f"{job_id}.pbs"
        script_path.write_text(script, encoding="utf-8")
        return HpcJob(job_id=job_id, script_path=script_path, status=HpcJobStatus.QUEUED)

    def poll(self, job: HpcJob) -> HpcJobStatus:
        return job.status
