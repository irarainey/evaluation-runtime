import subprocess
import time
from kubernetes import config, client


class KubernetesWrapper:
    def __init__(self, resource_group_name, aks_cluster_name, namespace="default"):
        self.resource_group_name = resource_group_name
        self.aks_cluster_name = aks_cluster_name
        self.namespace = namespace
        self.authenticate(resource_group_name, aks_cluster_name)
        self.core = client.CoreV1Api()

    def authenticate(self, resource_group_name, aks_cluster_name):
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

    def create_container(self, image, name, pull_policy):
        print(f"Creating container with image: {image}")
        container = client.V1Container(
            image=image, name=name, image_pull_policy=pull_policy
        )
        return container

    def create_pod_template(self, pod_name, container):
        print(f"Creating pod template with name: {pod_name}")
        pod_template = client.V1PodTemplateSpec(
            spec=client.V1PodSpec(restart_policy="Never", containers=[container]),
            metadata=client.V1ObjectMeta(name=pod_name, labels={"pod_name": pod_name}),
        )
        return pod_template

    def create_job(self, job_name, pod_template):
        print(f"Creating job with name: {job_name}")
        metadata = client.V1ObjectMeta(name=job_name, labels={"job_name": job_name})
        job = client.V1Job(
            api_version="batch/v1",
            kind="Job",
            metadata=metadata,
            spec=client.V1JobSpec(backoff_limit=0, template=pod_template),
        )
        return job

    def execute_job(self, job):
        print(f"Executing job: {job.metadata.name}")
        batch_api = client.BatchV1Api()
        batch_api.create_namespaced_job(self.namespace, job)

    def wait_for_pod_ready(self, job_name):
        print("Waiting for job to complete...")
        pod_ready = False
        for _ in range(30):  # Try for 30 iterations (30 x 2 = 60 seconds)
            pods = self.core.list_namespaced_pod(
                namespace=self.namespace, label_selector=f"job-name={job_name}"
            )
            if pods.items:
                print(f"Pod status: {pods.items[0].status.phase}")
                pod_status = pods.items[0].status.phase
                if pod_status == "Succeeded":
                    pod_ready = True
                    break
            time.sleep(2)
        return pod_ready

    def get_logs(self, job_name):
        print(f"Getting logs from pod for job {job_name}...")
        pods = self.core.list_namespaced_pod(
            namespace=self.namespace, label_selector=f"job-name={job_name}"
        )
        pod_name = pods.items[0].metadata.name
        logs = self.core.read_namespaced_pod_log(
            name=pod_name, namespace=self.namespace
        )
        return logs
