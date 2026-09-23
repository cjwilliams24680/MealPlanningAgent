import gradio as gr
from agents import Runner, trace

from .auth import UserMetadata, create_session
from .chat_history_store import get_or_create_history
from .orchestration import ORCHESTRATION_AGENT
from .theme import BISTRO_CSS, bistro_theme


async def _chat(message, history, request: gr.Request):
    # request/session_hash is None for direct API calls and example caching;
    # give those an isolated session
    session_hash = (request and request.session_hash) or create_session()
    with trace("Meal Planning Agent"):
        return (
            await Runner.run(
                starting_agent=ORCHESTRATION_AGENT,
                input=message,
                session=get_or_create_history(conversation_id=session_hash),
                context=UserMetadata(session_id=session_hash),
            )
        ).final_output


def run():
    introduction = """
## Hello! I'm your AI Meal Planner. I am here to help with your meal planning needs.
### Where would you like to start?
(Select an example or type your own message)
"""

    gr.ChatInterface(
        _chat,
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
