import os
from typing import Annotated

from agents import Runner, trace
from dotenv import load_dotenv
from fastapi import Body, Cookie, FastAPI, HTTPException, Response, status
from pydantic import BaseModel

from meal_planning_agent.auth import UserMetadata, create_session
from meal_planning_agent.chat_history_store import (
    create_conversation,
    get_or_create_history,
)
from meal_planning_agent.orchestration import ORCHESTRATION_AGENT

load_dotenv(override=True)

# Verbose logging dumps every prompt/response to stdout — on a shared deployment
# that means all users' conversations end up in the server logs, so opt in only.
if os.getenv("DEBUG_AGENT_LOGS"):
    from agents import enable_verbose_stdout_logging

    enable_verbose_stdout_logging()

app = FastAPI(
    title="Meal Planning Agent API",
    description="A meal planning agent that helps you plan your meals",
    version="0.1.0",
    contact={
        "name": "Chris",
        "url": "https://github.com/cjwilliams24680/meal-planning-agent",
    },
)


class AppCookies(BaseModel):
    session_id: str | None = None
    conversation_id: str | None = None


class SendMessageRequest(BaseModel):
    message: str = ""


@app.get("/", status_code=status.HTTP_200_OK)
async def read_root():
    return {"status": "healthy"}


@app.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    return {"status": "healthy"}


@app.get("/initialize", status_code=status.HTTP_200_OK)
async def initialize(
    cookies: Annotated[AppCookies, Cookie()],
    response: Response,
):
    session_id = cookies.session_id
    if not session_id:
        session_id = create_session()
    response.set_cookie(key="session_id", value=session_id)

    response.set_cookie(key="conversation_id", value=create_conversation())

    return {"message": "Cookies updated successfully"}


@app.post("/send_message", status_code=status.HTTP_200_OK)
async def send_message(
    cookies: Annotated[AppCookies, Cookie()],
    body: Annotated[SendMessageRequest, Body()],
):
    if not cookies.session_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Session not specified"
        )
    if not cookies.conversation_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Conversation not specified"
        )
    if not body.message:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Message is not provided"
        )

    session = get_or_create_history(conversation_id=cookies.conversation_id)

    with trace("Meal Planning Agent"):
        result = await Runner.run(
            starting_agent=ORCHESTRATION_AGENT,
            input=body.message,
            session=session,
            context=UserMetadata(session_id=cookies.session_id),
        )
        return {"response": result.final_output}
