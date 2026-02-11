# v2 Usage & Performance Guide

This guide explains how to **maximize phys-pipeline usage** (especially v2 add-ons)
and provides **benchmarks** that quantify performance gains where applicable.

## Maximal usage overview

Use the v2 feature set together to get the most out of phys-pipeline:

1. **Start with typed stages and a sequential baseline.**
   - Use `StageConfig` + `PipelineStage` for deterministic, testable transforms.
   - Run `SequentialPipeline` when the workflow is linear and you want minimal overhead.
2. **Switch to DAG execution for branching or merging workloads.**
   - Model parallel branches and fan-in with `NodeSpec` + `DagExecutor`.
   - Use `DagState` inputs when a node depends on multiple parents.
3. **Enable the scheduler when parallel work exists.**
   - `LocalScheduler` executes nodes concurrently; tune `max_workers` and `max_cpu`
     to match your host resources.
4. **Enable v2 cache keys for repeatable work.**
   - Wrap cache backends with `DagCache` to get DAG-aware cache keys.
   - Pair with deterministic `StageResult` and stable `State.hashable_repr()`.
5. **Scale parameter sweeps with `expand_sweep`.**
   - Use sweeps to generate many node variants while preserving provenance.
   - Combine sweeps with caching and scheduler concurrency to avoid recomputation.
6. **Record artifacts only when needed.**
   - Keep runs light by returning callables for artifacts and enable recording
     when you need outputs for analysis or reporting.
7. **Lean on provenance + metrics.**
   - Store run metadata in metrics/provenance for regression tracking and cache hits.

## Example physics use cases with dummy stages

These are simple, end-to-end patterns that exercise the main features while using
lightweight, deterministic “physics-like” stages:

1. **Baseline linear pipeline (sequential)**
   *Use case:* build confidence in deterministic stage contracts and metrics.
   *Stages:* generate initial state → apply a deterministic transform → record a scalar metric.
   *Why it matters:* confirms `StageConfig` immutability, `StageResult` metrics, and reproducibility.

2. **Branch + merge DAG (fan-out/fan-in)**
   *Use case:* independent physics sub-models that get merged (e.g., two approximations).
   *Stages:* branch into two transforms → merge via `DagState` → compute combined metric.
   *Why it matters:* exercises `NodeSpec` deps and `DagExecutor` ordering.

3. **Parameter sweep (grid search)**
   *Use case:* run a small grid of config values with stable cache keys.
   *Stages:* sweep a node’s config param (e.g., sample resolution) → compute metrics.
   *Why it matters:* tests `expand_sweep`, provenance, and cache hit rates.

4. **Cache reuse across repeated runs**
   *Use case:* simulate repeated experiments with identical configs and inputs.
   *Stages:* run a small DAG twice with `DagCache` enabled.
   *Why it matters:* validates cache key stability and warm-run speedups.

5. **Artifact recording on demand**
   *Use case:* generate plots or derived arrays only when needed.
   *Stages:* return a callable artifact (plot generator) → record only when flagged.
   *Why it matters:* keeps baseline runs lightweight while supporting analysis outputs.

6. **Resource-constrained scheduling**
   *Use case:* enforce limited CPU slots per node to emulate shared compute.
   *Stages:* annotate nodes with `NodeResources` → run with `LocalScheduler`.
   *Why it matters:* tests scheduling and queuing behavior under resource limits.

## Benchmarks: v2 add-ons

### How to reproduce

Run the built-in benchmarks:

```bash
python scripts/benchmarks.py
```

For comparison baselines used below:

```bash
python - <<'PY'
import time
start = time.perf_counter()
for _ in range(8):
    time.sleep(0.01)
print(f"Scheduler baseline (serial sleep): {time.perf_counter()-start:.4f}s")
PY
```

