from ai_agent.state import AgentState
import json
from manage_db.db_manager import DbManager

#for test
from ai_agent.llm_wrappers import BytezLLM


db = DbManager(table_name="jp_realestate")
df = db.load_data()

CANONICAL = {
  "zoning": ["Residential", "Commercial"],
  "structure": ["Wood", "Steel","Reinforced Concrete"],
  "occupancy": ["Vacant", "Occupied"]
}

NUMERIC_PROFILE = {
  "price": {
    "min": df["price_yen"].min(),
    "max": df["price_yen"].max()
  },
  "size": {
    "min": df["size"].min(),
    "max": df["size"].max()
  }
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
"""


def make_query_builder(llm):
    def query_builder(state:AgentState) -> AgentState:

        llm_context = {
                  "categorical_limited": CANONICAL,
                  "numeric_bounds": NUMERIC_PROFILE,
                    }

        user_prompt = f"""
        User Input : {state.user_input}
        Context : {llm_context}"""

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
    return query_builder

if __name__ == "__main__":
    state = AgentState(
        user_input="i want to buy a house of within 100 mil to 200 mil yen , with steel structure that is vacant",
        intent="property_search",
    )
    llm = BytezLLM("Qwen/Qwen3-4B-Instruct-2507")

    query_maker = make_query_builder(llm)
    query = query_maker(state)

    print(query.extracted_filters)