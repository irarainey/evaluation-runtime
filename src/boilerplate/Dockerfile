# Use the official Python 3.13 image from the Docker Hub
FROM python:3.13-slim

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/

# Set the working directory
WORKDIR /usr/src/app

# Copy the uploaded files to the container
COPY main.py .
COPY extraction.txt .

# Install the required Python packages
COPY pyproject.toml .
RUN uv sync --frozen --no-dev

# Run the Python script when the container launches
CMD ["uv", "run", "python", "main.py"]
