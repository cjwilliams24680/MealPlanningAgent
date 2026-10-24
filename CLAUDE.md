# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A conversational meal-planning agent built on the OpenAI Agents SDK (`openai-agents`), exposed via a
FastAPI app (`src/meal_planning_agent/main.py`). It reviews the user's preferences, brainstorms and
pairs meals, writes recipes, and produces a final meal plan with a consolidated shopping list. Users
and their preferences are persisted in Postgres; chat history is still in-memory and resets on process
restart.

## Commands

```bash
uv sync                        # install dependencies
uv run meal-planning-agent     # run FastAPI application
uv run ruff format .           # format
uv run ruff check .            # lint
```

There is no test suite in this repo currently. Package management is `uv` (see `uv.lock` /
`pyproject.toml`); `requirements.txt` also exists but `uv` is the primary workflow described in the README.

Python 3.12 is required (`.python-version`, `requires-python = ">=3.12"`).

```bash
docker compose up              # run the app plus its Postgres database
```

### Required environment variables

Set in `.env` (see `.env.example` for the full list): `OPENAI_API_KEY`, `GOOGLE_API_KEY`, `GROK_API_KEY`,
`PUSHOVER_USER`, `PUSHOVER_TOKEN`, `DB_PASSWORD` (used to build `USERS_DB_URL` for the Postgres
connection in `users_database.py`). Optional: `DEBUG=True` enables verbose Agents SDK + SQL logging.
`assert_key_exists` in `utils.py` raises at import time if a required key is missing, so most modules
that read env vars will fail fast on startup rather than at call time.

## Architecture

### Request flow

`main.py` is a thin FastAPI shell with `/initialize` (validates or mints a `session_token` cookie via
`authentication/service.py`, creates a new `conversation_id` cookie via `conversations/service.py`),
`/send_message` (runs the agent), and health checks. `session_token` resolves to a `User` row;
`conversation_id` scopes chat history. On `/send_message`, the user is looked up from the session
token, the conversation's history session is fetched/created, and a single
`Runner.run(starting_agent=ORCHESTRATION_AGENT, ...)` call is made with `AgentContext(user_id=...)`
passed as the run `context` so tools can look up the right user's data.

### Domain services (auth / users / conversations / preferences)

Four small modules under `src/meal_planning_agent/{authentication,users,conversations,preferences}/`
each follow the same `models.py` + `service.py` shape:

- `users`: the base `User` row (just an id/email placeholder for now — real auth is still TODO).
- `authentication`: `AuthSession` maps a non-expiring `session_token` to a `user_id`
  (`AuthSessionBase` docstring notes this will be replaced with real JWT-based auth later).
  `create_anonymous_session` creates a `User` + `AuthSession` together for first-time visitors.
- `preferences`: `UserPreferences`, one row per `user_id`, with `get_or_create_preferences` /
  `upsert_preferences`.
- `conversations`: still an in-memory dict (`_conversation_db`) keyed by `conversation_id`, holding a
  `Conversation` dataclass that wraps an `agents.SQLiteSession` for chat history. Marked as an
  "iterative solution until I add databases" — follow the existing dict-based interface here unless
  the task is specifically to move chat history into Postgres too.

`users`, `authentication`, and `preferences` are backed by Postgres via `users_database.py`
(`ENGINE` = async SQLAlchemy engine, `create_db_and_tables()` run on FastAPI's `lifespan` startup).
Models are `sqlmodel.SQLModel` classes split into a `*Base` (shared fields/validation, used as
request/response and tool I/O shapes) and a `table=True` subclass that adds `id`/foreign keys. Service
functions open their own `AsyncSession(ENGINE)` rather than taking a session as a FastAPI dependency
(except `users.service`, which takes a session so it can be called from within another service's
transaction, e.g. from `authentication.service.create_anonymous_session`).

When adding a new persisted concept, follow this same `models.py` (Base + table) / `service.py`
(get_or_create / upsert functions, own `AsyncSession`) split rather than inlining queries elsewhere.

### Agent-as-tool orchestration (`agent/orchestration.py`)

There's one top-level `ORCHESTRATION_AGENT` (a router) with no domain logic of its own — its
instructions explicitly tell it to delegate everything to tools rather than do steps itself. Each
"step" of the meal-planning conversation (review preferences, update preferences, propose meal ideas,
replace rejected ideas, write up the full plan, handle a single-dish request, or file a feature
request) is a separate `Agent` wrapped as a tool via `.as_tool(...)`. This is the pattern to follow
when adding a new conversational capability: define a small single-purpose `Agent` with its own
instructions/tools/output model in its own module under `agent/`, then register it as a tool on
`ORCHESTRATION_AGENT` in `orchestration.py`. Conversation state (which step comes next) lives entirely
in the chat history / LLM reasoning — there's no explicit state machine.

### Generate → validate pipeline

Most content generation follows a two-stage pattern: an LLM call generates candidates, then a second,
usually cheaper/different-model LLM call validates or filters them, often in a retry loop capped at a
few attempts:

- `meal_brainstorm_generation.py` generates dish ideas → `meal_brainstorm_validation.py` filters out
  dishes that violate preferences/allergens.
- `meal_pairing.py` picks entrees, pairs them with sides, then validates the pairing against
  preferences (loop up to 3 attempts, falling back to the last result).
- `recipe_generation.py` generates a recipe, adjusts serving size if needed, then
  `recipe_validation.py` validates it against preferences (same retry pattern).

When adding a new generation step, follow this same generate-then-validate shape rather than trusting
a single LLM call's output.

### Models (`agent/llm_models.py`)

Multiple providers are wired up as interchangeable `agents` SDK models, all via the OpenAI-compatible
chat completions interface: `DEFAULT_MODEL`/`HIGH_EFFORT_MODEL`/`BALANCED_MODEL` (OpenAI), `GEMINI_MODEL`
(via Google's OpenAI-compatible endpoint), and a Grok model. `get_random_model()` is used in a couple of
generation spots specifically to inject variety into brainstorming output — don't "fix" that
randomness, it's intentional. Pick a model tier per agent based on how much reasoning the step needs
(e.g. validation/boolean-judgment agents tend to use the cheaper/faster models; recipe generation uses
`BALANCED_MODEL`; recipe adjustment/validation uses `HIGH_EFFORT_MODEL`).

### Models/schemas

Pydantic/SQLModel models define the LLM structured-output contracts (`output_type=...` on `Agent`),
the tool I/O contracts (`@function_tool`, see `agent/tools.py`), and the Postgres row shapes:
`agent/meal_models.py` (`PreparedDish`, `MealPlanIdeas`), `preferences/models.py`
(`UserPreferencesBase`/`UserPreferences`), `agent/recipe_models.py` (`Ingredient`, `Recipe`,
`MealPlanItem`, grocery department list). Field descriptions on these models are part of the prompt
seen by the LLM (via structured output schemas) — treat them as prompt text, not just docs.

### Misc

- `agent/shopping_list.py` consolidates and sorts ingredients across recipes by (name, unit,
  department) and renders a grouped markdown checklist — pure Python, no LLM calls.
- `agent/seasonal_report.py` is a pure-Python helper that injects the current month/season into
  brainstorming prompts for variety and weather-appropriate suggestions.
- `push/service.py` sends a Pushover notification to the developer; used by the feature-request agent
  tool when a user asks for something out of scope.
- `notebooks/prompt_experiments.ipynb` is excluded from ruff (`extend-exclude = ["notebooks"]`) and used
  for ad hoc prompt experimentation, not part of the app.
