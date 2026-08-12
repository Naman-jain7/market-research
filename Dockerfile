ARG PYTHON_VERSION=3.11.9
ARG UV_VERSION=0.8.4


# stage 1: builder stage to install python dependencies
FROM python:${PYTHON_VERSION}-slim-bookworm AS builder

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=0

WORKDIR /app

# install uv from an existing docker img
COPY --from=ghcr.io/astral-sh/uv:${UV_VERSION} /uv /uvx /usr/local/bin/

# install build tools
RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential \
    && rm -rf /var/lib/apt/lists/*

# copy dependency files
COPY pyproject.toml uv.lock README.md ./
# create the project's venv without dev dependencies
RUN uv sync --frozen --no-dev --no-install-project




# stage 2: runtime stage to run the app
FROM python:${PYTHON_VERSION}-slim-bookworm AS runtime

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/app/.venv/bin:${PATH}" \
    STREAMLIT_SERVER_HEADLESS=true \
    STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends libgomp1 \
    && rm -rf /var/lib/apt/lists/* \
    && groupadd --system app \
    && useradd --system --gid app --home-dir /app --shell /usr/sbin/nologin app

COPY --from=builder /app/.venv /app/.venv
COPY . .

RUN mkdir -p data logs reports \
    && chown -R app:app /app

USER app

EXPOSE 8000 8500

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
