from agents import function_tool

import meal_planning_agent.push.service as PushService


@function_tool
def send_push_notification(message: str):
    """
    Send a push notification to the developer.

    Args:
        message: The message to send to the developer.
    """
    PushService.send_push_notification(message)
