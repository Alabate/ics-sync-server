FROM python:3.12-slim

WORKDIR /app

# Install dependencies
COPY pyproject.toml poetry.lock ./
RUN set -ex \
    && pip install --no-cache-dir poetry \
    && poetry install --no-root --no-interaction --no-ansi

# Copy the rest of the application
COPY . . 

# Pre-compile all pycache files
RUN python -m compileall .

EXPOSE 5000
ENV PORT=5000

CMD ["poetry", "run", "gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "main:app"]