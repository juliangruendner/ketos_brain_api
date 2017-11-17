import os
import docker

dockerClient = docker.from_env()

username = os.environ.get('DOCKER_USERNAME')
password = os.environ.get('DOCKER_PASSWORD')
registry = os.environ.get('DOCKER_REGISTRY')
dockerClient.login(username=username, password=password, registry=registry)
