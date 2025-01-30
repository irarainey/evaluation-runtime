import logging
import subprocess
import time
from kubernetes import config, client


class KubernetesWrapper:
    """
    A wrapper class for the Kubernetes SDK.

    Parameters:
    - resource_group_name (str): The name of the Azure resource group.
    - aks_cluster_name (str): The name of the Azure Kubernetes Service (AKS) cluster.
    - namespace (str): The Kubernetes namespace to use (default is 'default').
    """

    def __init__(self, resource_group_name, aks_cluster_name, namespace="default"):
        self.resource_group_name = resource_group_name
        self.aks_cluster_name = aks_cluster_name
        self.namespace = namespace
        self.authenticate(resource_group_name, aks_cluster_name)
        self.core = client.CoreV1Api()

    def authenticate(self, resource_group_name, aks_cluster_name):
        """
        Authenticate with the Azure Kubernetes Service (AKS) cluster.

        Parameters:
        - resource_group_name (str): The name of the Azure resource group.
        - aks_cluster_name (str): The name of the Azure Kubernetes Service (AKS) cluster.
        """
        subprocess.run(
            [
                "az",
                "aks",
                "get-credentials",
                "--resource-group",
                resource_group_name,
                "--name",
                aks_cluster_name,
            ],
            check=True,
        )

        config.load_kube_config()

    def create_secrets(self, secret_name, secret_data):
        """
        Create a Kubernetes secret.

        Parameters:
        - secret_name (str): The name to assign to the secret.
        - data (dict): The data to store in the secret.
        """
        logging.info(f"Creating secret with name: {secret_name}")

        # Create the Secret object
        secret = client.V1Secret(
            api_version="v1",
            kind="Secret",
            metadata=client.V1ObjectMeta(name=secret_name),
            type="Opaque",
            string_data=secret_data,
        )

        # Create the Secret in Kubernetes
        core_v1_api = client.CoreV1Api()

        # Check to see if the secret already exists and if so just update it
        try:
            # Attempt to read the existing Secret
            core_v1_api.read_namespaced_secret(
                name=secret_name, namespace=self.namespace
            )
            print(f"Secret '{secret_name}' exists. Updating it.")

            # Update the existing Secret
            core_v1_api.replace_namespaced_secret(
                name=secret_name, namespace=self.namespace, body=secret
            )
        except Exception as e:
            if e.status == 404:
                # Secret does not exist; create it
                print(f"Secret '{secret_name}' does not exist. Creating it.")
                core_v1_api.create_namespaced_secret(
                    namespace=self.namespace, body=secret
                )
            else:
                raise e

    def create_container(self, image, name, pull_policy="Always"):
        """
        Create a container definition for a Kubernetes pod.

        Parameters:
        - image (str): The name of the Docker image to use.
        - name (str): The name to assign to the container.
        - pull_policy (str): The image pull policy to use (default is 'Always').
        """
        logging.info(f"Creating container with image: {image}")

        container = client.V1Container(
            image=image,
            name=name,
            image_pull_policy=pull_policy,
            env=[
                client.V1EnvVar(
                    name="AZURE_OPENAI_ENDPOINT",
                    value_from=client.V1EnvVarSource(
                        secret_key_ref=client.V1SecretKeySelector(
                            name="azure-openai-secrets",
                            key="AZURE_OPENAI_ENDPOINT",
                        )
                    ),
                ),
                client.V1EnvVar(
                    name="AZURE_OPENAI_API_KEY",
                    value_from=client.V1EnvVarSource(
                        secret_key_ref=client.V1SecretKeySelector(
                            name="azure-openai-secrets",
                            key="AZURE_OPENAI_API_KEY",
                        )
                    ),
                ),
            ],
        )
        return container

    def create_pod_template(self, pod_name, container):
        """
        Create a pod template for a Kubernetes job.

        Parameters:
        - pod_name (str): The name to assign to the pod.
        - container (V1Container): The container definition to use.
        """
        logging.info(f"Creating pod template with name: {pod_name}")
        pod_template = client.V1PodTemplateSpec(
            spec=client.V1PodSpec(restart_policy="Never", containers=[container]),
            metadata=client.V1ObjectMeta(name=pod_name, labels={"pod_name": pod_name}),
        )
        return pod_template

    def create_job(self, job_name, pod_template):
        """
        Create a job definition for a Kubernetes job.

        Parameters:
        - job_name (str): The name to assign to the job.
        - pod_template (V1PodTemplateSpec): The pod template to use.
        """
        logging.info(f"Creating job with name: {job_name}")
        metadata = client.V1ObjectMeta(name=job_name, labels={"job_name": job_name})
        job = client.V1Job(
            api_version="batch/v1",
            kind="Job",
            metadata=metadata,
            spec=client.V1JobSpec(backoff_limit=0, template=pod_template),
        )
        return job

    def execute_job(self, job):
        """
        Execute a Kubernetes job.

        Parameters:
        - job (V1Job): The job definition to execute.
        """
        logging.info(f"Executing job: {job.metadata.name}")
        batch_api = client.BatchV1Api()
        batch_api.create_namespaced_job(self.namespace, job)

    def wait_for_pod_completion(self, job_name):
        """
        Wait for a Kubernetes job to complete.

        Parameters:
        - job_name (str): The name of the job to wait for.
        """
        logging.info("Waiting for job to complete...")
        pod_ready = False
        for _ in range(30):  # Try for 30 iterations (30 x 2 = 60 seconds)
            pods = self.core.list_namespaced_pod(
                namespace=self.namespace, label_selector=f"job-name={job_name}"
            )
            if pods.items:
                logging.info(f"Pod status: {pods.items[0].status.phase}")
                pod_status = pods.items[0].status.phase
                if pod_status == "Succeeded":
                    pod_ready = True
                    break
                elif pod_status == "Failed":
                    raise RuntimeError("Job failed to complete")
            time.sleep(2)
        return pod_ready

    def get_logs(self, job_name):
        """
        Get logs from a Kubernetes pod.

        Parameters:
        - job_name (str): The name of the job to get logs for.
        """
        logging.info(f"Getting logs from pod for job {job_name}...")
        pods = self.core.list_namespaced_pod(
            namespace=self.namespace, label_selector=f"job-name={job_name}"
        )
        pod_name = pods.items[0].metadata.name
        logs = self.core.read_namespaced_pod_log(
            name=pod_name, namespace=self.namespace
        )
        return logs
