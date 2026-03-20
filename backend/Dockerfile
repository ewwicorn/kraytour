FROM python:3.11-slim

WORKDIR /app

COPY pyproject.toml ./

RUN pip install --no-cache-dir \
    "fastapi>=0.135.1,<0.136.0" \
    "uvicorn[standard]>=0.42.0,<0.43.0" \
    "sqlalchemy>=2.0.48,<3.0.0" \
    "asyncpg>=0.31.0,<0.32.0" \
    "alembic>=1.18.4,<2.0.0" \
    "python-jose[cryptography]>=3.5.0,<4.0.0" \
    "bcrypt==4.0.1" \
    "passlib[bcrypt]>=1.7.4,<2.0.0" \
    "pydantic-settings>=2.13.1,<3.0.0" \
    "python-multipart>=0.0.22,<0.0.23" \
    "pydantic[email]>=2.12.5,<3.0.0" \
    "psycopg2-binary>=2.9.11,<3.0.0" \
    "minio>=7.2.0,<8.0.0"

COPY . .
