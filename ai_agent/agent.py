from ai_agent.agent_graph import build_graph
from manage_db.db_manager import DbManager
from ai_agent.llm_wrappers import BytezLLM


def real_estate_agent(message:str):
    llm = BytezLLM("Qwen/Qwen3-4B-Instruct-2507")
    db = DbManager(table_name="jp_realestate")
    df = db.load_data()
    db.close_conn()

    agent = build_graph(llm,df)

    final_state = agent.invoke({
        "user_input": message
    })

    return final_state["response"]

if __name__ == "__main__":
    user_input = "i want to buy a house of around 15739655 yen , with wood structure that is vacant"
    response = real_estate_agent(user_input)
    print(response)