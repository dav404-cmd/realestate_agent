from ai_agent.agent_runtime import AgentRuntime
from manage_db.db_manager_v1 import DbManagerV1
from manage_db.agent_db_manager import AgentMemory

from dotenv import load_dotenv
import os

load_dotenv()
db = DbManagerV1("jp_realestate_v1")
agent_db = AgentMemory()
runtime  = AgentRuntime(db.conn)

def reduce_state(state):
    results = state.get("results") or []

    result_ids = [
        {"id": r["id"]}
        for r in results
        if r.get("id") is not None
    ]
    return {
        "user_input" : state.get("user_input"),
        "response" : state.get("response"),
        "intent" : state.get("intent"),
        "extracted_filters" : state.get("extracted_filters"),
        "result_ids": result_ids
    }

def real_estate_agent(message:str,thread_id:str):

    print(f"thread : {thread_id}")

    final_state = runtime.agent.invoke(
        {"user_input": message},
        config={"configurable":{"thread_id":thread_id}})

    _id = agent_db.insert_message(thread_id, reduce_state(final_state))

    print(f"stored message for : {_id}")
    return (
        final_state.get("response"),
        final_state.get("extracted_filters", {})
    )

if __name__ == "__main__":

    _thread_id = "0433e51f-6226-484b-b64d-6e01ce61a3cc"

    while True:
        user_input = input("you : ")

        if user_input == "bye":
            break

        if _thread_id is None:
            _thread_id = agent_db.new_thread(user_id=os.getenv("TEST_USER_ID"), title=user_input[:40])

        response,fillers = real_estate_agent(user_input,_thread_id)
        print(f"ai : {response}")
        print(f"fillers : {fillers}")
    agent_db.close_conn()
    db.close_conn()
