from ai_agent.state import AgentState
from ai_agent.to_history import get_history

from langchain_core.messages import HumanMessage,AIMessage

RESULT_EXPLAINER_SYSTEM = """
You are a real estate assistant helping users choose the best property.

Rules:
- Only use the provided data.
- If a field is missing, explicitly say it is unknown.
- Always include the property URL when available.
- Do not guess prices, locations, or conditions.
- If results are limited, explain why.

Your goal:
Explain clearly why these properties were selected.
Mention trade-offs and limitations.
Help the user decide.
"""

#todo: Present data in formate with logic
def format_results_for_llm(results):
    formatted = []
    for r in results[:5]:  # limit
        r_data = r.get("data",{})
        formatted.append({
            "id" : r.get("id"),
            "price": r.get("price_yen"),
            "type" : r_data.get("type")  or "Unknown",
            "structure": r_data.get("structure")  or "Unknown",
            "occupancy": r_data.get("occupancy")  or "Unknown",
            "prefecture": r_data.get("prefecture")  or "Unknown",
            "city" : r_data.get("city")  or "Unknown",
            "district" : r_data.get("district")  or "Unknown",
            "layout" : r_data.get("layout")  or "Unknown",
            "land_area": r_data.get("land_area")  or "Unknown",
            "building_area_ratio" : r_data.get("building_area_ratio")  or "Unknown",
            "url": f"https://realestate.co.jp/en/forsale/view/{r.get('source_listing_id')}", #todo: use and test get_url
        })
    return formatted

def make_result_explainer(llm):
    def result_explainer(state:AgentState) -> AgentState:
        history = get_history(state.messages)

        state.messages.append(HumanMessage(content=state.user_input))

        if not state.results:
            reply  = (
                f"I couldn't find any properties matching these filters:\n"
                f"{state.extracted_filters}\n"
                "You may want to relax price, structure, or availability."
            )
            state.response = reply

            state.messages.append(AIMessage(content=reply))

            return state

        clean_results = format_results_for_llm(state.results)

        user_prompt = f"""
        User request: {state.user_input}
        Extracted results : {clean_results}
        """

        reply = llm.invoke(
            user=user_prompt,
            system=RESULT_EXPLAINER_SYSTEM,
            history=history
        )

        state.messages.append(AIMessage(content=reply))

        state.response = reply

        return state
    return result_explainer
