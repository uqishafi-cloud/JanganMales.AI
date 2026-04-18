FROM python:3.11-slim

# Ensure logs are streamed in real-time
ENV PYTHONUNBUFFERED=1

# Set WORKDIR ke /app
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH="/root/.local/bin:$PATH"

# Copy only dependency specification files
COPY pyproject.toml poetry.lock* README.md ./

# Install project dependencies
RUN poetry config virtualenvs.create false \
    && poetry install --only main --no-interaction --no-ansi

# Copy the rest of the application code
COPY src ./src

# Set PYTHONPATH agar Python dapat menemukan module "agent" yang berada di dalam "src"
ENV PYTHONPATH="/app/src"

# Cloud Run by default injects the PORT environment variable.
EXPOSE 8080

# Set the command to run the FastAPI server
CMD ["sh", "-c", "uvicorn src.api.main:app --host 0.0.0.0 --port ${PORT:-8080}"]