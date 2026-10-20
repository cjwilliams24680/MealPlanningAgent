# syntax=docker/dockerfile:1
# ^ Pins the Dockerfile syntax to the latest Dockerfile v1.x frontend. This is
#   what enables newer features like the `--mount=type=cache` flag used below,
#   and keeps behavior stable even as Docker updates its default parser.

# =============================================================================
# Stage 1: "builder" - resolves and installs dependencies with uv, then
# installs the project itself. Nothing from this stage ships in the final
# image except the finished virtualenv and the source tree.
# =============================================================================
FROM python:3.12-slim AS builder
# python:3.12-slim matches the `requires-python = ">=3.12"` / `.python-version`
# pin in this repo. "slim" (Debian-based, trimmed) keeps the base small while
# still having a real package manager available, unlike "alpine" (musl libc),
# which can cause subtle breakage with Python wheels built against glibc.

COPY --from=ghcr.io/astral-sh/uv:0.11 /uv /uvx /bin/
# Grabs the official static `uv`/`uvx` binaries directly from Astral's
# published image instead of `pip install uv` or a curl|sh bootstrap script -
# this is the documented, reproducible way to get uv into a Docker image, and
# it adds no Python packaging overhead of its own.

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PROJECT_ENVIRONMENT=/app/.venv
# UV_COMPILE_BYTECODE=1 : pre-compiles .pyc files during `uv sync` (build time)
#   rather than paying that cost on every container cold start.
# UV_LINK_MODE=copy     : uv normally hardlinks packages from its cache to save
#   disk space, but hardlinks don't survive being copied across Docker build
#   stages (as we do below) - `copy` avoids warnings/broken links from that.
# UV_PROJECT_ENVIRONMENT : tells uv exactly where to create the venv, so stage 2
#   knows precisely what path to `COPY --from=builder`.

WORKDIR /app
# All subsequent instructions run relative to /app inside the image.

COPY pyproject.toml uv.lock ./
# Copy ONLY the dependency manifests first, not the application source. Docker
# caches each layer keyed on its inputs - as long as these two files don't
# change, the expensive `uv sync` layer below is reused on every rebuild, even
# if application code in src/ changes constantly.

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project --no-dev
# --frozen             : install exactly what's in uv.lock, never re-resolve -
#   guarantees the same dependency versions in every build (reproducibility).
# --no-install-project : install only third-party dependencies at this point,
#   not this project's own package (its source isn't copied in yet).
# --no-dev             : skip the `dev` dependency group (ipykernel, jupyter,
#   ruff, ...) - those are for local development, not for running the app.
# --mount=type=cache   : a BuildKit cache mount that persists uv's package
#   cache between builds without baking it into any image layer, so repeated
#   builds are fast but the final image stays lean.

COPY src ./src
COPY README.md ./
# Now bring in the actual application code, after the slow dependency layer
# has already been cached above. README.md is also required here: uv_build
# reads pyproject.toml's `readme = "README.md"` field when it builds this
# project's own package in the next step.

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev
# Second sync, now without --no-install-project, installs this project's own
# package (meal-planning-agent) into the venv, which is what wires up the
# `meal-planning-agent` console-script entry point used as the CMD below.
# Fast, because all dependencies were already installed in the previous layer.

# =============================================================================
# Stage 2: runtime - a clean base with only the finished venv and source code.
# No uv binary, no build cache, no lockfiles: smaller image, smaller attack
# surface, nothing an attacker could use to pull in new packages at runtime.
# =============================================================================
FROM python:3.12-slim AS runtime

RUN addgroup --system app && adduser --system --ingroup app app
# Creates a dedicated unprivileged system user/group. Containers should never
# run application processes as root - if the process is ever compromised, a
# non-root user limits what it can do to the host or other containers.

WORKDIR /app

COPY --from=builder --chown=app:app /app/.venv /app/.venv
COPY --from=builder --chown=app:app /app/src /app/src
# Copy only the two things the running app actually needs out of the builder
# stage: the fully-populated virtualenv and the application source (needed
# because uv installs this project in editable mode, so the venv's entry
# point still points back at these files on disk).
# --chown=app:app sets ownership to the non-root user up front, instead of a
# separate `RUN chown -R` layer (which would otherwise double the image size,
# since Docker layers are additive - the old root-owned copy stays in history).

ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1
# PATH        : puts the venv's binaries (including the `meal-planning-agent`
#   entry-point script) first, so CMD can call it by name with no activation
#   step and without needing `uv run` (uv itself isn't even in this stage).
# PYTHONUNBUFFERED : makes Python flush stdout/stderr immediately instead of
#   buffering, so `docker logs` shows output in real time rather than in
#   delayed chunks.

USER app
# Drop root privileges for every instruction (and the running process) from
# here on.

EXPOSE 8000
# Documents which port the app listens on (see uvicorn.run(..., port=8000) in
# main.py). Purely informational to humans/tools reading the image - it does
# NOT actually publish the port; that still requires `-p 8000:8000` at
# `docker run` time.

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1
# Lets `docker ps` / orchestrators (Compose, Kubernetes, etc.) know whether the
# container is actually serving traffic, not just "running". Reuses the app's
# existing GET /health endpoint. Uses Python's stdlib urllib instead of
# curl/wget so we don't have to install an extra OS package just for this.

CMD ["meal-planning-agent"]
# Runs the project's own console-script entry point (from
# pyproject.toml's [project.scripts]), which calls uvicorn.run(...) in
# main.py. Using the exec-form JSON array (not a shell string) means this
# process runs as PID 1 and receives signals like SIGTERM directly, so
# `docker stop` shuts it down promptly instead of waiting for a timeout.
