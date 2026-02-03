import numpy as np

from phys_pipeline.pipeline import SequentialPipeline
from phys_pipeline.types import PipelineStage, SimpleState, StageConfig, StageResult


# ---- demo stages used in the test ----
class FreqCfg(StageConfig):
    N: int
    center: float
    span: float


class FreqStage(PipelineStage[SimpleState, FreqCfg]):
    def process(self, state: SimpleState) -> StageResult:
        w = self.cfg.center + np.linspace(-self.cfg.span, self.cfg.span, self.cfg.N)
        st = state.deepcopy()
        st.meta["omega"] = w
        return StageResult(state=st)


class FragCfg(StageConfig):
    a: float = 2.0


class FragStage(PipelineStage[SimpleState, FragCfg]):
    def process(self, state: SimpleState) -> StageResult:
        w = state.meta["omega"]
        phi = self.cfg.a * (w - w.mean()) ** 2
        st = state.deepcopy()
        st.meta["phase/G1"] = phi
        return StageResult(state=st)


class SumStage(PipelineStage[SimpleState, StageConfig]):
    def process(self, state: SimpleState) -> StageResult:
        st = state.deepcopy()
        st.meta["phi_total"] = st.meta["phase/G1"]
        return StageResult(state=st)


class FitCfg(StageConfig):
    degree: int = 2


class FitStage(PipelineStage[SimpleState, FitCfg]):
    def process(self, state: SimpleState) -> StageResult:
        import numpy as np

        w = state.meta["omega"]
        w0 = w.mean()
        x = w - w0
        phi = state.meta["phi_total"]
        coefs = np.polyfit(x, phi, deg=self.cfg.degree)
        P = np.poly1d(coefs)
        GDD = float(np.polyder(P, 2)(0.0))
        TOD = float(np.polyder(P, 3)(0.0))

        # artifact (saved only if --save-artifacts is used)
        def _plot():
            import matplotlib.pyplot as plt

            fig, ax = plt.subplots()
            ax.plot(w, np.unwrap(phi), label="φ(ω)")
            ax.plot(w, P(x), "--", label="poly fit")
            ax.set_xlabel("ω")
            ax.set_ylabel("phase (rad)")
            ax.legend()
            return fig

        st = state.deepcopy()
        st.meta["phase/fit_coefs"] = coefs
        return StageResult(
            state=st,
            metrics={"phase.fit.GDD": GDD, "phase.fit.TOD": TOD},
            artifacts={"phase.fit.plot": _plot},
        )


# ---- the test ----
def test_pipeline_runs(run_pipeline):  # uses the fixture from conftest.py
    st0 = SimpleState(payload=None)
    pipe = SequentialPipeline(
        [
            FreqStage(FreqCfg(name="freq", N=2048, center=0.02, span=1e-3)),
            FragStage(FragCfg(name="frag", a=2.0)),
            SumStage(StageConfig(name="sum")),
            FitStage(FitCfg(name="fit", degree=2)),
        ],
        name="demo",
    )

    out = run_pipeline(pipe, st0)  # this enables artifact saving if flag is set
    assert "demo.fit.phase.fit.GDD" in out.metrics

    # if you ran with --save-artifacts, verify the plot entry exists and print where it was saved
    key = "demo.fit.phase.fit.plot"
    if key in out.artifacts:
        print("ARTIFACT:", out.artifacts[key])  # should be {'figure': 'path/to/png'}
