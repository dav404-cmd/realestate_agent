from langgraph.graph import StateGraph,END

from ai_agent.nodes.info_loader import make_load_profile
from ai_agent.nodes.intent_router import make_intent_router
from ai_agent.nodes.query_builder import make_query_builder
from ai_agent.nodes.result_explainer import make_result_explainer
from ai_agent.nodes.search_executor import make_search_executor
from ai_agent.state import AgentState


def build_graph(llm,df):
    graph = StateGraph(AgentState)

    graph.add_node("intent",make_intent_router(llm))
    graph.add_node("profile",make_load_profile(df))
    graph.add_node("query",make_query_builder(llm))
    graph.add_node("search",make_search_executor(df))
    graph.add_node("explain",make_result_explainer(llm))

    graph.set_entry_point("intent")

    graph.add_edge("intent","profile")
    graph.add_edge("profile","query")
    graph.add_edge("query","search")
    graph.add_edge("search","explain")
    graph.add_edge("explain",END)

    return graph.compile()
