# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

Package manager is **uv** (Python 3.12, `uv_build` backend). There is no Makefile or test suite.

```bash
uv sync                    # install dependencies
uv run meal-planning-agent # launch the Gradio chat UI at http://127.0.0.1:7860
uv run ruff format .       # format
uv run ruff check .        # lint (add --fix to autofix)
```

Ruff is the only formatter/linter. It excludes `notebooks/`, formats at 88 columns, and E501 only flags lines over 120 (long prompt strings can't be wrapped by the formatter). Lint rules: E, W, F, I, UP, B, SIM.

### Environment

Config comes from a gitignored `.env` loaded by `src/meal_planning_agent/__init__.py` at import time (which also enables verbose agent SDK stdout logging). Required keys — several modules call `assertKeyExists()` **eagerly at import**, so the package won't even import without them:

- `OPENAI_API_KEY`
- `GOOGLE_API_KEY`, `GROK_API_KEY` (asserted in `models.py`)
- `PUSHOVER_USER`, `PUSHOVER_TOKEN` (asserted in `push.py`, which is otherwise unused)

## Architecture

A conversational meal-planning agent built on the **OpenAI Agents SDK** (`agents` package) with a Gradio front end. All code lives in `src/meal_planning_agent/`.

### Orchestration (agents-as-tools pattern)

`main.py` runs a chat loop: each user turn goes through `Runner.run(starting_agent=orchestration_agent, ...)` with a `SQLiteSession("meal_planner_history.db")` for conversation memory, wrapped in a trace.

`orchestration.py` is the hub. The root `orchestration_agent` exposes five sub-agents via `.as_tool(...)`, each with a Pydantic parameter model, implementing the workflow: review preferences → update preferences → generate initial meal pairings → generate replacement pairings → write the final meal plan + shopping list. All agent prompts are long triple-quoted strings inline in this file (shared preamble in `utils.py:base_system_instructions`).

### Generation pipeline

- `meal_brainstorming.py` — brainstorms `number_of_meals * 5` entrees and sides in parallel (`asyncio.gather`), seasoned by `get_seasonal_report()` (current month/season injected into prompts); a validation agent filters dishes that violate preferences.
- `meal_pairing.py` — picks entrees, pairs them with sides, and validates the pairings, retrying up to 4 attempts in `generate_meals()`. Exposes the `@function_tool`s used by orchestration for initial ideas and replacements.
- `recipes.py` — generates full `Recipe`s with typed `Ingredient`s (each tagged with a grocery-store department), adjusts serving counts, and validates in a retry loop.
- `meal_plan_writeup.py` — final `generate_meal_plan()` tool: LLM-authored plan markdown plus a deterministic shopping list.
- `shopping_list.py` — pure Python (no LLM): consolidates ingredients keyed on `(name, unit, department)` and emits a markdown grocery checklist ordered by department.

### Cross-cutting details

- **Multi-provider models** (`models.py`): named OpenAI model tiers (`high_effort_model`, `balanced_model`, `low_effort_model`/`default_model`) plus Gemini and Grok reached through `OpenAIChatCompletionsModel` with custom `AsyncOpenAI` base URLs. `get_random_model()` deliberately varies providers for output diversity; validation steps intentionally use a *different* provider than generation (e.g. pairing validation uses Gemini, recipe validation uses Grok).
- **Preferences are in-memory only** (`preferences.py`): a module-level global `saved_user_preferences` holds the `UserPreferences` model; `sanitize_user_preferences` clamps meals to 1–10 and servings to 1–100. Nothing persists across restarts except chat history in the SQLite session db.
- `notebooks/prompt_experiments.ipynb` is a cleared scratchpad for prompt iteration; the real prompts live in the Python modules.
