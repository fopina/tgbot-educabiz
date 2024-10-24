FROM python:3.11-alpine AS app

# for env -S
RUN apk add --no-cache coreutils-env

RUN pip install --no-cache-dir pipenv

WORKDIR /app

COPY Pipfile* .
RUN pipenv requirements > x.txt \
 && pip install --no-cache-dir -r x.txt \
 && rm x.txt

COPY tgbot_educabiz tgbot_educabiz

ENTRYPOINT [ "python3", "-m", "tgbot_educabiz" ]

# ------ #

FROM app AS tests

RUN pipenv requirements --dev > x.txt \
 && pip install --no-cache-dir -r x.txt \
 && rm x.txt

COPY tests tests
COPY pyproject.toml .

ENTRYPOINT [ "" ]
CMD [ "pytest", "--cov" ]

# ------ #

# re-declare "app" as last to make it the default
FROM app
