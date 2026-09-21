import os

from dotenv import load_dotenv
from fastapi import FastAPI

load_dotenv(override=True)

# Verbose logging dumps every prompt/response to stdout — on a shared deployment
# that means all users' conversations end up in the server logs, so opt in only.
if os.getenv("DEBUG_AGENT_LOGS"):
    from agents import enable_verbose_stdout_logging

    enable_verbose_stdout_logging()

app = FastAPI()

@app.get("/")
async def read_root():
    return {"message": "Hello, World!"}
