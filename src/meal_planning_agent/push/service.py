import requests

from meal_planning_agent.utils import assert_key_exists

_PUSHOVER_USER = assert_key_exists("PUSHOVER_USER")
_PUSHOVER_TOKEN = assert_key_exists("PUSHOVER_TOKEN")
_PUSHOVER_URL = "https://api.pushover.net/1/messages.json"


def send_push_notification(message: str):
    payload = {"user": _PUSHOVER_USER, "token": _PUSHOVER_TOKEN, "message": message}
    requests.post(_PUSHOVER_URL, data=payload)
