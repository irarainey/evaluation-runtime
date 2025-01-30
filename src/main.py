import json
import logging
import os
import uuid
import uvicorn
from dotenv import load_dotenv
from constants import (
    AKS_SECRET_NAME,
    EXECUTION_SCRIPT,
    EXTRACTION_FILE,
    IMAGE_NAME,
    IMAGE_TAG,
    MEDIA_TYPE,
    SAVE_PATH,
)
from utils.azure import azure_login
from utils.docker import DockerWrapper
from utils.evaluation import evaluate
from utils.file import copy_file, delete_all_files_in_path, write_file
from utils.kubernetes import KubernetesWrapper
from fastapi import FastAPI, Form, Response, File, UploadFile
from utils.notebook import convert_notebook_to_script

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

# Load environment variables
load_dotenv()

# Get environment variables
registry_name = os.getenv("ACR_NAME")
resource_group = os.getenv("RESOURCE_GROUP_NAME")
aks_cluster = os.getenv("AKS_NAME")
openai_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
openai_api_key = os.getenv("AZURE_OPENAI_API_KEY")

# Create the FastAPI app
app = FastAPI()


# Define the endpoint to evaluate the code
@app.post("/")
async def evaluation(
    ground_truth: str = Form(...),
    evaluators: str = Form(...),
    extraction: UploadFile = File(...),
    script: UploadFile = File(...),
) -> Response:

    logging.info("Received a request to execute code")

    # Create the full registry and container image names
    fqdn_registry = f"{registry_name}.azurecr.io"
    container_image = f"{fqdn_registry}/{IMAGE_NAME}:{IMAGE_TAG}"

    # Perform Azure login
    try:
        azure_login()
    except Exception as e:
        logging.error(f"Error logging in to Azure: {e}")
        return Response(
            content={"error": str(e)},
            media_type=MEDIA_TYPE,
            status_code=500,
        )

    # Handle the uploaded files for execution
    try:
        # Check if the code directory exists
        os.makedirs(SAVE_PATH, exist_ok=True)

        # Empty out the code directory
        delete_all_files_in_path(SAVE_PATH)

        # Save the uploaded file
        if script.filename.endswith(".ipynb"):
            file_location = os.path.join(SAVE_PATH, script.filename)
            await write_file(script, file_location)
            # Convert the Jupyter Notebook to a Python script
            await convert_notebook_to_script(
                file_location, f"{SAVE_PATH}/{EXECUTION_SCRIPT}"
            )
        else:
            file_location = os.path.join(SAVE_PATH, EXECUTION_SCRIPT)
            await write_file(script, file_location)

        # Save the extraction file contents
        file_location = os.path.join(SAVE_PATH, EXTRACTION_FILE)
        extraction_file = await extraction.read()
        extraction_json = extraction_file.decode('utf-8')
        extraction_content = json.loads(extraction_json)
        await write_file(extraction_content.get("content"), file_location, "w")

        # Copy the Dockerfile from the boilerplate folder to the execution directory
        copy_file("src/boilerplate/Dockerfile", SAVE_PATH)
    except Exception as e:
        logging.error(f"Error handling the uploaded file: {e}")
        return Response(
            content={"error": str(e)},
            media_type=MEDIA_TYPE,
            status_code=500,
        )

    # Attempt to build and push the Docker image
    try:
        # Create a Docker client authenticated with the ACR
        docker = DockerWrapper(fqdn_registry)

        # Build the Docker image
        docker.build(
            path=f"./{SAVE_PATH}",
            tag=container_image,
        )

        # Push the Docker image to the Azure Container Registry
        docker.push(repository=f"{fqdn_registry}/{IMAGE_NAME}", tag=IMAGE_TAG)
    except Exception as e:
        logging.error(f"Error building or pushing Docker image: {e}")
        return Response(
            content={"error": str(e)},
            media_type=MEDIA_TYPE,
            status_code=500,
        )

    # Attempt to execute the job on the Azure Kubernetes Service
    try:
        # Create a Kubernetes client
        aks = KubernetesWrapper(resource_group, aks_cluster)

        # Create job and pod names
        job_id = uuid.uuid4()
        pod_name = f"execution-pod-{job_id}"
        job_name = f"execution-job-{job_id}"

        # Create the secrets, container, pod, and job
        secret_data = {
            "AZURE_OPENAI_ENDPOINT": openai_endpoint,
            "AZURE_OPENAI_API_KEY": openai_api_key,
        }

        aks.create_secrets(AKS_SECRET_NAME, secret_data)
        container = aks.create_container(container_image, job_name)
        pod_spec = aks.create_pod_template(pod_name, container)
        job = aks.create_job(job_name, pod_spec)

        # Execute the job
        aks.execute_job(job)

        # Poll the pod status until it is completed
        if aks.wait_for_pod_completion(job_name) is False:
            raise Exception("Job did not complete successfully")

        # Capture the logs from the pod for the job
        logs = aks.get_logs(job_name)

        # Create the data for evaluation
        data = dict(
            response=logs,
            ground_truth=ground_truth,
        )

        # Perform the evaluation
        evaluator_list = evaluators.split(",")
        eval_results = evaluate(evaluator_list, data)

    except Exception as e:
        logging.error(f"Error executing job: {e}")
        return Response(
            content={"error": str(e)},
            media_type=MEDIA_TYPE,
            status_code=500,
        )

    logging.info("Job execution completed successfully")

    response_content = {
        "response": logs,
        "ground_truth": ground_truth,
        "evaluation": eval_results,
    }

    # Return the response
    return Response(
        content=json.dumps(response_content),
        media_type=MEDIA_TYPE,
        status_code=200,
    )


# Entry point of the script
if __name__ == "__main__":
    # Create the Uvicorn server
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)
