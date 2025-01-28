# Use the official Python 3.11 image from the Docker Hub
FROM python:3.11-slim

# Set the working directory
WORKDIR /usr/src/app

# Copy the local file with the Python script to the container
COPY code/main.py .

# Run the Python script when the container launches
CMD ["python", "main.py"]
