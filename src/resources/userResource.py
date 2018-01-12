from flask import g
from flask_restful import reqparse, abort, fields, marshal_with
from flask_restful_swagger_2 import swagger, Resource
from rdb.models.user import User, get_user_by_username
from rdb.models.id import ID, id_fields
from rdb.rdb import db
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
    user = get_user_by_username(username)

    if not user or not user.verify_password(password):
        return False
    g.user = user
    return True


def check_request_for_logged_in_user(user_id):
    if not (is_admin_user() or user_id == g.user.id):
        abort(403, message="only an admin or the logged in user matching the requested user id is allowed to use this")


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
        return User.query.all(), 200

    @auth.login_required
    @marshal_with(user_fields)
    def post(self):
        args = self.parser.parse_args()

        u = User()
        u.username = args['username']
        u.email = args['email']
        u.hash_password(args['password'])
        u.first_name = args['first_name']
        u.last_name = args['last_name']

        db.session.add(u)
        db.session.commit()

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

    def abort_if_user_doesnt_exist(self, user_id):
        abort(404, message="user {} doesn't exist".format(user_id))

    def get_user(self, user_id):
        u = User.query.get(user_id)

        if not u:
            self.abort_if_user_doesnt_exist(user_id)

        return u

    @auth.login_required
    @marshal_with(user_fields)
    def get(self, user_id):
        return self.get_user(user_id), 200

    @auth.login_required
    @marshal_with(id_fields)
    def delete(self, user_id):
        check_request_for_logged_in_user(user_id)

        u = self.get_user(user_id)

        db.session.delete(u)
        db.session.commit()

        id = ID()
        id.id = user_id
        return id, 200

    @auth.login_required
    @marshal_with(user_fields)
    def put(self, user_id):
        check_request_for_logged_in_user(user_id)

        u = self.get_user(user_id)

        args = self.parser.parse_args()
        if args['username']:
            u.username = args['username']

        if args['email']:
            u.email = args['email']

        if args['password']:
            u.hash_password(args['password'])

        if args['first_name']:
            u.first_name = args['first_name']

        if args['last_name']:
            u.last_name = args['last_name']

        db.session.commit()
        return u, 200
