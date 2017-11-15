from flask import g
from flask_restful import Resource, reqparse, abort, fields, marshal_with
from rdb.models.user import User
from rdb.rdb import db
from flask_httpauth import HTTPBasicAuth

auth = HTTPBasicAuth()

envSpecParser = reqparse.RequestParser()
envSpecParser.add_argument('codetype',
                    type=str,
                    required=True,
                    help='No codetype provided',
                    location='json')
envSpecParser.add_argument('version',
                    type=str,
                    required=True,
                    help='No version provided',
                    location='json')
envSpecParser.add_argument('libraryPackage',
                    type=str,
                    required=False,
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


class EnvironmentListResource(Resource):
    def __init__(self):
        super(EnvironmentListResource, self).__init__()

    def get(self):
        return {'turns out u can just write json here': 4098, 'thisIsBloodyAwesome': 'muhahah'}

    def post(self):
        args = envSpecParser.parse_args()

        '''
        environment = User(first_name=args['first_name'], last_name=args['last_name'],
                 email=args['email'], password=args['password'])

        db.session.add(environment)
        db.session.commit()
        '''

        return args, 401


class EnvironmentResource(Resource):
    def __init__(self):
        super(EnvironmentResource, self).__init__()

    def abort_if_example_doesnt_exist(self, env_id):
        abort(404, message="user {} doesn't exist".format(env_id))

    @auth.login_required
    def get(self, env_id):
        '''
        u = User.query.get(user_id)

        if not u:
            self.abort_if_example_doesnt_exist(user_id)

        '''

        return {'id':'1', 'user' : g.user.email}

