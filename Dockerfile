FROM python:3.11-slim as builder

WORKDIR /build

RUN apt-get update && apt-get install -y --no-install-recommends build-essential git && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml /build/
COPY src/ /build/src/

RUN python -m pip install --upgrade pip setuptools wheel
RUN python -m pip wheel . -w /wheels

FROM python:3.11-slim

RUN useradd -m appuser
WORKDIR /app

COPY --from=builder /wheels /wheels
RUN python -m pip install --no-cache /wheels/*

USER appuser
ENV PATH="/home/appuser/.local/bin:$PATH"

ENTRYPOINT ["mbenchmark"]
