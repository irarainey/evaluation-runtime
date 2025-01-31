# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Install Azure CLI
RUN apt-get update -y \
    && apt-get install -y apt-transport-https ca-certificates curl gnupg lsb-release \
    && curl -fsSL https://packages.microsoft.com/keys/microsoft.asc | apt-key add - \
    && echo "deb [arch=amd64] https://packages.microsoft.com/repos/azure-cli/ $(lsb_release -cs) main" > /etc/apt/sources.list.d/azure-cli.list \
    && apt-get update -y \
    && apt-get install -y azure-cli \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Docker
RUN apt-get update && apt-get install -y --no-install-recommends docker.io \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory inside the container
WORKDIR /app

# Install Poetry
RUN pip install --no-cache-dir poetry \
    && rm -rf /root/.cache/pipdocker

# Copy the entire application to the working directory
COPY . .

# Install dependencies via Poetry
RUN poetry config virtualenvs.create false \
    && poetry install --no-root --no-interaction --no-ansi \
    && rm -rf /root/.cache/pypoetry

# Expose the port that your application will run on
EXPOSE 8000

# Specify the command to run your application using uvicorn
CMD ["python", "src/main.py"]
