from ai_agent.agent_graph import build_graph
from ai_agent.llm_wrappers import BytezLLM,OpenRouterLLM
from manage_db.db_manager_v1 import DbManagerV1

class AgentRuntime:
    _conn = None
    _agents = {}

    def __init__(self, openrouter=False):
        if openrouter:
            llm = OpenRouterLLM("openrouter/owl-alpha")
            key = "openrouter"
        else:
            llm = BytezLLM("Qwen/Qwen3-4B-Instruct-2507")
            key = "bytez"

        if AgentRuntime._conn is None:
            db = DbManagerV1("jp_realestate_v1")
            AgentRuntime._conn = db.conn

        if key not in AgentRuntime._agents:
            AgentRuntime._agents[key] = build_graph(
                llm=llm,
                conn= AgentRuntime._conn,
                table_name = "jp_realestate_v1"
            )

        self.llm = llm
        self.conn = AgentRuntime._conn
        self.agent = AgentRuntime._agents[key]
