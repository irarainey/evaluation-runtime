import json
import logging
import os
import subprocess
from azure.identity import DefaultAzureCredential


def is_running_in_azure():
    """
    Check if the code is running in Azure.
    """
    return "MSI_ENDPOINT" in os.environ or "MSI_SECRET" in os.environ


def azure_login():
    """
    Authenticate with Azure using the DefaultAzureCredential or az login for Managed Identity.
    """
    if is_running_in_azure():
        logging.info("Using Managed Identity for Azure login...")
        subprocess.run(["az", "login", "--identity"], check=True)
    else:
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
