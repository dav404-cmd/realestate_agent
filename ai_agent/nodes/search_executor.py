from manage_db.query import PropertyQuery,query_property
from ai_agent.state import AgentState

#for test
from ai_agent.llm_wrappers import OpenRouterLLM
from manage_db.db_manager_v1 import DbManagerV1

def make_search_executor(conn,table_name:str):
    def search_executor(state:AgentState) -> AgentState:
        if not state.extracted_filters:
            state.results = []
            return state
        q = PropertyQuery(**state.extracted_filters)
        state.results = query_property(q, table_name , conn)
        return state
    return search_executor

if __name__ == "__main__":
    state0 = AgentState(
        user_input="i want to buy a house of within 100 mil to 200 mil yen , with wood structure that is vacant",
        extracted_filters={'max_price': 200000000, 'min_price': 100000000, 'structure': 'Wood', 'occupancy': 'Vacant'}
    )
    llm = OpenRouterLLM("openrouter/owl-alpha")#openrouter/free

    db = DbManagerV1(table_name="jp_realestate_v1")
    conn = db.conn


    sercher = make_search_executor(conn,table_name="jp_realestate_v1")
    state1 = sercher(state0)

    print(state1.results)