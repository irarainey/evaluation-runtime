import os
import json
import logging
import subprocess
from azure.identity import DefaultAzureCredential, ClientSecretCredential


def is_running_in_docker():
    return (
        os.path.exists("/.dockerenv") or "docker" in open("/proc/1/cgroup", "rt").read()
    )


def azure_login():
    """
    Authenticate with Azure using DefaultAzureCredential or ClientSecretCredential.
    """
    if is_running_in_docker():
        logging.info("Using ClientSecretCredential for Azure login...")
        credential = ClientSecretCredential(
            tenant_id=os.getenv("AZURE_TENANT_ID"),
            client_id=os.getenv("AZURE_CLIENT_ID"),
            client_secret=os.getenv("AZURE_CLIENT_SECRET"),
        )
    else:
        # Clear any environment variables to ensure local account is used
        if "AZURE_CLIENT_ID" in os.environ:
            del os.environ["AZURE_CLIENT_ID"]
        if "AZURE_CLIENT_SECRET" in os.environ:
            del os.environ["AZURE_CLIENT_SECRET"]
        if "AZURE_TENANT_ID" in os.environ:
            del os.environ["AZURE_TENANT_ID"]
        logging.info("Using DefaultAzureCredential for Azure login...")
        credential = DefaultAzureCredential()

    # Get the access token which we don't use but it is required to authenticate
    _ = credential.get_token("https://management.azure.com/.default")


def authenticate_acr(registry_name):
    """
    Authenticate with the Azure Container Registry.

    Parameters:
    - registry_name (str): The name of the Azure Container Registry.
    """
    logging.info(f"Authenticating with {registry_name}")
    result = subprocess.run(
        ["az", "acr", "login", "--name", registry_name, "--expose-token"],
        capture_output=True,
        text=True,
        check=True,
    )
    token_info = json.loads(result.stdout)
    access_token = token_info["accessToken"]
    return access_token
