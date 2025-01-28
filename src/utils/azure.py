import json
import os
import subprocess
from azure.identity import DefaultAzureCredential


def is_running_in_azure():
    return "MSI_ENDPOINT" in os.environ or "MSI_SECRET" in os.environ


def azure_login():
    if is_running_in_azure():
        print("Using Managed Identity for Azure login...")
        subprocess.run(["az", "login", "--identity"], check=True)
    else:
        print("Using DefaultAzureCredential for Azure login...")
        credential = DefaultAzureCredential()
        _ = credential.get_token("https://management.azure.com/.default")
        print("Successfully authenticated using DefaultAzureCredential.")


def authenticate_acr(registry_name):
    result = subprocess.run(
        ["az", "acr", "login", "--name", registry_name, "--expose-token"],
        capture_output=True,
        text=True,
        check=True,
    )
    token_info = json.loads(result.stdout)
    access_token = token_info["accessToken"]
    return access_token
