FROM python:3.12-slim

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Copy dependency files first (for caching)
COPY pyproject.toml uv.lock ./

# Install dependencies
RUN uv sync --locked

# Copy source code
COPY src/ .

# Run the app
CMD ["python", "main.py"]
