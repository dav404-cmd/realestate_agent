from ai_agent.agent_graph import build_graph
from ai_agent.llm_wrappers import BytezLLM,OpenRouterLLM

from utils.logger import get_logger

llm_log = get_logger("RunTime")

class MultiLLm:
    def __init__(self,models):
        self.models = models

    def invoke(self,**kwargs):
        last_error = None

        for i,model in enumerate(self.models):
            try:
                llm_log.info(f" current model : {model.model}")
                return model.invoke(**kwargs)
            except Exception as e:
                llm_log.warning(
                    f"{model.__class__.__name__} failed."
                    f"Trying fallback ({i + 1}/{len(self.models)}). Error: {e}"
                )
                last_error = e
        raise last_error


class AgentRuntime:
    _conn = None
    _agents = None
    _llm = None

    def __init__(self, conn):

        if AgentRuntime._conn is None:
            AgentRuntime._conn = conn

        if AgentRuntime._llm is None:
            AgentRuntime._llm = MultiLLm([
                OpenRouterLLM("nvidia/nemotron-3-super-120b-a12b:free"),
                OpenRouterLLM("google/gemma-4-31b-it:free"),
                OpenRouterLLM("openrouter/free")
            ])
        if AgentRuntime._agents is None:
            AgentRuntime._agents = build_graph(
                llm = AgentRuntime._llm,
                conn=AgentRuntime._conn,
                table_name="jp_realestate_v1"
            )

        self.llm = AgentRuntime._llm
        self.conn = AgentRuntime._conn
        self.agent = AgentRuntime._agents
