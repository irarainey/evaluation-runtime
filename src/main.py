import os
import uuid
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

    job_id = uuid.uuid4()
    pod_id = job_id
    pod_name = f"my-job-pod-{pod_id}"
    job_name = f"my-job-{job_id}"

    container = aks.create_container(container_image, "execution", "Always")
    pod_spec = aks.create_pod_template(pod_name, container)
    job = aks.create_job(job_name, pod_spec)
    aks.execute_job(job)

    # Poll the pod status until it is running
    if aks.wait_for_pod_ready(job_name) is False:
        raise RuntimeError("Job did not start within the expected time")

    # Capture the logs from the pod
    logs = aks.get_logs(job_name)

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
