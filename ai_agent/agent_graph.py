from langgraph.graph import StateGraph,END
from langgraph.checkpoint.memory import MemorySaver

from ai_agent.nodes.casual_responder import make_casual_responder
from ai_agent.nodes.info_loader import make_load_profile
from ai_agent.nodes.intent_router import make_intent_router,route_by_intent
from ai_agent.nodes.query_builder import make_query_builder
from ai_agent.nodes.result_explainer import make_result_explainer
from ai_agent.nodes.search_executor import make_search_executor
from ai_agent.state import AgentState


def build_graph(llm,df):
    graph = StateGraph(AgentState)

    graph.add_node("intent",make_intent_router(llm))
    graph.add_node("casual",make_casual_responder(llm))
    graph.add_node("profile",make_load_profile(df))
    graph.add_node("query",make_query_builder(llm))
    graph.add_node("search",make_search_executor(df))
    graph.add_node("explain",make_result_explainer(llm))

    graph.set_entry_point("intent")

    graph.add_conditional_edges("intent",route_by_intent,
                                {
                                    "property_search":"profile",
                                    "chat" : "casual"
                                })

    graph.add_edge("casual",END)
    graph.add_edge("profile","query")
    graph.add_edge("query","search")
    graph.add_edge("search","explain")
    graph.add_edge("explain",END)

    checkpointer = MemorySaver()

    return graph.compile(checkpointer=checkpointer)
