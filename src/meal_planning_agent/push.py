import requests
from agents import function_tool

from .utils import assertKeyExists

pushover_user = assertKeyExists("PUSHOVER_USER")
pushover_token = assertKeyExists("PUSHOVER_TOKEN")
pushover_url = "https://api.pushover.net/1/messages.json"


@function_tool
def send_push_notification(message: str):
    print(f"Push: {message}")
    payload = {"user": pushover_user, "token": pushover_token, "message": message}
    requests.post(pushover_url, data=payload)
