from manage_db.query import PropertyQuery,query_properties
from ai_agent.state import AgentState
from data.data_cleaner.to_json_safe import df_to_json_safe_records

#for test
from ai_agent.llm_wrappers import BytezLLM
from manage_db.db_manager import DbManager

def make_search_executor(df):
    def search_executor(state:AgentState) -> AgentState:
        if not state.extracted_filters:
            state.results = []
            return state
        q = PropertyQuery(**state.extracted_filters)
        state.results = df_to_json_safe_records(query_properties(df,q))
        return state
    return search_executor

if __name__ == "__main__":
    state0 = AgentState(
        user_input="i want to buy a house of within 100 mil to 200 mil yen , with wood structure that is vacant",
        extracted_filters={'max_price': 200000000, 'min_price': 100000000, 'structure': 'Steel', 'occupancy': 'Vacant'}
    )
    llm = BytezLLM("Qwen/Qwen3-4B-Instruct-2507")

    db = DbManager(table_name="jp_realestate")
    df = db.load_data()


    sercher = make_search_executor(df)
    state1 = sercher(state0)

    print(state1.results)