---
title: meal-planning-agent
emoji: 🍽️
colorFrom: green
colorTo: blue
sdk: gradio
sdk_version: 6.20.0
app_file: app.py
pinned: false
---

# Meal Planning Agent

A conversational meal-planning agent built on the OpenAI Agents SDK with a
Gradio chat UI. It reviews your preferences, brainstorms and pairs meals,
writes recipes, and produces a final meal plan with a consolidated shopping
list.

[You can use it here](https://huggingface.co/spaces/cjwilliams24680/meal-planning-agent)

Each browser session gets its own preferences and chat history. State is
ephemeral: refreshing the page (or a Space restart) starts a fresh session.

## Required secrets / environment variables

- `OPENAI_API_KEY`
- `GOOGLE_API_KEY`
- `GROK_API_KEY`

Optional: set `DEBUG_AGENT_LOGS=1` to enable verbose agent SDK logging
(dumps full prompts/responses to stdout — leave off in shared deployments).

## Local development

```bash
uv sync                    # install dependencies
uv run meal-planning-agent # launch the chat UI at http://127.0.0.1:7860
uv run ruff format .       # format
uv run ruff check .        # lint
```

## Deploying to Hugging Face

Don't use `gradio deploy` — it uploads the entire working directory,
including `.venv` (~25k files, over the Space file limit) and `.env`
(your API keys). Instead, upload only the project files:

```bash
# if dependencies changed, regenerate requirements.txt first:
uv export --no-dev --no-hashes --no-emit-project -o requirements.txt

uv run python -c "
from huggingface_hub import HfApi
HfApi().upload_folder(
    folder_path='.',
    repo_id='cjwilliams24680/meal-planning-agent',
    repo_type='space',
    ignore_patterns=[
        '.git/**', '.venv/**', '.env', '.ruff_cache/**', '.claude/**',
        '__pycache__/**', '**/__pycache__/**', '.ipynb_checkpoints/**',
        '.DS_Store', '*.egg-info/**', 'meal_planner_history.db',
    ],
)"
```

The Space rebuilds automatically after each upload. Note that the build
installs `requirements.txt` alongside `gradio[oauth,mcp]`, whose `mcp`
extra caps `pydantic<=2.12.5` — keep the pin in `pyproject.toml`
compatible or the build will fail to resolve.
