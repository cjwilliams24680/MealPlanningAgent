from contextlib import asynccontextmanager
from typing import Annotated

from agents import Runner, trace
from fastapi import Body, Cookie, FastAPI, HTTPException, Response, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

import meal_planning_agent.authentication.service as AuthService
import meal_planning_agent.conversations.service as ConversationsService
import meal_planning_agent.conversations_database as ConversationsDatabase
import meal_planning_agent.users_database as UsersDatabase
from meal_planning_agent.agent.orchestration import ORCHESTRATION_AGENT
from meal_planning_agent.agent_context import AgentContext


@asynccontextmanager
async def lifespan(app: FastAPI):
    await UsersDatabase.create_db_and_tables()
    await ConversationsDatabase.create_db_and_tables()
    yield


app = FastAPI(
    title="Meal Planning Agent API",
    description="A meal planning agent that helps you plan your meals",
    version="0.1.0",
    contact={
        "name": "Chris Williams",
        "url": "https://github.com/cjwilliams24680/meal-planning-agent",
    },
    lifespan=lifespan,
)
# TODO make this restrictive in production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class AppCookies(BaseModel):
    session_token: str | None = None
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
    session_token = cookies.session_token
    has_valid_session_token = await AuthService.is_valid(session_token)

    if not has_valid_session_token:
        session = await AuthService.create_anonymous_session()
        session_token = session.session_token

    user = await AuthService.get_user(session_token=session_token)
    conversation = await ConversationsService.create_conversation(user.id)

    response.set_cookie(key="session_token", value=session_token)
    response.set_cookie(key="conversation_id", value=conversation.id)

    return {"message": "Cookies updated successfully"}


@app.post("/send_message", status_code=status.HTTP_200_OK)
async def send_message(
    cookies: Annotated[AppCookies, Cookie()],
    body: Annotated[SendMessageRequest, Body()],
):
    if not cookies.session_token:
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

    user = await AuthService.get_user(cookies.session_token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Session"
        )

    conversation = await ConversationsService.get_conversation(
        conversation_id=cookies.conversation_id,
        user_id=user.id,
    )

    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found for user",
        )

    with trace("Meal Planning Agent"):
        # Generate LLM Response
        trimmed_conversation_history = conversation.history[-100:]
        input = trimmed_conversation_history + [
            {"role": "user", "content": body.message}
        ]
        result = await Runner.run(
            starting_agent=ORCHESTRATION_AGENT,
            input=input,
            context=AgentContext(user_id=user.id),
        )

        await ConversationsService.update_history(
            user_id=conversation.user_id,
            conversation_id=conversation.id,
            history=result.to_input_list(),
        )
        return {"response": result.final_output}


def run():
    import os

    import uvicorn

    uvicorn.run(
        "meal_planning_agent.main:app",
        host="0.0.0.0",
        port=8000,
        reload=os.getenv("UVICORN_RELOAD", "false").lower() == "true",
    )
