from ai_agent.state import AgentState
from ai_agent.llm_wrappers import BytezLLM

INTENT_ROUTER_SYSTEM = """
    Classify the user's intent.

    Return ONLY one word:
    - chat
    - property_search
    """

def intent_router(state:AgentState,llm) -> AgentState:
    result = llm.invoke(
        system=INTENT_ROUTER_SYSTEM,
        user=state.user_input
    ).lower()


    if "property" in result or "house" in result:
        state.intent = "property_search"
    else:
        state.intent = "chat"

    return state

if __name__ == "__main__":
    state = AgentState(
        user_input="i want to buy a house",
    )
    llm = BytezLLM("Qwen/Qwen3-4B-Instruct-2507")
    state1 = intent_router(state,llm)
    print(state1)