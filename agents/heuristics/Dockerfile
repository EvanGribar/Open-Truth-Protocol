FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN groupadd --system otp && useradd --system --gid otp otp
WORKDIR /app

COPY pyproject.toml README.md /app/
COPY agents /app/agents
COPY shared /app/shared

RUN pip install --no-cache-dir .

USER otp
CMD ["python", "-c", "from agents.heuristics.main import process_job; print('heuristics agent ready')"]
