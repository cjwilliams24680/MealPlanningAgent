import random

from agents import OpenAIChatCompletionsModel
from openai import AsyncOpenAI

from .utils import assertKeyExists

high_effort_model = "gpt-5.6-sol"
balanced_model = "gpt-5.6-terra"
low_effort_model = "gpt-5.6-luna"
default_model = low_effort_model

GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"
gemini_client = AsyncOpenAI(
    base_url=GEMINI_BASE_URL, api_key=assertKeyExists("GOOGLE_API_KEY")
)
gemini_model = OpenAIChatCompletionsModel(
    model="gemini-3.6-flash", openai_client=gemini_client
)

GROK_BASE_URL = "https://api.x.ai/v1"
grok_client = AsyncOpenAI(
    base_url=GROK_BASE_URL, api_key=assertKeyExists("GROK_API_KEY")
)
grok_model = OpenAIChatCompletionsModel(model="grok-4.5", openai_client=grok_client)

# Randomly returns a model so that the behavior is more variable
def get_random_model():
    models = [default_model, gemini_model, grok_model]
    return random.choice(models)