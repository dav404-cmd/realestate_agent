from ai_agent.state import AgentState
import json

#for test
from ai_agent.llm_wrappers import BytezLLM
from ai_agent.nodes.info_loader import load_profile
from manage_db.db_manager import DbManager
from scraper.japan.realestate.clean_data import make_df_structurally_safe

QUERY_BUILDER_SYSTEM = """
You extract structured property search filters from user input.

You are given a database profile describing valid columns, ranges,
and example categorical values.


Rules:
- Extract ONLY what the user EXPLICITLY says
- DO NOT infer, guess, or expand ranges
- If user gives only a minimum or maximum, return the other as null
- Use values exactly as spoken if possible
- Return ONLY valid JSON
- Use null if information is missing
- Do NOT explain


Allowed fields:
- structure
- max_price
- min_price
- min_size
- max_size
- zoning
- property_type
- occupancy
"""

def query_builder(state:AgentState,llm) -> AgentState:
    if not state.db_profile:
        state.extracted_filters = {}
        return state

    user_prompt = f"""
    User Input : {state.user_input}
    Database profile : {json.dumps(state.db_profile,indent=2)}"""

    raw = llm.invoke(
        system=QUERY_BUILDER_SYSTEM,
        user=user_prompt
    )

    try:
        state.extracted_filters = json.loads(raw)
    except json.JSONDecodeError as e:
        print(f"JSON parse error: {e}")
        state.extracted_filters = {}

    return state

if __name__ == "__main__":
    db = DbManager(table_name="jp_realestate")
    df = db.load_data()
    df = make_df_structurally_safe(df)
    state = AgentState(
        user_input="i want to buy a house of within 100 mil to 200 mil yen , with steel structure that is vacant",
        intent="property_search",
    )
    profile = load_profile(state,df)
    llm = BytezLLM("Qwen/Qwen3-4B-Instruct-2507")
    state1 = query_builder(profile,llm)
    print(state1.extracted_filters)