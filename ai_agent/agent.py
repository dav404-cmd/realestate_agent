from ai_agent.agent_runtime import AgentRuntime
from manage_db.db_manager_v1 import DbManagerV1

db = DbManagerV1("jp_realestate_v1")
runtime  = AgentRuntime(db.conn,openrouter=True)

def real_estate_agent(message:str,thread_id:str):
    final_state = runtime.agent.invoke(
        {"user_input": message},
        config={"configurable":{"thread_id":thread_id}})

    return (
        final_state.get("response"),
        final_state.get("extracted_filters", {})
    )

if __name__ == "__main__":
    while True:
        user_input = input("you : ")
        if user_input == "bye":
            break
        response,fillers = real_estate_agent(user_input,"nox_1")
        print(f"ai : {response}")
        print(f"fillers : {fillers}")