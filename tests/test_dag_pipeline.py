from phys_pipeline.pipeline import DagPipeline
from phys_pipeline.scheduler import TopoScheduler
from phys_pipeline.types import Dag, PipelineStage, SimpleState, StageConfig, StageResult


class AddConfig(StageConfig):
    amount: int = 1


class AddStage(PipelineStage[SimpleState, AddConfig]):
    def process(self, state: SimpleState, *, policy=None) -> StageResult:
        st = state.deepcopy()
        st.payload = (st.payload or 0) + self.cfg.amount
        return StageResult(state=st)


def test_dag_topo_order_is_deterministic():
    dag = Dag(
        nodes={
            "b": AddStage(AddConfig(amount=1)),
            "a": AddStage(AddConfig(amount=1)),
            "c": AddStage(AddConfig(amount=1)),
        },
        deps={"c": {"a", "b"}},
    )
    assert dag.topo_order() == ["a", "b", "c"]


def test_dag_pipeline_runs_in_topo_order():
    dag = Dag(
        nodes={
            "first": AddStage(AddConfig(amount=1)),
            "second": AddStage(AddConfig(amount=1)),
            "third": AddStage(AddConfig(amount=1)),
        },
        deps={"second": {"first"}, "third": {"second"}},
    )
    pipeline = DagPipeline(dag, name="demo", scheduler=TopoScheduler())
    result = pipeline.run(SimpleState(payload=0))
    assert result.state.payload == 3
