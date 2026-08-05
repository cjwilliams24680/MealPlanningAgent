---
title: Meal Planner
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
