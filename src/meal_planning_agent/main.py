import uuid
from collections import OrderedDict
from dataclasses import dataclass, field

import gradio as gr
from agents import Runner, SQLiteSession, trace

from .orchestration import orchestration_agent
from .preferences import SessionState, set_current_session
from .theme import BISTRO_CSS, bistro_theme

MAX_SESSIONS = 100  # LRU cap on concurrently-remembered browser sessions


@dataclass
class UserSession:
    state: SessionState = field(default_factory=SessionState)
    history: SQLiteSession | None = None


_sessions: OrderedDict[str, UserSession] = OrderedDict()


def _get_or_create_session(session_hash: str) -> UserSession:
    existing = _sessions.get(session_hash)
    if existing is not None:
        _sessions.move_to_end(session_hash)
        return existing
    user_session = UserSession(history=SQLiteSession(session_id=session_hash))
    _sessions[session_hash] = user_session
    while len(_sessions) > MAX_SESSIONS:
        _sessions.popitem(last=False)
    return user_session


async def chat(message, history, request: gr.Request):
    # request/session_hash is None for direct API calls and example caching;
    # give those an isolated session
    session_hash = (request and request.session_hash) or str(uuid.uuid4())
    user_session = _get_or_create_session(session_hash)
    set_current_session(user_session.state)
    with trace("Meal Planning Agent"):
        return (
            await Runner.run(
                starting_agent=orchestration_agent,
                input=message,
                session=user_session.history,
            )
        ).final_output

introduction = """
## Hello! I'm your AI Meal Planner. I am here to help with your meal planning needs.
### Where would you like to start?
(Select an example or type your own message)
"""

def run():
    gr.ChatInterface(
        chat,
        title="🍷 Meal Planner",
        description=introduction,
        concurrency_limit=10,  # Gradio's default of 1 serializes all users
        chatbot=gr.Chatbot(
            show_label=False,
        ),
        examples=[
            "Please generate meal ideas for me",
            "I have chicken thighs in the fridge, please generate a meal using them",
            "Please write a recipe for pasta carbonara",
            "I want to review my user preferences",
        ],
        # Spaces sets GRADIO_CACHE_EXAMPLES=true, which would run the full
        # agent pipeline per example at every build
        cache_examples=False,
    ).launch(
        theme=bistro_theme(),
        css=BISTRO_CSS,
    )


if __name__ == "__main__":
    run()
