import os

BASE_SYSTEM_INSTRUCTIONS = """
You are a meal planning assistant who helps people plan their meals for the week.
You are an expert on simple meals that require minimal amounts of preparation, reheat well, and are delicious.
"""


def assert_key_exists(key: str) -> str:
    value = os.getenv(key)
    if value:
        return value
    raise ValueError(f"{key} not found")


def to_markdown_list(data: list[any], bullet: str = "-"):
    """
    Converts a list into a markdown bulleted list string.
    """
    return "\n".join(f"{bullet} {str(item)}" for item in data)


def clamp(n, min_n, max_n):
    return max(min_n, min(n, max_n))


def enable_debug_logging() -> bool:
    return os.getenv("DEBUG", "False").lower() in ("true", "1", "t")
