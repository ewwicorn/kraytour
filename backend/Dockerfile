FROM python:3.11-slim

RUN pip config set global.index-url https://mirrors.aliyun.com/pypi/simple/ && \
    pip config set global.trusted-host mirrors.aliyun.com && \
    pip install --no-cache-dir poetry

WORKDIR /app

COPY pyproject.toml poetry.lock* ./

RUN touch README.md

RUN poetry config virtualenvs.create false && poetry install --no-interaction --no-ansi --no-root -v

COPY . .
