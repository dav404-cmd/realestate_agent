from ai_agent.state import AgentState
from ai_agent.llm_wrappers import BytezLLM

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


if __name__ == "__main__":
    state = AgentState(
        user_input="i want to buy a house",
    )
    llm = BytezLLM("Qwen/Qwen3-4B-Instruct-2507")
    router = make_intent_router(llm)
    state1 = router(state)
    print(state1.intent)

    answer = route_by_intent(state1)
    print(answer)