import logging
import docker
from utils.azure import authenticate_acr


class DockerWrapper:
    """
    A wrapper class for the Docker SDK.

    Parameters:
    - registry (str): The fully qualified domain name (FQDN) of the Azure Container Registry (ACR).
    """

    def __init__(self, registry):
        self.client = docker.from_env()
        self.login(registry)

    def login(self, registry: str):
        """
        Log in to the Azure Container Registry (ACR).

        Parameters:
        - registry (str): The fully qualified domain name (FQDN) of the Azure Container Registry (ACR).
        """
        logging.info(f"Logging docker in to {registry}")
        access_token = authenticate_acr(registry)
        self.client.login(
            username="00000000-0000-0000-0000-000000000000",
            password=access_token,
            registry=registry,
        )

    def build(self, path, tag):
        """
        Build a Docker image.

        Parameters:
        - path (str): The path to the directory containing the Dockerfile.
        - tag (str): The tag to apply to the Docker image.
        """
        logging.info(f"Building Dockerfile at {path} with tag {tag}")
        self.client.images.build(path=path, tag=tag)

    def push(self, repository, tag):
        """
        Push a Docker image to a container registry.

        Parameters:
        - repository (str): The name of the repository to push the image to.
        - tag (str): The tag to apply to the Docker image.
        """
        logging.info(f"Pushing image to repository {repository} with tag {tag}")
        self.client.images.push(repository=repository, tag=tag)
