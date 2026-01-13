from langchain_core.messages import HumanMessage, AIMessage

from ai_agent.state import AgentState
from ai_agent.llm_wrappers import BytezLLM
from ai_agent.to_history import get_history
CASUAL_RESPONDER_SYSTEM = """
You are a friendly real estate assistant.
"""

def make_casual_responder(llm):
    def casual_responder(state:AgentState) -> AgentState:
        history = get_history(messages=state.messages)

        reply = llm.invoke(
            system=CASUAL_RESPONDER_SYSTEM,
            user=state.user_input,
            history=history
        )

        state.messages.append(HumanMessage(content=state.user_input))
        state.messages.append(AIMessage(content=reply))

        state.response = reply
        return state
    return casual_responder

if __name__ == "__main__":
    llm = BytezLLM("Qwen/Qwen3-4B-Instruct-2507")
    cr = make_casual_responder(llm)
    state0 = AgentState(user_input="hello should i buy a japanese house currently?")
    state = cr(state0)
    print(state.response)