from flask import Flask, abort, request, jsonify, g, url_for
from flask_restful import Resource, Api, reqparse, abort, fields, marshal_with
from rdb.rdb import db
from flask_httpauth import HTTPBasicAuth
from dockerUtil.dockerClient import dockerClient

class DockerResource(Resource):
    def __init__(self):
        super(DockerResource, self).__init__()

    def post(self):
        ret = dockerClient.containers.run("ubuntu:latest", detach=True)

        return ret.id, 201