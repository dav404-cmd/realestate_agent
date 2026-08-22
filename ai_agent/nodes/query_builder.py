from ai_agent.state import AgentState
import json
from manage_db.db_manager_v1 import DbManagerV1
from ai_agent.normalize_query import normalize_value, normalize_location

#for test
from ai_agent.llm_wrappers import OpenRouterLLM,GloqLLM
from utils.logger import get_logger

query_log = get_logger("QueryBuilder","agent")

db = DbManagerV1(table_name="jp_realestate_v1")

CANONICAL = {
  "zoning": [row[0] for row in db.get_options("zoning")],
  "structure": [row[0] for row in db.get_options("structure")],
  "occupancy": [row[0] for row in db.get_options("occupancy")]
}

NUMERIC_PROFILE = {
  "price": db.get_numeric_range("price_yen"),
  "size": db.get_json_numeric_range("size")
}

CATEGORICAL_FORMAT = {
    "prefecture" : "Free text, example : Tokyo",
    "city" : "Free text, example : Kawasaki-shi Asao-ku",
    "district" : "Free text, example : Higashiyurigaoka "
}

LOCATION = ["prefecture","city","district"] #for later
TEXT_BASED_KEYS = ["zoning","structure","occupancy"]

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

Price extraction rules:
- If users specifies a price range (e.g. "between 100M and 200M") use min_price and max_price.
- If users specifies an approximate price (e.g. "around 100M") use target price.
- If the user specifies a maximum budget (e.g. "under 100M", "less than 100M", "up to 100M"), populate max_price only.
- If the user specifies a minimum budget (e.g. "above 100M", "at least 100M"), populate min_price only.
- Never populate target_price together with min_price or max_price.
- If target_price is populated, min_price and max_price must be null.

Allowed fields:
- max_price
- min_price
- target_price
- min_size
- max_size
- zoning
- structure
- occupancy
- prefecture 
- city
- district
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

            json_query = json.loads(raw)
            for key in TEXT_BASED_KEYS:
                json_query[key] = normalize_value(
                    json_query.get(key),
                    CANONICAL[key]
                )

            for key in LOCATION:
                value = json_query.get(key)
                if not value:
                    continue

                result = normalize_location(
                    key = key,
                    value=value,
                    valid_keys= LOCATION,
                    db_conn=db
                )

                if result is None:
                    json_query[key] = None
                    continue

                matched_key, matched_value = result

                if matched_key != key:
                    json_query[key] = None

                json_query[matched_key] = matched_value

            state.extracted_filters = json_query

        except Exception as e:
            query_log.info(f"RAW: {raw}")
            query_log.exception(f"ERROR: {e}")
            state.extracted_filters = {}

        return state
    return query_builder

if __name__ == "__main__":
    state = AgentState(
        user_input="i want to buy a house of around 150 mil , with steel structure that is vacant in Kanagawa,Minato-ku",
        intent="property_search",
    )
    llm = GloqLLM("openai/gpt-oss-120b")

    query_maker = make_query_builder(llm)
    query = query_maker(state)

    print(query.extracted_filters)