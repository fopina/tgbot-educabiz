FROM python:3.11-alpine AS base

# for env -S
RUN apk add --no-cache coreutils-env

# --- builder
FROM base AS builder
WORKDIR /app
RUN pip install --no-cache-dir uv

COPY tgbot_educabiz /src/tgbot_educabiz
COPY pyproject.toml uv.lock README.md /src/
RUN uv pip install --target=/app /src

# --- app
FROM base AS app
COPY --from=builder /app /app
ENV PYTHONPATH=/app

EXPOSE 9999

ENTRYPOINT [ "python3", "-m", "tgbot_educabiz" ]

# ------ #

FROM app AS tests

RUN pip install --no-cache-dir uv

WORKDIR /src
COPY tgbot_educabiz tgbot_educabiz
COPY tests tests
COPY pyproject.toml uv.lock README.md .
RUN uv pip install --system --group dev .

ENTRYPOINT [ "" ]
CMD [ "pytest", "--cov" ]

# ------ #

# re-declare "app" as last to make it the default
FROM app
