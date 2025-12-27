from ai_agent.state import AgentState
from ai_agent.llm_wrappers import BytezLLM

CASUAL_RESPONDER_SYSTEM = """
You are a friendly real estate assistant.
"""

def make_casual_responder(llm):
    def casual_responder(state:AgentState) -> AgentState:
        state.response = llm.invoke(
            system=CASUAL_RESPONDER_SYSTEM,
            user=state.user_input
        )
        return state
    return casual_responder

if __name__ == "__main__":
    llm = BytezLLM("Qwen/Qwen3-4B-Instruct-2507")
    cr = make_casual_responder(llm)
    state0 = AgentState(user_input="hello should i buy a japanese house currently?")
    state = cr(state0)
    print(state.response)