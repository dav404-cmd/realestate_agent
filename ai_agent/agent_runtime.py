from ai_agent.agent_graph import build_graph
from llm_wrappers import BytezLLM,OpenRouterLLM
from manage_db.db_manager import DbManager
class AgentRuntime:
    def __init__(self,openrouter=False):
        if openrouter:
            self.llm = OpenRouterLLM("allenai/molmo-2-8b:free")
        else:
            self.llm = BytezLLM("Qwen/Qwen3-4B-Instruct-2507")
        db = DbManager("jp_realestate")
        self.df = db.load_data()
        db.close_conn()
        self.agent = build_graph(llm = self.llm,df = self.df)