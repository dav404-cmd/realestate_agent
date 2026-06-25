from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel

from utils.logger import get_logger

api_log = get_logger("AgentApi")
router = APIRouter()

class ChatRequest(BaseModel):
    message: str
    thread_id: str

@router.post("/re_agent")
def chat_agent(
    request: Request,
    body: ChatRequest
):
    api_log.info(f"Request received for agent. ms : {body.message},thread_id : {body.thread_id}")
    try:
        runtime = request.app.state.agent_runtime

        final_state = runtime.agent.invoke(
            {"user_input": body.message},
            config={
                "configurable": {
                    "thread_id": body.thread_id
                }
            }
        )
        api_log.info(f"Response : {final_state.get('response')},thread_id : {body.thread_id}")

        return {
            "response": final_state.get("response")
        }

    except Exception:
        api_log.exception("Error during chat")
        raise HTTPException(
            status_code=500,
            detail="Agent execution failed"
        )