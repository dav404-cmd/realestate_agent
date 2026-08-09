from ai_agent.state import AgentState


INTENT_ROUTER_SYSTEM = """
    Classify the user's intent.

    Return ONLY one word:
    - chat
    - property_search
    """

def make_intent_router(llm):
    def intent_router(state:AgentState) -> AgentState:
        result = llm.invoke(
            system=INTENT_ROUTER_SYSTEM,
            user=state.user_input
        ).lower()


        if "property" in result or "house" in result:
            state.intent = "property_search"
        else:
            state.intent = "chat"

        return state
    return intent_router

def route_by_intent(state: AgentState) -> str:
    return state.intent or "chat"
