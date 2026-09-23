# Meal Planning Agent

A conversational meal-planning agent built on the OpenAI Agents SDK with a FastAPI interface. 
It reviews your preferences, brainstorms and pairs meals,
writes recipes, and produces a final meal plan with a consolidated shopping
list.

[You can use it here](https://huggingface.co/spaces/cjwilliams24680/meal-planning-agent)

The browser will remember your preferences, but every refresh will clear the chat history.

## Required secrets / environment variables

- `OPENAI_API_KEY`
- `GOOGLE_API_KEY`
- `GROK_API_KEY`

Optional: set `DEBUG_AGENT_LOGS=1` to enable verbose agent SDK logging
(dumps full prompts/responses to stdout — leave off in shared deployments).

## Local development

```bash
uv sync                        # install dependencies
uv run meal-planning-agent     # run FastAPI application
uv run ruff format .           # format
uv run ruff check .            # lint
```

