import os
import uvicorn
from dotenv import load_dotenv
from utils.azure import azure_login
from utils.docker import DockerWrapper
from utils.kubernetes import KubernetesWrapper
from fastapi import FastAPI, Response, File, UploadFile


app = FastAPI()


@app.post("/execute")
async def execute(file: UploadFile = File(...)) -> Response:

    # Get environment variables
    registry_name = os.getenv("ACR_NAME")
    image_name = os.getenv("IMAGE_NAME")
    image_tag = os.getenv("IMAGE_TAG")
    resource_group_name = os.getenv("RESOURCE_GROUP_NAME")
    aks_cluster_name = os.getenv("AKS_NAME")
    fqdn_registry = f"{registry_name}.azurecr.io"
    container_image = f"{fqdn_registry}/{image_name}:{image_tag}"
    app_name = "my-app"
    service_name = "execution-service"
    deployment_name = "execution-deployment"

    # Perform Azure login
    azure_login()

    # Check if the code directory exists
    save_path = "src/boilerplate/code/"
    os.makedirs(save_path, exist_ok=True)

    # Read and save the uploaded file
    file_location = os.path.join(save_path, "main.py")
    with open(file_location, "wb") as f:
        f.write(await file.read())

    # Create a Docker client authenticated with the ACR
    docker = DockerWrapper(fqdn_registry)

    # Build the Docker image
    docker.build(
        path="./src/boilerplate",
        tag=container_image,
    )

    # Push the Docker image to the Azure Container Registry
    docker.push(repository=f"{fqdn_registry}/{image_name}", tag=image_tag)

    # Create a Kubernetes client
    aks = KubernetesWrapper(resource_group_name, aks_cluster_name)

    print("Setting up deployment and service...")

    # Check if the service exists
    if aks.check_service_exists(service_name) is False:
        aks.create_service(service_name, app_name)

    # Check if the deployment exists
    existing_deployment = aks.get_existing_deployment(deployment_name)

    if existing_deployment is not None:
        # Update the existing deployment with the new image
        aks.update_deployment(
            existing_deployment, deployment_name, container_image
        )
    else:
        # Create a new deployment if it doesn't exist
        aks.create_deployment(deployment_name, container_image, app_name)

    print("Deployment and service are set up. Waiting for pod to start...")

    # Poll the pod status until it is running
    if aks.wait_for_pod_ready(app_name) is False:
        raise RuntimeError("Pod did not start within the expected time")

    print("Pod is running. Fetching logs...")

    # Capture the logs from the pod
    logs = aks.get_logs(app_name)

    # Return the response
    return Response(
        content=logs,
        media_type="application/json",
        status_code=200,
    )


# Entry point of the script
if __name__ == "__main__":
    # Load environment variables
    load_dotenv()

    # Create the Uvicorn server
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)
