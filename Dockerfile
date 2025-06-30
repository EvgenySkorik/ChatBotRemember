FROM python:3.12-slim

WORKDIR /app

RUN echo 'Acquire::Retries "5";' > /etc/apt/apt.conf.d/80-retries && \
    echo 'Acquire::http::Timeout "120";' >> /etc/apt/apt.conf.d/80-retries && \
    echo 'Acquire::https::Timeout "120";' >> /etc/apt/apt.conf.d/80-retries && \
    apt-get update && \
    apt-get install -y --no-install-recommends libpq-dev && \
    rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir poetry==2.1.3

COPY pyproject.toml poetry.lock ./

# COPY app ./app
# COPY database ./database
# COPY alembic ./alembic


RUN poetry config virtualenvs.create false && \
    poetry install --only main --no-interaction --no-ansi --no-root

COPY . .
ENV PYTHONPATH="/app:${PYTHONPATH}"

#
# RUN echo "Содержимое /app:" && ls -la && \
#     echo "Содержимое /app/app:" && ls -la app/ && \
#     echo "Содержимое /app/database:" && ls -la database/ && \
#     echo "Содержимое /app/alembic:" && ls -la alembic/



CMD ["poetry", "run", "python", "app/run.py"]