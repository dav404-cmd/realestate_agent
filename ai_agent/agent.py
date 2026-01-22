from ai_agent.agent_runtime import AgentRuntime

runtime  = AgentRuntime(openrouter=False)

def real_estate_agent(message:str,thread_id:str):
    final_state = runtime.agent.invoke(
        {"user_input": message},
        config={"configurable":{"thread_id":thread_id}})

    return final_state["response"]

if __name__ == "__main__":
    while True:
        user_input = input("you : ")
        if user_input == "bye":
            break
        response = real_estate_agent(user_input,"nox_1")
        print(f"ai : {response}")