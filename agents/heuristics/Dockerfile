FROM python:3.12.6-slim@sha256:ad48727987b259854d52241fac3bc633574364867b8e20aec305e6e7f4028b26

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN groupadd --system otp && useradd --system --gid otp otp
WORKDIR /app

COPY pyproject.toml README.md /app/
COPY agents /app/agents
COPY shared /app/shared

RUN pip install --no-cache-dir .

USER otp
CMD ["python", "-m", "agents.heuristics.main"]
