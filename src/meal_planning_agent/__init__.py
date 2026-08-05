import os

from dotenv import load_dotenv

load_dotenv(override=True)

# Verbose logging dumps every prompt/response to stdout — on a shared deployment
# that means all users' conversations end up in the server logs, so opt in only.
if os.getenv("DEBUG_AGENT_LOGS"):
    from agents import enable_verbose_stdout_logging

    enable_verbose_stdout_logging()
