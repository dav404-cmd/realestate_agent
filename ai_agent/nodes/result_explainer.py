from ai_agent.state import AgentState

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

def format_results_for_llm(results):
    formatted = []
    for r in results[:5]:  # limit
        formatted.append({
            "price": r.get("price_yen"),
            "type" : r.get("type"),
            "structure": r.get("structure"),
            "occupancy": r.get("occupancy"),
            "location": r.get("location"),
            "layout" : r.get("layout"),
            "land_area": r.get("land_area"),
            "building_area_ratio" : r.get("building_area_ratio"),
            "url": r.get("url"),
        })
    return formatted

def make_result_explainer(llm):
    def result_explainer(state:AgentState) -> AgentState:
        if not state.results:
            state.response = (
                f"I couldn't find any properties matching these filters:\n"
                f"{state.extracted_filters}\n"
                "You may want to relax price, structure, or availability."
            )
            return state

        clean_results = format_results_for_llm(state.results)

        user_prompt = f"""
        User request: {state.user_input}
        Extracted results : {clean_results}
        """

        state.response = llm.invoke(
            user=user_prompt,
            system=RESULT_EXPLAINER_SYSTEM
        )
        return state
    return result_explainer
