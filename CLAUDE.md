# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A conversational meal-planning agent built on the OpenAI Agents SDK (`openai-agents`), exposed via a
FastAPI app (`src/meal_planning_agent/main.py`). It reviews the user's preferences, brainstorms and
pairs meals, writes recipes, and produces a final meal plan with a consolidated shopping list. All
state (chat history, preferences) is in-memory and ephemeral — it resets on process restart.

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

### Required environment variables

Set in `.env` (see `.env` for the full list): `OPENAI_API_KEY`, `GOOGLE_API_KEY`, `GROK_API_KEY`,
`PUSHOVER_USER`, `PUSHOVER_TOKEN`. Optional: `DEBUG_AGENT_LOGS=1` enables verbose Agents SDK logging
(dumps full prompts/responses — keep off in shared deployments). `assertKeyExists` in `utils.py` raises
at import time if a required key is missing, so most modules that read env vars will fail fast on
startup rather than at call time.

## Architecture

### Request flow

`main.py` is a thin FastAPI shell with three endpoints: `/initialize` (mints `session_id` and
`conversation_id` cookies), `/send_message` (runs the agent), and health checks. `session_id` scopes
user preferences; `conversation_id` scopes chat history — they're independent, set as separate cookies,
and both are required on `/send_message`. Every message runs through a single
`Runner.run(starting_agent=ORCHESTRATION_AGENT, ...)` call, with `UserMetadata(session_id=...)` passed
as the run `context` so tools can look up the right session's data.

### Agent-as-tool orchestration (`orchestration.py`)

There's one top-level `ORCHESTRATION_AGENT` (a router) with no domain logic of its own — its
instructions explicitly tell it to delegate everything to tools rather than do steps itself. Each
"step" of the meal-planning conversation (review preferences, update preferences, propose meal ideas,
replace rejected ideas, write up the full plan, handle a single-dish request, or file a feature
request) is a separate `Agent` wrapped as a tool via `.as_tool(...)`. This is the pattern to follow
when adding a new conversational capability: define a small single-purpose `Agent` with its own
instructions/tools/output model in its own module, then register it as a tool on
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

### Models (`llm_models.py`)

Multiple providers are wired up as interchangeable `agents` SDK models, all via the OpenAI-compatible
chat completions interface: `DEFAULT_MODEL`/`HIGH_EFFORT_MODEL`/`BALANCED_MODEL` (OpenAI), `GEMINI_MODEL`
(via Google's OpenAI-compatible endpoint), and a Grok model. `get_random_model()` is used in a couple of
generation spots specifically to inject variety into brainstorming output — don't "fix" that
randomness, it's intentional. Pick a model tier per agent based on how much reasoning the step needs
(e.g. validation/boolean-judgment agents tend to use the cheaper/faster models; recipe generation uses
`BALANCED_MODEL`; recipe adjustment uses `HIGH_EFFORT_MODEL`).

### In-memory stores

`chat_history_store.py` (keyed by `conversation_id`, using `agents.SQLiteSession`) and
`preferences_store.py` (keyed by `session_id`, using `UserPreferences`) are both plain in-memory dicts
with a `get_or_create_*` / `upsert_*` interface, explicitly marked as "iterative solution until I add
databases." When touching persistence, keep using that dict-based interface unless the task is
specifically to add real database-backed storage.

### Models/schemas

Pydantic models define both the LLM structured-output contracts (`output_type=...` on `Agent`) and the
tool I/O contracts (`@function_tool(output_type=...)`): `meal_models.py` (`PreparedDish`,
`MealPlanIdeas`), `preference_models.py` (`UserPreferences`), `recipe_models.py` (`Ingredient`,
`Recipe`, `MealPlanItem`, grocery department list). Field descriptions on these models are part of the
prompt seen by the LLM (via structured output schemas) — treat them as prompt text, not just docs.

### Misc

- `shopping_list.py` consolidates and sorts ingredients across recipes by (name, unit, department) and
  renders a grouped markdown checklist — pure Python, no LLM calls.
- `seasonal_report.py` is a pure-Python helper that injects the current month/season into brainstorming
  prompts for variety and weather-appropriate suggestions.
- `push.py` sends a Pushover notification to the developer; used by the feature-request agent tool when
  a user asks for something out of scope.
- `notebooks/prompt_experiments.ipynb` is excluded from ruff (`extend-exclude = ["notebooks"]`) and used
  for ad hoc prompt experimentation, not part of the app.
