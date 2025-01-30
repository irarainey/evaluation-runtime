# Evaluation Runtime

This repository contains a simple Python execution and evaluation engine that can run Python scripts or Jupyter notebooks which make calls to Azure OpenAI and perform evaluation of the output. It does this by dynamically building a Docker image with the necessary dependencies and running the container on an Azure Kubernetes Service instance.

The project uses FastAPI and takes in a single POST request with a file containing the file to be executed. The engine will then execute the file and return the output. A sample notebook is included in the `samples` directory and can be run using the following commands:

```bash
curl -X POST "http://127.0.0.1:8000/" -F "file=@samples/prompt.ipynb"
```

## Prerequisites

- Azure CLI (installed locally)
- Docker (installed locally)
- Azure Kubernetes Service (AKS)
- Azure Container Registry (ACR)

## Setup

Copy the `.env.example` file to `.env` and fill in the necessary values for the required Azure services.

Run `poetry install` to install the required dependencies.

## Running the Engine

Run the following command to start the FastAPI server by pressing `F5` in Visual Studio Code.
