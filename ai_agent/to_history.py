from langchain_core.messages import HumanMessage,AIMessage

def get_history(messages) -> list:
    out = []
    for m in messages:
        if isinstance(m,HumanMessage):
            out.append({"role":"user","content":m.content})
        elif isinstance(m,AIMessage):
            out.append({"role":"assistant","content":m.content})
    return out