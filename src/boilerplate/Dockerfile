# Use the official Python 3.11 image from the Docker Hub
FROM python:3.11-slim

# Set the working directory
WORKDIR /usr/src/app

# Copy the uploaded files to the container
COPY main.py .
COPY extraction.txt .

# Install the required Python packages
COPY requirements.txt .
RUN pip install -r requirements.txt

# Run the Python script when the container launches
CMD ["python", "main.py"]
