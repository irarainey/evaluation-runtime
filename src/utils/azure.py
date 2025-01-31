import json
import logging
import subprocess
from azure.identity import DefaultAzureCredential


def azure_login():
    """
    Authenticate with Azure using the DefaultAzureCredential.
    """
    logging.info("Using DefaultAzureCredential for Azure login...")
    credential = DefaultAzureCredential()
    _ = credential.get_token("https://management.azure.com/.default")


def authenticate_acr(registry_name):
    """
    Authenticate with the Azure Container Registry.

    Parameters:
    - registry_name (str): The name of the Azure Container Registry.
    """
    result = subprocess.run(
        ["az", "acr", "login", "--name", registry_name, "--expose-token"],
        capture_output=True,
        text=True,
        check=True,
    )
    token_info = json.loads(result.stdout)
    access_token = token_info["accessToken"]
    return access_token
