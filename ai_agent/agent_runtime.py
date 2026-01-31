from ai_agent.agent_graph import build_graph
from ai_agent.llm_wrappers import BytezLLM,OpenRouterLLM
from manage_db.db_manager import DbManager

class AgentRuntime:
    _df = None
    _agents = {}

    def __init__(self, openrouter=False):
        if openrouter:
            llm = OpenRouterLLM("deepseek/deepseek-r1-0528:free")
            key = "openrouter"
        else:
            llm = BytezLLM("Qwen/Qwen3-4B-Instruct-2507")
            key = "bytez"

        if AgentRuntime._df is None:
            db = DbManager("jp_realestate")
            AgentRuntime._df = db.load_data()
            db.close_conn()

        if key not in AgentRuntime._agents:
            AgentRuntime._agents[key] = build_graph(
                llm=llm,
                df=AgentRuntime._df
            )

        self.llm = llm
        self.df = AgentRuntime._df
        self.agent = AgentRuntime._agents[key]
