import os
import docker

docker_registry_domain = os.environ.get('DOCKER_REGISTRY_DOMAIN')

dockerClient = docker.from_env()

username = os.environ.get('DOCKER_USERNAME')
password = os.environ.get('DOCKER_PASSWORD')
registry = os.environ.get('DOCKER_REGISTRY')
dockerClient.login(username=username, password=password, registry=registry)
