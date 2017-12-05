import docker
import subprocess
import config
import os


dockerClient = docker.from_env()

print('group!! {}'.format(os.getegid()))
print('user id!! {}'.format(os.getuid()))
print('user!! {}'.format(os.path.expanduser('~')))

print(config.DOCKER_REGISTRY_USERNAME)
print(config.DOCKER_REGISTRY_PASSWORD)
print(config.DOCKER_REGISTRY_URL)
dockerClient.login(username=config.DOCKER_REGISTRY_USERNAME, password=config.DOCKER_REGISTRY_PASSWORD, registry=config.DOCKER_REGISTRY_URL)


def wait_for_it(host, port, timeout=0):
    timeout_str = ""
    if timeout >= 0:
        timeout_str = "--timeout=" + str(timeout)

    subprocess.call(["./wait-for-it.sh", str(host) + ":" + str(port), timeout_str])
