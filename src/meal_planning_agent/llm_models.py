import random

from agents import OpenAIChatCompletionsModel
from openai import AsyncOpenAI

from .utils import assertKeyExists

HIGH_EFFORT_MODEL = "gpt-5.6-sol"
BALANCED_MODEL = "gpt-5.6-terra"
LOW_EFFORT_MODEL = "gpt-5.6-luna"
DEFAULT_MODEL = LOW_EFFORT_MODEL

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
    models = [DEFAULT_MODEL, gemini_model, grok_model]
    return random.choice(models)
