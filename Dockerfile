# ==================================== #
# ======= DOCKER BUILDER IMAGE ======= #
# ==================================== #

FROM python:3.12-slim AS builder

# Set up environmental variables
ENV \
    LANG=C.UTF-8 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONFAULTHANDLER=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Install uv (https://github.com/astral-sh/uv)
RUN pip install uv

# Copy project files
COPY pyproject.toml ./
COPY src/ ./src/

# Create and activate a virtual environment, then install dependencies
RUN python -m venv /.venv \
    && . /.venv/bin/activate \
    && uv pip install -e .

# ==================================== #
# ======= DOCKER RUNTIME IMAGE ======= #
# ==================================== #

FROM python:3.12-slim AS runtime

WORKDIR /app

# Install Playwright system dependencies
RUN apt-get update && apt-get install -y \
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libdbus-1-3 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libpango-1.0-0 \
    libcairo2 \
    libasound2 \
    libatspi2.0-0 \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Copy the virtual environment from builder
COPY --from=builder /.venv /.venv

# Use executables from the virtual environment
ENV PATH="/.venv/bin:$PATH"

# Install Playwright browsers (chromium only)
RUN playwright install chromium --with-deps

# Copy application code
COPY src/ ./src/

# Run the application
EXPOSE 8080
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8080"]
