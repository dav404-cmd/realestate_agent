from pydantic import BaseModel,Field
from typing import Optional, List, Dict, Any
from langchain_core.messages import BaseMessage

class AgentState(BaseModel):
    # user input
    user_input: str

    #memory
    messages: List[BaseMessage] = Field(default_factory=list)

    # routing
    intent: Optional[str] = None

    # property search
    extracted_filters: Optional[Dict[str, Any]] = None
    query_object: Optional[Dict[str, Any]] = None
    results: Optional[List[Dict[str, Any]]] = None

    # final response
    response: Optional[str] = None
