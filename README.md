# Python Execution Engine Test

This repository contains a simple Python execution engine that can execute Python code and Jupyter notebooks on the fly. It does this by building a Docker image with the necessary dependencies and running the code in a container on an AKS Cluster.

The engine is built using FastAPI and takes in a single POST request with a file containing the file to be executed. The engine will then execute the file and return the output. Two sample files are included in the `samples` directory and can be run using the following commands:

```bash
curl -X POST "http://127.0.0.1:8000/execute" -F "file=@samples/test.py"
```

```bash
curl -X POST "http://127.0.0.1:8000/execute" -F "file=@samples/test.ipynb"
```

## Prerequisites

- Azure CLI (installed locally)
- Azure Kubernetes Service (AKS)
- Azure Container Registry (ACR)

## Setup

Copy the `.env.example` file to `.env` and fill in the necessary values.
