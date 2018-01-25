from flask_restful import reqparse, fields, marshal_with
from flask_restful_swagger_2 import swagger, Resource
import rdb.models.environment as Environment
from rdb.models.id import ID, id_fields
from resources.userResource import auth, user_fields

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

    @auth.login_required
    @marshal_with(environment_fields)
    def get(self):
        return Environment.get_all(), 200

    @auth.login_required
    @marshal_with(environment_fields)
    def post(self):
        args = self.parser.parse_args()

        e = Environment.create(name=args['name'], desc=args['description'], image_id=args['image_id'])

        return e, 201


class EnvironmentResource(Resource):
    def __init__(self):
        super(EnvironmentResource, self).__init__()
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('name', type=str, required=False, help='No environment name provided', location='json')
        self.parser.add_argument('status', type=str, required=False, location='json')
        self.parser.add_argument('description', type=str, required=False, location='json')
        self.parser.add_argument('image_id', type=int, required=False, help='No image id provided', location='json')

    @auth.login_required
    @marshal_with(environment_fields)
    def get(self, env_id):
        return Environment.get(env_id), 200

    @auth.login_required
    @marshal_with(environment_fields)
    def put(self, env_id):
        args = self.parser.parse_args()

        e = Environment.update(env_id=env_id, status=args['status'], name=args['name'], desc=args['description'])

        return e, 200

    @auth.login_required
    @marshal_with(id_fields)
    def delete(self, env_id):
        id = ID()
        id.id = Environment.delete(env_id)

        return id, 200


class UserEnvironmentListResource(Resource):
    def __init__(self):
        super(UserEnvironmentListResource, self).__init__()

    @auth.login_required
    @marshal_with(environment_fields)
    def get(self, user_id):
        return Environment.get_all_for_user(user_id), 200
