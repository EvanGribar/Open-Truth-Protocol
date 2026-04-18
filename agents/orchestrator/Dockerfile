FROM python:3.12.6-slim@sha256:ad48727987b259854d52241fac3bc633574364867b8e20aec305e6e7f4028b26

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN groupadd --system otp && useradd --system --gid otp otp
WORKDIR /app

# Install dependencies from requirements.txt with hashes
COPY requirements.txt /app/
RUN pip install --no-cache-dir --require-hashes -r requirements.txt

COPY pyproject.toml README.md /app/
COPY agents /app/agents
COPY shared /app/shared

# Install the local package without dependencies (already installed)
RUN pip install --no-cache-dir --no-deps .

USER otp
EXPOSE 8000

CMD ["python", "-m", "uvicorn", "agents.orchestrator.main:app", "--host", "0.0.0.0", "--port", "8000"]