```bash
python - <<'PY'
import time
from phys_pipeline.executor import DagExecutor
from phys_pipeline.pipeline import SequentialPipeline
from phys_pipeline.scheduler import LocalScheduler
from phys_pipeline.types import NodeSpec, PipelineStage, SimpleState, StageConfig, StageResult

class AddConfig(StageConfig):
    amount: int = 1

class AddStage(PipelineStage[SimpleState, AddConfig]):
    def process(self, state: SimpleState, *, policy=None) -> StageResult:
        new_state = state.deepcopy()
        new_state.payload += self.cfg.amount
        return StageResult(state=new_state)

stage = AddStage(AddConfig(amount=1))
seq = SequentialPipeline([stage])

runs = 50

start = time.perf_counter()
for _ in range(runs):
    seq.run(SimpleState(payload=1))
seq_elapsed = time.perf_counter() - start

start = time.perf_counter()
for _ in range(runs):
    nodes = [NodeSpec(id="a", stage=stage)]
    executor = DagExecutor(scheduler=LocalScheduler(max_workers=1, max_cpu=1))
    executor.run(SimpleState(payload=1), nodes)
dag_elapsed = time.perf_counter() - start

print(f"Sequential pipeline ({runs} runs): {seq_elapsed:.4f}s")
print(f"DAG executor ({runs} runs): {dag_elapsed:.4f}s")
PY
```

### Results (captured with Python 3.12.12)

| v2 add-on | Benchmark | Result | Observed impact |
| --- | --- | --- | --- |
| **DAG cache keys** (`DagCache`) | Cold vs warm run | cold=0.0038s, warm=0.0004s | **~9.5× speedup** on cache hit (warm vs cold). |
| **LocalScheduler** (parallel execution) | 8×10ms tasks | parallel=0.0107s, serial=0.0809s | **~7.6× speedup** vs serial baseline. |
| **DAG executor** (single-node overhead) | 50 runs | sequential=0.0015s, DAG=0.0359s | **~24× overhead** for single-node graphs (expected; DAG adds scheduling + provenance). |

**Interpretation**

- **Caching is the biggest win for repeated work**: enable `DagCache` when you rerun the
  same stage inputs/configs.
- **Schedulers pay off when you have real parallelism**: the `LocalScheduler` speedup
  approaches ideal for independent tasks.
- **DAG execution is not free**: for trivial single-node workloads, keep `SequentialPipeline`.
  The DAG path pays off when you have branching, fan-in, or concurrency to exploit.

## Plan: spot and close performance gaps

Use this plan to find weak spots and close them systematically:

1. **Expand the benchmark matrix**
   - Add benchmarks for realistic stage payload sizes (small/medium/large states).
   - Measure scheduler performance under different worker counts and resource contention.
   - Track cache hit ratios and serialization overhead for artifacts.
2. **Add regression thresholds**
   - Record current baseline timings in CI (or a nightly job) and alert on slowdowns.
   - Keep a rolling window of benchmark results to detect drift.
3. **Profile hot paths**
   - Use `cProfile` or `pyinstrument` on DAG runs with large graphs.
   - Focus on hashing, state copying, cache serialization, and scheduler wait loops.
4. **Instrument provenance + metrics**
   - Add timing metrics per stage (opt-in policy flag) to flag slow stages.
   - Log cache hit/miss ratios and average serialization time.
5. **Prioritize fixes by impact**
   - If cache serialization dominates, consider compressed formats or chunked storage.
   - If scheduler overhead dominates, batch nodes or reduce graph granularity.
   - If hashing dominates, shrink `hashable_repr()` payloads and avoid large blobs.

## GIL and multiprocessing considerations

`LocalScheduler` uses a thread pool (`ThreadPoolExecutor`) and **does not bypass the GIL** for
CPU-bound Python code. You will see real speedups when stages are I/O-bound, or when the
work releases the GIL (e.g., NumPy, compiled kernels, or external system calls). For
CPU-bound pure-Python stages, thread-level parallelism is limited by the GIL.

If you need multiprocessing, you can implement a custom `Scheduler` that uses a
`ProcessPoolExecutor` or delegates to an external HPC system. The repo already includes
HPC scheduler adapters (Slurm/PBS script generation) for job submission, but the default
local scheduler is thread-based only.
