from flask import g
from flask_restful import Resource, reqparse, abort, fields, marshal_with
from rdb.models.user import User
from rdb.rdb import db
from flask_httpauth import HTTPBasicAuth

auth = HTTPBasicAuth()

parser = reqparse.RequestParser()
parser.add_argument('first_name',
                    type=str,
                    required=True,
                    help='No first name provided',
                    location='json')
parser.add_argument('last_name',
                    type=str,
                    required=True,
                    help='No last name provided',
                    location='json')
parser.add_argument('email',
                    type=str,
                    required=True,
                    help='No email provided',
                    location='json')
parser.add_argument('password',
                    type=str,
                    required=True,
                    help='No password provided',
                    location='json')

user_fields = {
    'id': fields.Integer,
    'first_name': fields.String,
    'last_name': fields.String,
    'email': fields.String,
    'password': fields.String
}


@auth.verify_password
def verify_password(username, password):
    # try to authenticate with username/password
    user = User.query.filter_by(email=username).first()
    if not user or not user.verify_password(password):
        return False
    g.user = user
    return True


class UserListResource(Resource):
    def __init__(self):
        super(UserListResource, self).__init__()

    @marshal_with(user_fields)
    def get(self):
        return User.query.all()

    @marshal_with(user_fields)
    def post(self):
        args = parser.parse_args()

        u = User(first_name=args['first_name'], last_name=args['last_name'],
                 email=args['email'], password=args['password'])

        db.session.add(u)
        db.session.commit()

        return u, 201


class UserResource(Resource):
    def __init__(self):
        super(UserResource, self).__init__()

    def abort_if_example_doesnt_exist(self, user_id):
        abort(404, message="user {} doesn't exist".format(user_id))

    @marshal_with(user_fields)
    def get(self, user_id):
        u = User.query.get(user_id)

        if not u:
            self.abort_if_example_doesnt_exist(user_id)

        return u

    @marshal_with(user_fields)
    def delete(self, user_id):
        u = User.query.get(user_id)

        if not u:
            self.abort_if_example_doesnt_exist(user_id)

        db.session.delete(u)
        db.session.commit()
        return {'result': True}, 204

    @marshal_with(user_fields)
    def put(self, user_id):
        u = User.query.get(user_id)

        if not u:
            self.abort_if_example_doesnt_exist(user_id)

        args = parser.parse_args()
        u.first_name = args['first_name']
        u.last_name = args['last_name']
        u.email = args['email']
        u.password = args['password']

        db.session.commit()

        return u, 201
