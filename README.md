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

Optional: set `DEBUG=1` to enable verbose agent SDK logging
(dumps full prompts/responses to stdout — leave off in shared deployments).

## Local development

```bash
uv sync                        # install dependencies
uv run meal-planning-agent     # run FastAPI application
uv run ruff format .           # format
uv run ruff check .            # lint
```



## Run With Docker

```bash
# Build Docker image locally
docker build -t cjwilliams24680/meal-planning-agent:0.1.0 .

# Run Docker image locally in isolation
docker run -p 8080:8000 --env-file .env cjwilliams24680/meal-planning-agent:0.1.0

# Use Docker Compose to run the image with a local environment
docker compose up
```
