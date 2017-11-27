from flask import g
from flask_restful import Resource, reqparse, abort, fields, marshal_with
from rdb.rdb import db
from rdb.models.user import User
from rdb.models.mlModel import MLModel
from rdb.models.environment import Environment
from resources.userResource import auth
import requests

parser = reqparse.RequestParser()
parser.add_argument('environment_id', type=int, required=True, help='No environment id provided', location='json')
parser.add_argument('name', type=str, required=True, help='No model name provided', location='json')
parser.add_argument('description', type=str, required=False, location='json')

ml_model_fields = {
    'environment_id': fields.Integer,
    'name': fields.String,
    'description': fields.String,
    'creator_id': fields.Integer
}


class MLModelListResource(Resource):
    def __init__(self):
        super(MLModelListResource, self).__init__()

    def abort_if_environment_doesnt_exist(self, env_id):
        abort(404, message="environment {} doesn't exist".format(env_id))

    @auth.login_required
    @marshal_with(ml_model_fields)
    def get(self, env_id):
        # r = requests.get('http://nico_prod:5000/tests')
        # return r.json()
        return MLModel.query.all(), 200

    @auth.login_required
    @marshal_with(ml_model_fields)
    def post(self, env_id):
        e = Environment.query.get(env_id)

        if not e:
            self.abort_if_environment_doesnt_exist(env_id)

        args = parser.parse_args()
        m = MLModel()
        m.environment_id = e.id
        m.name = args['name']
        m.description = args['description']
        m.creator_id = User.query.get(g.user.id).id

        db.session.add(m)
        db.session.commit()

        return m, 201


class MLModelResource(Resource):
    def __init__(self):
        super(MLModelResource, self).__init__()

    def abort_if_environment_doesnt_exist(self, env_id):
        abort(404, message="environment {} doesn't exist".format(env_id))

    def abort_if_ml_model_doesnt_exist(self, env_id, model_id):
        abort(404, message="model {} for environment {} doesn't exist".format(model_id, env_id))

    def get_ml_model(self, env_id, model_id):
        m = MLModel.query.get(env_id, model_id)

        if not m:
            self.abort_if_ml_model_doesnt_exist(env_id, model_id)

        return m

    @auth.login_required
    @marshal_with(ml_model_fields)
    def get(self, env_id, model_id):
        return self.get_ml_model(env_id, model_id), 200

    @auth.login_required
    @marshal_with(ml_model_fields)
    def put(self, env_id, model_id):
        m = self.get_ml_model(env_id, model_id)

        args = parser.parse_args()
        m.description = args['description']

        db.session.commit()
        return m, 200

    @auth.login_required
    @marshal_with(ml_model_fields)
    def delete(self, env_id, model_id):
        m = self.get_ml_model(env_id, model_id)

        db.session.delete(m)
        db.session.commit()
        return {'result': True}, 204
