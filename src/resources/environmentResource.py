from flask import g
from flask_restful import Resource, reqparse, abort, fields, marshal_with
from rdb.rdb import db
from rdb.models.environment import Environment
from rdb.models.user import User
from rdb.models.image import Image
from resources.userResource import auth

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
            e.fill_jupyter_url()

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
        e.creator_id = User.query.get(g.user.id).id

        db.session.add(e)
        db.session.commit()

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

        e.fill_jupyter_url()

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

        db.session.delete(e)
        db.session.commit()
        return {'result': True}, 204
