FROM python:3.11.9-slim-bookworm

ARG UV_VERSION=0.11.25

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/app/.venv/bin:$PATH" \
    STREAMLIT_SERVER_HEADLESS=true \
    STREAMLIT_BROWSER_GATHER_USAGE_STATS=false \
    UV_TORCH_BACKEND=cpu

RUN pip install --no-cache-dir "uv==${UV_VERSION}"

COPY pyproject.toml uv.lock README.md ./

RUN uv sync --frozen --no-dev --no-install-project

COPY . .

RUN mkdir -p data logs reports

EXPOSE 8000 8500

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
