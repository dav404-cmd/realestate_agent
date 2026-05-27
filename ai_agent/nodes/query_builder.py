from ai_agent.state import AgentState
import json
from manage_db.db_manager_v1 import DbManagerV1

#for test
from ai_agent.llm_wrappers import OpenRouterLLM


db = DbManagerV1(table_name="jp_realestate_v1")


CANONICAL = {
  "zoning": ["Residential", "Commercial"],
  "structure": ["Wood", "Steel Frame","Reinforced Concrete"],
  "occupancy": ["Vacant", "Occupied"]
}

NUMERIC_PROFILE = {
  "price": db.get_numeric_range("price_yen"),
  "size": db.get_json_numeric_range("size")
}

CATEGORICAL_FORMAT = {
    "prefecture" : "Free text, example : tokyo",
}


QUERY_BUILDER_SYSTEM = """
You extract structured property search filters from user input.

You are given a context of valid options and format choose filers in the according format or closest matching option.


Rules:
- Extract only user-stated constraints in natural language form
- Choose the closest matching value from each list.
- If user gives only a minimum or maximum, return the other as null
- If a field is not mentioned, return it as null
- Return ONLY valid JSON
- Do NOT explain


Allowed fields:
- max_price
- min_price
- min_size
- max_size
- zoning
- structure
- occupancy
- prefecture 
"""


def make_query_builder(llm):
    def query_builder(state:AgentState) -> AgentState:

        llm_context = {
                "categorical_limited": CANONICAL,
                "numeric_bounds": NUMERIC_PROFILE,
                "categorical_format" : CATEGORICAL_FORMAT
                }

        user_prompt = f"""
        User Input : {state.user_input}
        Context : {llm_context}"""

        raw = llm.invoke(
            system=QUERY_BUILDER_SYSTEM,
            user=user_prompt
        )
        try:
            raw = raw.strip()

            if raw.startswith("```"):
                raw = raw.replace("```json", "")
                raw = raw.replace("```", "")
                raw = raw.strip()

            state.extracted_filters = json.loads(raw)

        except Exception as e:
            print("RAW:", repr(raw))
            print("ERROR:", e)
            state.extracted_filters = {}

        return state
    return query_builder

if __name__ == "__main__":
    state = AgentState(
        user_input="i want to buy a house of within 100 mil to 200 mil yen , with steel structure that is vacant in Kanagawa,Minato-ku",
        intent="property_search",
    )
    llm = OpenRouterLLM("openrouter/free")

    query_maker = make_query_builder(llm)
    query = query_maker(state)

    print(query.extracted_filters)