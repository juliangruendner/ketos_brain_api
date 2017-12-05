import docker
import subprocess
import config

dockerClient = docker.from_env()

dockerClient.login(username=config.DOCKER_REGISTRY_USERNAME, password=config.DOCKER_REGISTRY_PASSWORD, registry=config.DOCKER_REGISTRY_URL)


def wait_for_it(host, port, timeout=0):
    timeout_str = ""
    if timeout >= 0:
        timeout_str = "--timeout=" + str(timeout)

    subprocess.call(["./wait-for-it.sh", str(host) + ":" + str(port), timeout_str])
