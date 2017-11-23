from flask import g
from flask_restful import Resource, reqparse, abort, fields, marshal_with
from rdb.rdb import db
from rdb.models.environment import Environment
from rdb.models.user import User
from rdb.models.image import Image
from dockerUtil.dockerClient import dockerClient, docker_registry_domain
from resources.userResource import auth
import subprocess
import requests
import uuid

parser = reqparse.RequestParser()
parser.add_argument('name', type=str, required=True, help='No environment name provided', location='json')
parser.add_argument('description', type=str, required=False, location='json')
parser.add_argument('image_id', type=int, required=True, help='No image id provided', location='json')

environment_fields = {
    'id': fields.Integer,
    'name': fields.String,
    'jupyter_port': fields.String,
    'jupyter_token': fields.String,
    'jupyter_url': fields.String,
    'description': fields.String,
    'creator_id': fields.Integer,
    'image_id': fields.Integer
}


def get_open_port():
    import socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("", 0))
    s.listen(1)
    port = s.getsockname()[1]
    s.close()
    return port


class EnvironmentListResource(Resource):
    def __init__(self):
        super(EnvironmentListResource, self).__init__()

    def abort_if_image_doesnt_exist(self, image_id):
        abort(404, message="image {} doesn't exist".format(image_id))

    @auth.login_required
    @marshal_with(environment_fields)
    def get(self):
        envs = Environment.query.all()

        for e in envs:
            e.set_jupyter_url()

        return envs, 200

    @auth.login_required
    @marshal_with(environment_fields)
    def post(self):
        args = parser.parse_args()

        e = Environment()
        e.name = args['name'].lower()
        e.description = args['description']

        image = Image.query.get(args['image_id'])
        if not image:
            self.abort_if_image_doesnt_exist(args['image_id'])

        e.image_id = image.id
        u = User.query.get(g.user.id)
        e.creator_id = u.id
        e.authorized_users.append(u)

        image_name = docker_registry_domain + "/" + image.name
        open_port = get_open_port()
        e.jupyter_port = open_port
        dockerClient.containers.run(image_name, detach=True, name=e.name, network='docker_environment', ports={"8000/tcp": open_port})
        # wait for container api to be up and running
        subprocess.call(["./wait-for-it.sh", str(e.name + ":5000")])

        e.jupyter_token = str(uuid.uuid4().hex)
        '''
        # TODO: save jupyter token
        resp = requests.post('http://' + e.name + ':5000/jupyter').json()
        e.jupyter_token = resp['jupyter_token']
        '''

        db.session.add(e)
        db.session.commit()

        e.set_jupyter_url()

        return e, 201


class EnvironmentResource(Resource):
    def __init__(self):
        super(EnvironmentResource, self).__init__()

    def abort_if_environment_doesnt_exist(self, env_id):
        abort(404, message="environment {} doesn't exist".format(env_id))

    def get_environment(self, env_id):
        e = Environment.query.get(env_id)

        if not e:
            self.abort_if_environment_doesnt_exist(env_id)

        e.set_jupyter_url()

        return e

    @auth.login_required
    @marshal_with(environment_fields)
    def get(self, env_id):
        return self.get_environment(env_id), 200

    @auth.login_required
    @marshal_with(environment_fields)
    def put(self, env_id):
        e = self.get_environment(env_id)

        args = parser.parse_args()
        e.description = args['description']
        return e, 200

    @auth.login_required
    @marshal_with(environment_fields)
    def delete(self, env_id):
        e = self.get_environment(env_id)

        container = dockerClient.containers.get(e.name)
        container.remove(force=True)

        e.authorized_users = []
        db.session.commit()

        db.session.delete(e)
        db.session.commit()
        return {'result': True}, 204
