from flask_restful import reqparse, abort, fields, marshal_with
from flask_restful_swagger_2 import swagger, Resource
from rdb.rdb import db
from rdb.models.environment import Environment
from rdb.models.id import ID, id_fields
from dockerUtil.dockerClient import dockerClient
from resources.userResource import auth, user_fields, check_request_for_logged_in_user
from util import environmentUtil

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
            environmentUtil.handle_jupyter_data(e)

        return envs, 200

    @auth.login_required
    @marshal_with(environment_fields)
    def post(self):
        args = self.parser.parse_args()

        e = environmentUtil.create_environment(name=args['name'], desc=args['description'], image_id=args['image_id'])

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

        environmentUtil.handle_jupyter_data(e)

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
                environmentUtil.start_jupyter(e)
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
            environmentUtil.handle_jupyter_data(e)

        return envs, 200
