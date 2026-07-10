FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

ENV UV_NO_DEV=1
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project

COPY src ./src
COPY prompts ./prompts

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen

EXPOSE 8000

ENTRYPOINT ["uv", "run", "--no-sync"]

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]