from agents import Runner, trace
import gradio as gr
from agents import SQLiteSession, enable_verbose_stdout_logging
from .orchestration import orchestration_agent

def run():
    session = SQLiteSession("meal_planner_history.db")

    async def chat(message, history):
        with trace("Meal Planning - LLM Orchestration"):
            return (await Runner.run(starting_agent = orchestration_agent, input = message, session = session)).final_output

    # enable_verbose_stdout_logging()
    gr.ChatInterface(
        chat,
        title="Meal Planner",
        chatbot=gr.Chatbot(
            value=[{"role": "assistant", "content": "Hello! I'm your AI Meal Planner. I can help you plan, shop for, and cook your meals. Would you like to review your eating and cooking preferences? Or should we skip ahead to picking out some meals?"}],
            show_label=False,
        ),
    ).launch(
        theme=gr.themes.Base(), 
    )


if __name__ == "__main__":
    run()