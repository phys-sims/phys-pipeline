from __future__ import annotations

from phys_pipeline.hpc import HpcJobStatus, MockHpcScheduler, PbsScheduler, SlurmScheduler


def test_mock_hpc_scheduler(tmp_path):
    scheduler = MockHpcScheduler(tmp_path)
    job = scheduler.submit("#!/bin/bash\necho hello")
    assert job.status == HpcJobStatus.QUEUED
    assert scheduler.poll(job) in {HpcJobStatus.RUNNING, HpcJobStatus.SUCCEEDED}


def test_slurm_pbs_script_generation(tmp_path):
    slurm = SlurmScheduler(tmp_path)
    pbs = PbsScheduler(tmp_path)
    slurm_job = slurm.submit("#!/bin/bash\necho slurm")
    pbs_job = pbs.submit("#!/bin/bash\necho pbs")
    assert slurm_job.script_path.exists()
    assert pbs_job.script_path.exists()
