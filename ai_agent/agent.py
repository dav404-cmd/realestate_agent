from ai_agent.agent_runtime import AgentRuntime

runtime  = AgentRuntime(openrouter=True)

def real_estate_agent(message:str,thread_id:str):
    final_state = runtime.agent.invoke(
        {"user_input": message},
        config={"configurable":{"thread_id":thread_id}})

    return final_state["response"]

if __name__ == "__main__":
    user_input = "i want to buy a house of around 15739655 yen , with wood structure that is vacant"
    response = real_estate_agent(user_input,"nox_1")
    print(response)