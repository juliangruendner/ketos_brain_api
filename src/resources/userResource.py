from flask import g
from flask_restful import Resource, reqparse, abort, fields, marshal_with
from rdb.models.user import User
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
    user = None
    if "@" in username:
        user = User.query.filter_by(email=username).first()
    else:
        user = User.query.filter_by(username=username).first()

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
        return User.query.all()

    @marshal_with(user_fields)
    def post(self):
        args = parser.parse_args()

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

    def abort_if_example_doesnt_exist(self, user_id):
        abort(404, message="user {} doesn't exist".format(user_id))

    @auth.login_required
    @marshal_with(user_fields)
    def get(self, user_id):
        u = User.query.get(user_id)

        if not u:
            self.abort_if_example_doesnt_exist(user_id)

        return u

    @auth.login_required
    @marshal_with(user_fields)
    def delete(self, user_id):
        u = User.query.get(user_id)

        if not u:
            self.abort_if_example_doesnt_exist(user_id)

        db.session.delete(u)
        db.session.commit()
        return {'result': True}, 204

    @auth.login_required
    @marshal_with(user_fields)
    def put(self, user_id):
        u = User.query.get(user_id)

        if not u:
            self.abort_if_example_doesnt_exist(user_id)

        args = parser.parse_args()
        u.first_name = args['first_name']
        u.last_name = args['last_name']
        u.username = args['username']
        u.email = args['email']
        u.hash_password(args['password'])

        db.session.commit()

        return u, 201
