FROM ghcr.io/astral-sh/uv:python3.12-trixie

WORKDIR /code

COPY pyproject.toml  uv.lock README.md ./

RUN uv sync --no-cache --locked --no-dev --no-install-project

COPY . ./

RUN uv sync --no-cache --locked --no-dev

CMD ["fastapi", "run", "src/backend/main.py", "--host", "0.0.0.0", "--port", "8080"]