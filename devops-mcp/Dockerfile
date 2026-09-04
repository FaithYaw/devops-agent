FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY pyproject.toml uv.lock README.md ./
RUN pip install uv && uv sync --frozen --no-dev

COPY . .

EXPOSE 9090

CMD ["uv", "run", "python", "server.py"]
