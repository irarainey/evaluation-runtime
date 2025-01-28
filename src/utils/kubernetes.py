import subprocess
import time
from kubernetes import config, client


class KubernetesWrapper:
    def __init__(self, resource_group_name, aks_cluster_name, namespace="default"):
        self.resource_group_name = resource_group_name
        self.aks_cluster_name = aks_cluster_name
        self.namespace = namespace
        self.authenticate(resource_group_name, aks_cluster_name)
        self.apps = client.AppsV1Api()
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

    def get_existing_deployment(self, name):
        try:
            existing_deployment = self.apps.read_namespaced_deployment(
                name=name, namespace=self.namespace
            )
            return existing_deployment
        except client.exceptions.ApiException as e:
            if e.status == 404:
                return None
            else:
                raise

    def update_deployment(self, deployment, name, container_image):
        print("Updating existing deployment with the new image...")
        deployment.spec.template.spec.containers[0].image = container_image
        self.apps.patch_namespaced_deployment(
            name=name, namespace=self.namespace, body=deployment
        )

    def create_deployment(self, name, container_image, app_name):
        print(f"Creating a new deployment: {name}...")
        deployment = client.V1Deployment(
            api_version="apps/v1",
            kind="Deployment",
            metadata=client.V1ObjectMeta(name=name),
            spec=client.V1DeploymentSpec(
                replicas=1,
                selector=client.V1LabelSelector(match_labels={"app": app_name}),
                template=client.V1PodTemplateSpec(
                    metadata=client.V1ObjectMeta(labels={"app": app_name}),
                    spec=client.V1PodSpec(
                        containers=[
                            client.V1Container(
                                name=f"{name}-container",
                                image=container_image,
                                ports=[client.V1ContainerPort(container_port=80)],
                            )
                        ],
                        image_pull_secrets=[
                            client.V1LocalObjectReference(name="acr-secret")
                        ],
                    ),
                ),
            ),
        )
        self.apps.create_namespaced_deployment(
            namespace=self.namespace, body=deployment
        )

    def check_service_exists(self, name):
        try:
            _ = self.core.read_namespaced_service(name=name, namespace=self.namespace)
            return True
        except client.exceptions.ApiException as e:
            if e.status == 404:
                return False
            else:
                raise

    def create_service(self, name, app_name):
        print(f"Creating a new service: {name}...")
        service = client.V1Service(
            api_version="v1",
            kind="Service",
            metadata=client.V1ObjectMeta(name=name),
            spec=client.V1ServiceSpec(
                selector={"app": app_name},
                ports=[client.V1ServicePort(port=80, target_port=80)],
                type="LoadBalancer",
            ),
        )
        self.core.create_namespaced_service(namespace=self.namespace, body=service)

    def wait_for_pod_ready(self, app_name):
        pod_ready = False
        for _ in range(30):  # Try for 30 iterations (30 x 2 = 60 seconds)
            pods = self.core.list_namespaced_pod(
                namespace=self.namespace, label_selector=f"app={app_name}"
            )
            if pods.items:
                pod_status = pods.items[0].status.phase
                if pod_status == "Running":
                    pod_ready = True
                    break
            time.sleep(2)

        return pod_ready

    def get_logs(self, app_name):
        pods = self.core.list_namespaced_pod(
            namespace=self.namespace, label_selector=f"app={app_name}"
        )
        pod_name = pods.items[0].metadata.name
        logs = self.core.read_namespaced_pod_log(
            name=pod_name, namespace=self.namespace
        )
        return logs
