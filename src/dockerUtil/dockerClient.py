import os
import docker

dockerClient = docker.from_env()

# TODO: certificate for registry...

# username = os.environ.get('DOCKER_USERNAME')
# password = os.environ.get('DOCKER_PASSWORD')
# registry = os.environ.get('DOCKER_REGISTRY')
# dockerClient.login(username=username, password=password, registry=registry)
