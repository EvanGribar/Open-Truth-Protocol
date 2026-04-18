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
EXPOSE 8000

CMD ["python", "-m", "uvicorn", "agents.orchestrator.main:app", "--host", "0.0.0.0", "--port", "8000"]
