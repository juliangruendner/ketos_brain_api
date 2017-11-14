from flask_restful import Resource
from dockerUtil.dockerClient import dockerClient


class DockerResource(Resource):
    def __init__(self):
        super(DockerResource, self).__init__()

    def post(self):
        ret = dockerClient.containers.run("ubuntu:latest", detach=True)

        return ret.id, 201
