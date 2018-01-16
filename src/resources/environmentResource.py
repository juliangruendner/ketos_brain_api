from flask import g
from flask_restful import reqparse, abort, fields, marshal_with
from flask_restful_swagger_2 import swagger, Resource
from rdb.rdb import db
from rdb.models.environment import Environment
from rdb.models.user import User
from rdb.models.image import Image
from rdb.models.id import ID, id_fields
from dockerUtil.dockerClient import dockerClient, wait_for_it
from resources.userResource import auth, user_fields, check_request_for_logged_in_user
from resources.adminAccess import is_admin_user
import config
import requests
import uuid

environment_fields = {
    'id': fields.Integer,
    'name': fields.String,
    'container_id': fields.String,
    'container_name': fields.String,
    'status': fields.String,
    'jupyter_port': fields.String,
    'jupyter_token': fields.String,
    'jupyter_url': fields.String,
    'description': fields.String,
    'creator': fields.Nested(user_fields),
    'image_id': fields.Integer,
    'created_at': fields.DateTime,
    'updated_at': fields.DateTime
}


def get_open_port():
    import socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("", 0))
    s.listen(1)
    port = s.getsockname()[1]
    s.close()
    return port


def handle_jupyter_data(e):
        if is_admin_user() or g.user.id == e.creator_id:
            e.set_jupyter_url()
        else:
            e.hide_jupyter_data()


def start_jupyter(e):
    # wait for container api to be up and running
    wait_for_it(e.container_name, 5000)
    # start jupyter notebook and get jupyter token
    resp = requests.post('http://' + e.container_name + ':5000/jupyter').json()
    e.jupyter_token = str(resp['jupyter_token'])
    e.status = Environment.Status.running.value


class EnvironmentListResource(Resource):
    def __init__(self):
        super(EnvironmentListResource, self).__init__()
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('name', type=str, required=True, help='No environment name provided', location='json')
        self.parser.add_argument('status', type=str, required=False, location='json')
        self.parser.add_argument('description', type=str, required=False, location='json')
        self.parser.add_argument('image_id', type=int, required=True, help='No image id provided', location='json')

    def abort_if_image_doesnt_exist(self, image_id):
        abort(404, message="image {} doesn't exist".format(image_id))

    @auth.login_required
    @marshal_with(environment_fields)
    def get(self):
        envs = Environment.query.all()

        for e in envs:
            handle_jupyter_data(e)

        return envs, 200

    @auth.login_required
    @marshal_with(environment_fields)
    def post(self):
        args = self.parser.parse_args()

        e = Environment()
        e.name = args['name']
        e.description = args['description']

        image = Image.query.get(args['image_id'])
        if not image:
            self.abort_if_image_doesnt_exist(args['image_id'])

        e.image_id = image.id
        e.creator_id = g.user.id

        image_name = config.DOCKER_REGISTRY_DOMAIN + "/" + image.name
        e.jupyter_port = get_open_port()

        e.container_name = str(uuid.uuid4().hex)

        container = dockerClient.containers.run(image_name,
                                                name=e.container_name,
                                                detach=True,
                                                network=config.PROJECT_NAME+"_environment",
                                                ports={"8000/tcp": e.jupyter_port},
                                                volumes={'/tmp/ketos/environments_data/'+e.container_name: {'bind': '/mlenvironment/models', 'mode': 'rw'}})

        e.container_id = container.id
        start_jupyter(e)

        db.session.add(e)
        db.session.commit()

        e.set_jupyter_url()

        return e, 201


class EnvironmentResource(Resource):
    def __init__(self):
        super(EnvironmentResource, self).__init__()
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('name', type=str, required=False, help='No environment name provided', location='json')
        self.parser.add_argument('status', type=str, required=False, location='json')
        self.parser.add_argument('description', type=str, required=False, location='json')
        self.parser.add_argument('image_id', type=int, required=False, help='No image id provided', location='json')

    def abort_if_environment_doesnt_exist(self, env_id):
        abort(404, message="environment {} doesn't exist".format(env_id))

    def get_environment(self, env_id):
        e = Environment.query.get(env_id)

        if not e:
            self.abort_if_environment_doesnt_exist(env_id)

        handle_jupyter_data(e)

        return e

    @auth.login_required
    @marshal_with(environment_fields)
    def get(self, env_id):
        return self.get_environment(env_id), 200

    @auth.login_required
    @marshal_with(environment_fields)
    def put(self, env_id):
        e = self.get_environment(env_id)

        check_request_for_logged_in_user(e.creator_id)

        args = self.parser.parse_args()
        status_new = args['status']
        if status_new and not e.status == status_new:
            if status_new == Environment.Status.running.value:
                dockerClient.containers.get(e.container_id).start()
                start_jupyter(e)
            elif status_new == Environment.Status.stopped.value:
                dockerClient.containers.get(e.container_id).stop()
            else:
                abort(400, message="status {} is not allowed".format(status_new))

            e.status = status_new

        if args['name']:
            e.name = args['name']

        if args['description']:
            e.description = args['description']

        db.session.commit()
        return e, 200

    @auth.login_required
    @marshal_with(id_fields)
    def delete(self, env_id):
        e = self.get_environment(env_id)

        check_request_for_logged_in_user(e.creator_id)

        if not e.status == 'stopped':
            abort(405, message="environment must be stopped before it can be deleted")

        container = dockerClient.containers.get(e.container_id)
        container.remove(force=True)

        db.session.delete(e)
        db.session.commit()

        id = ID()
        id.id = env_id
        return id, 200


class UserEnvironmentListResource(Resource):
    def __init__(self):
        super(UserEnvironmentListResource, self).__init__()

    @auth.login_required
    @marshal_with(environment_fields)
    def get(self, user_id):
        envs = Environment.query.filter_by(creator_id=user_id).all()

        for e in envs:
            handle_jupyter_data(e)

        return envs, 200
