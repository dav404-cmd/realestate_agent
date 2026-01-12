from manage_db.query import build_db_profile
from ai_agent.state import AgentState

from manage_db.db_manager import DbManager
def make_load_profile(df):
    def load_profile(state: AgentState):
        if state.db_profile is None:
            return {
                "db_profile": build_db_profile(df)
            }
        return {}
    return load_profile


if __name__ == "__main__":
    db = DbManager(table_name="jp_realestate")
    df = db.load_data()
    state0 = AgentState(user_input="sf")
    loader = make_load_profile(df)
    state = loader(state0)
    print(state)
