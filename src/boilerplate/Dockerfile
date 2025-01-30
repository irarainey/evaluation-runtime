# Use the official Python 3.11 image from the Docker Hub
FROM python:3.11-slim

# Set the working directory
WORKDIR /usr/src/app

# Copy the local file with the Python script to the container
COPY main.py .
COPY extraction.txt .

# Set environment variables
ENV AZURE_OPENAI_ENDPOINT=""
ENV AZURE_OPENAI_API_KEY=""

RUN pip install openai

# Run the Python script when the container launches
CMD ["python", "main.py"]
