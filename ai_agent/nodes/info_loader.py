from manage_db.query import build_db_profile
from ai_agent.state import AgentState

from manage_db.db_manager import DbManager
def load_profile(state: AgentState, df) -> AgentState:
    state.db_profile = build_db_profile(df)
    return state

if __name__ == "__main__":
    db = DbManager(table_name="jp_realestate")
    df = db.load_data()
    state0 = AgentState(user_input="sf")
    state = load_profile(state0,df)
    print(state)
