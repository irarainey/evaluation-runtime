import docker
from utils.azure import authenticate_acr


class DockerWrapper:
    def __init__(self, registry: str):
        self.client = docker.from_env()
        self.login(registry)

    def login(self, registry: str):
        access_token = authenticate_acr(registry)
        self.client.login(username="00000000-0000-0000-0000-000000000000", password=access_token, registry=registry)

    def build(self, path: str, tag: str):
        self.client.images.build(path=path, tag=tag)

    def push(self, repository: str, tag: str):
        self.client.images.push(repository=repository, tag=tag)
