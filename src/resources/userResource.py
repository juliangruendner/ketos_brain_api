from flask import g
from flask_restful import reqparse, abort, fields, marshal_with
from flask_restful_swagger_2 import swagger, Resource
import rdb.models.user as User
from rdb.models.id import ID, id_fields
from flask_httpauth import HTTPBasicAuth
from resources.adminAccess import AdminAccess, is_admin_user

auth = HTTPBasicAuth()

user_fields = {
    'id': fields.Integer,
    'first_name': fields.String,
    'last_name': fields.String,
    'username': fields.String,
    'email': fields.String,
    'created_at': fields.DateTime,
    'updated_at': fields.DateTime
}


@auth.verify_password
def verify_password(username, password):
    u = User.get_by_username(username, raise_abort=False)

    if not u or not u.verify_password(password):
        return False
    g.user = u
    return True


class UserLoginResource(Resource):
    def __init__(self):
        super(UserLoginResource, self).__init__()

    @auth.login_required
    @marshal_with(user_fields)
    def get(self):
        return g.user, 200


class UserListResource(Resource):
    def __init__(self):
        super(UserListResource, self).__init__()
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('first_name', type=str, location='json')
        self.parser.add_argument('last_name', type=str, location='json')
        self.parser.add_argument('username', type=str, required=True, help='No username provided', location='json')
        self.parser.add_argument('email', type=str, required=True, help='No email provided', location='json')
        self.parser.add_argument('password', type=str, required=True, help='No password provided', location='json')

    @auth.login_required
    @marshal_with(user_fields)
    @AdminAccess()
    def get(self):
        return User.get_all(), 200

    @auth.login_required
    @marshal_with(user_fields)
    def post(self):
        args = self.parser.parse_args()

        u = User.create(username=args['username'], email=args['email'], password=args['password'], first_name=args['first_name'], last_name=args['last_name'])

        return u, 201


class UserResource(Resource):
    def __init__(self):
        super(UserResource, self).__init__()
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('first_name', type=str, location='json')
        self.parser.add_argument('last_name', type=str, location='json')
        self.parser.add_argument('username', type=str, location='json')
        self.parser.add_argument('email', type=str, location='json')
        self.parser.add_argument('password', type=str, location='json')

    @auth.login_required
    @marshal_with(user_fields)
    def get(self, user_id):
        return User.get(user_id), 200

    @auth.login_required
    @marshal_with(id_fields)
    def delete(self, user_id):
        id = ID()
        id.id = User.delete(user_id)

        return id, 200

    @auth.login_required
    @marshal_with(user_fields)
    def put(self, user_id):
        args = self.parser.parse_args()

        u = User.update(user_id=user_id, username=args['username'], email=args['email'], password=args['password'], first_name=args['first_name'], last_name=args['last_name'])

        return u, 200
