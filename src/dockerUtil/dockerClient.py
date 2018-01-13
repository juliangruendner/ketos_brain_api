import docker
import subprocess
import config
import logging
logger = logging.getLogger(__name__)

try:
    dockerClient = docker.from_env()
    dockerClient.login(username=config.DOCKER_REGISTRY_USERNAME, password=config.DOCKER_REGISTRY_PASSWORD, registry=config.DOCKER_REGISTRY_URL)
except Exception as e:
    logger.error("Error when connecting to docker registry: ", exc_info=True)

def wait_for_it(host, port, timeout=0):
    timeout_str = ""
    if timeout >= 0:
        timeout_str = "--timeout=" + str(timeout)

    subprocess.call(["./wait-for-it.sh", str(host) + ":" + str(port), timeout_str])
