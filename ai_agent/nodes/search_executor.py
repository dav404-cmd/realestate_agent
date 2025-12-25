from manage_db.query import PropertyQuery,query_properties
from ai_agent.state import AgentState
from data.data_cleaner.to_json_safe import df_to_json_safe_records

#for test
from ai_agent.llm_wrappers import BytezLLM
from ai_agent.nodes.intent_router import intent_router
from ai_agent.nodes.query_builder import query_builder
from ai_agent.nodes.info_loader import load_profile
from manage_db.db_manager import DbManager
from scraper.japan.realestate.clean_data import make_df_structurally_safe

def search_executor(state:AgentState,df) -> AgentState:
    if not state.extracted_filters:
        state.results = []
        return state
    q = PropertyQuery(**state.extracted_filters)
    state.results = df_to_json_safe_records(query_properties(df,q))
    return state

if __name__ == "__main__":
    state0 = AgentState(
        user_input="i want to buy a house of within 100 mil to 200 mil yen , with wood structure that is vacant",
    )
    llm = BytezLLM("Qwen/Qwen3-4B-Instruct-2507")
    state1 = intent_router(state0,llm)

    db = DbManager(table_name="jp_realestate")
    df = db.load_data()
    df = make_df_structurally_safe(df)

    profile = load_profile(state1,df)
    llm = BytezLLM("Qwen/Qwen3-4B-Instruct-2507")
    state2 = query_builder(profile,llm)

    state3 = search_executor(state2,df)

    print(state3.results)