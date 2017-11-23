import os
import docker
import subprocess


docker_registry_domain = os.environ.get('DOCKER_REGISTRY_DOMAIN')

dockerClient = docker.from_env()

username = os.environ.get('DOCKER_USERNAME')
password = os.environ.get('DOCKER_PASSWORD')
registry = os.environ.get('DOCKER_REGISTRY')
dockerClient.login(username=username, password=password, registry=registry)


def wait_for_it(host, port, timeout=0):
    timeout_str = ""
    if timeout >= 0:
        timeout_str = "--timeout=" + str(timeout)

    subprocess.call(["./wait-for-it.sh", str(host) + ":" + str(port), timeout_str])
