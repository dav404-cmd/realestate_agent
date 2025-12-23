from pydantic import BaseModel
from typing import Optional, List, Dict, Any

class AgentState(BaseModel):
    # user input
    user_input: str

    # routing
    intent: Optional[str] = None

    #database info
    db_profile : Optional[Dict[str,Any]] = None

    # property search
    extracted_filters: Optional[Dict[str, Any]] = None
    query_object: Optional[Dict[str, Any]] = None
    results: Optional[List[Dict[str, Any]]] = None

    # final response
    response: Optional[str] = None
