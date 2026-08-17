import random

from agents import OpenAIChatCompletionsModel
from openai import AsyncOpenAI

from .utils import assertKeyExists

HIGH_EFFORT_MODEL = "gpt-5.6-sol"
BALANCED_MODEL = "gpt-5.6-terra"
_LOW_EFFORT_MODEL = "gpt-5.6-luna"
DEFAULT_MODEL = _LOW_EFFORT_MODEL

_GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"
_GEMINI_CLIENT = AsyncOpenAI(
    base_url=_GEMINI_BASE_URL, api_key=assertKeyExists("GOOGLE_API_KEY")
)
GEMINI_MODEL = OpenAIChatCompletionsModel(
    model="gemini-3.6-flash", openai_client=_GEMINI_CLIENT
)

_GROK_BASE_URL = "https://api.x.ai/v1"
_GROK_CLIENT = AsyncOpenAI(
    base_url=_GROK_BASE_URL, api_key=assertKeyExists("GROK_API_KEY")
)
_GROK_MODEL = OpenAIChatCompletionsModel(model="grok-4.5", openai_client=_GROK_CLIENT)


# Randomly returns a model so that the behavior is more variable
def get_random_model():
    models = [DEFAULT_MODEL, GEMINI_MODEL, _GROK_MODEL]
    return random.choice(models)
