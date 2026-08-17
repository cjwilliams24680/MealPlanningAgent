import requests
from agents import function_tool

from .utils import assertKeyExists

PUSHOVER_USER = assertKeyExists("PUSHOVER_USER")
PUSHOVER_TOKEN = assertKeyExists("PUSHOVER_TOKEN")
PUSHOVER_URL = "https://api.pushover.net/1/messages.json"


@function_tool
def send_push_notification(message: str):
    """
    Send a push notification to the developer.

    Args:
        message: The message to send to the developer.
    """
    payload = {"user": PUSHOVER_USER, "token": PUSHOVER_TOKEN, "message": message}
    requests.post(PUSHOVER_URL, data=payload)
