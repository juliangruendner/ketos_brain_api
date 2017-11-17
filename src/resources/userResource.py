from flask import g
from flask_restful import Resource, reqparse, abort, fields, marshal_with
from rdb.models.user import User, get_user_by_username
from rdb.rdb import db
from flask_httpauth import HTTPBasicAuth

auth = HTTPBasicAuth()

parser = reqparse.RequestParser()
parser.add_argument('first_name', type=str, location='json')
parser.add_argument('last_name', type=str, location='json')
parser.add_argument('username', type=str, required=True, help='No username provided', location='json')
parser.add_argument('email', type=str, required=True, help='No email provided', location='json')
parser.add_argument('password', type=str, required=True, help='No password provided', location='json')

user_fields = {
    'id': fields.Integer,
    'first_name': fields.String,
    'last_name': fields.String,
    'username': fields.String,
    'email': fields.String
}


@auth.verify_password
def verify_password(username, password):
    # is username the real username or the email
    # username: not @ contained
    # email: @ contained
    user = get_user_by_username(username)

    if not user or not user.verify_password(password):
        return False
    g.user = user
    return True


class UserListResource(Resource):
    def __init__(self):
        super(UserListResource, self).__init__()

    @auth.login_required
    @marshal_with(user_fields)
    def get(self):
        return User.query.all(), 200

    @marshal_with(user_fields)
    def post(self):
        args = parser.parse_args()

        u = User()
        u.username = args['username'].lower()
        u.email = args['email'].lower()
        u.hash_password(args['password'])
        u.first_name = args['first_name']
        u.last_name = args['last_name']

        db.session.add(u)
        db.session.commit()

        return u, 201


class UserResource(Resource):
    def __init__(self):
        super(UserResource, self).__init__()

    def abort_if_user_doesnt_exist(self, user_id):
        abort(404, message="user {} doesn't exist".format(user_id))

    def get_user(self, username):
        u = get_user_by_username(username)

        if not u:
            self.abort_if_user_doesnt_exist(username)

        return u

    @auth.login_required
    @marshal_with(user_fields)
    def get(self, username):
        return self.get_user(username), 200

    @auth.login_required
    @marshal_with(user_fields)
    def delete(self, username):
        u = self.get_user(username)

        db.session.delete(u)
        db.session.commit()
        return {'result': True}, 204

    @auth.login_required
    @marshal_with(user_fields)
    def put(self, username):
        u = self.get_user(username)

        args = parser.parse_args()
        u.username = args['username'].lower()
        u.email = args['email'].lower()
        u.hash_password(args['password'])
        u.first_name = args['first_name']
        u.last_name = args['last_name']

        db.session.commit()
        return u, 200
