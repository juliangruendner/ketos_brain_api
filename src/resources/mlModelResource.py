from flask import g
from flask_restful import Resource, reqparse, abort, fields, marshal_with
from rdb.rdb import db
from rdb.models.user import User
from rdb.models.mlModel import MLModel
from rdb.models.id import ID, id_fields
from rdb.models.environment import Environment
from resources.userResource import auth, user_fields, check_request_for_logged_in_user
import requests


parser = reqparse.RequestParser()
parser.add_argument('environment_id', type=int, required=True, help='No environment id provided', location='json')
parser.add_argument('name', type=str, required=True, help='No model name provided', location='json')
parser.add_argument('description', type=str, required=False, location='json')

ml_model_fields = {
    'id': fields.Integer,
    'environment_id': fields.Integer,
    'ml_model_name': fields.String,
    'name': fields.String,
    'description': fields.String,
    'creator': fields.Nested(user_fields),
    'created_at': fields.DateTime,
    'updated_at': fields.DateTime
}


class MLModelListResource(Resource):
    def __init__(self):
        super(MLModelListResource, self).__init__()

    def abort_if_environment_doesnt_exist(self, env_id):
        abort(404, message="environment {} doesn't exist".format(env_id))

    @auth.login_required
    @marshal_with(ml_model_fields)
    def get(self):
        return MLModel.query.all(), 200

    @auth.login_required
    @marshal_with(ml_model_fields)
    def post(self):
        args = parser.parse_args()
        e = Environment.query.get(args['environment_id'])

        if not e:
            self.abort_if_environment_doesnt_exist(args['environment_id'])

        m = MLModel()
        m.environment_id = e.id
        m.name = args['name']
        m.description = args['description']
        m.creator_id = User.query.get(g.user.id).id

        resp = requests.post('http://' + e.container_name + ':5000/models').json()
        m.ml_model_name = str(resp['modelName'])

        db.session.add(m)
        db.session.commit()

        return m, 201


class MLModelResource(Resource):
    def __init__(self):
        super(MLModelResource, self).__init__()

    def abort_if_environment_doesnt_exist(self, env_id):
        abort(404, message="environment {} doesn't exist".format(env_id))

    def abort_if_ml_model_doesnt_exist(self, model_id):
        abort(404, message="model {} for environment {} doesn't exist".format(model_id))

    def get_ml_model(self, model_id):
        m = MLModel.query.get(model_id)

        if not m:
            self.abort_if_ml_model_doesnt_exist(model_id)

        return m

    @auth.login_required
    @marshal_with(ml_model_fields)
    def get(self, model_id):
        return self.get_ml_model(model_id), 200

    @auth.login_required
    @marshal_with(ml_model_fields)
    def put(self, model_id):
        m = self.get_ml_model(model_id)
        check_request_for_logged_in_user(m.creator_id)

        args = parser.parse_args()
        if args['name']:
            m.name = args['name']

        if args['description']:
            m.description = args['description']

        db.session.commit()
        return m, 200

    @auth.login_required
    @marshal_with(id_fields)
    def delete(self, model_id):
        m = self.get_ml_model(model_id)
        check_request_for_logged_in_user(m.creator_id)

        db.session.delete(m)
        db.session.commit()

        id = ID()
        id.id = model_id
        return id, 200


class UserMLModelListResource(Resource):
    def __init__(self):
        super(UserMLModelListResource, self).__init__()

    @auth.login_required
    @marshal_with(ml_model_fields)
    def get(self, user_id):
        return MLModel.query.filter_by(creator_id=user_id).all(), 200
