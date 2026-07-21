import os
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel
from ai_agent.agent import reduce_state

from utils.logger import get_logger


api_log = get_logger("AgentApi")
router = APIRouter()

#todo : update with new version
class ChatRequest(BaseModel):
    message: str
    thread_id: Optional[UUID] = None
    user_id : UUID

@router.post("/re_agent")
def chat_agent(
    request: Request,
    body: ChatRequest
):

    try:
        runtime = request.app.state.agent_runtime

        if not body.thread_id:
            api_log.info(f"Received new chat request for user : {body.user_id}")
            title = body.message[:35]
            body.thread_id = runtime.agent_db.new_thread(str(body.user_id),title)

        api_log.info(f"chat request for :{body.thread_id}")

        final_state = runtime.agent.invoke(
            {"user_input": body.message},
            config={
                "configurable": {
                    "thread_id": body.thread_id
                }
            }
        )
        api_log.info(
            "Response generated (%d chars)",
            len(final_state["response"])
        )
        api_log.info(f"thread_id : {body.thread_id}")
        _id = runtime.agent_db.insert_message(str(body.thread_id),reduce_state(final_state))
        api_log.info(f"message stored , id : {_id}")
        return {
            "thread_id" : body.thread_id,
            "response": final_state.get("response")
        }

    except Exception as e:
        api_log.exception(f"Error during chat : {e}")
        raise HTTPException(
            status_code=500,
            detail="Agent execution failed"
        )

@router.get("/get_message")
def get_message(
        request : Request,
        thread_id : str
):
    try:
        runtime = request.app.state.agent_runtime
        messages = runtime.agent_db.get_messages(thread_id)
        return messages
    except Exception as e :
        api_log.exception(f"error during message retrival : {e}")
        raise HTTPException(
            status_code= 500,
            detail= "Message retrival failed."
        )

@router.get("/get_chat")
def get_chats(
        request : Request ,
        user_id : str
):
    try :
        runtime = request.app.state.agent_runtime
        threads = runtime.agent_db.get_threads(user_id)
        return threads
    except Exception as e:
        api_log.exception(f"error during chat retrival : {e}")
        raise HTTPException(
            status_code=500,
            detail="Message chat failed."
        )

if __name__ == "__main__":
    som = ChatRequest(
        message="hehe",
        user_id= UUID(os.getenv("TEST_USER_ID"))
    )