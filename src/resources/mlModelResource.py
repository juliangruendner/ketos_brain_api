from flask import g
from flask_restful import Resource, reqparse, abort, fields, marshal_with, marshal
from rdb.rdb import db
from rdb.models.user import User
from rdb.models.mlModel import MLModel
from rdb.models.featureSet import FeatureSet
from rdb.models.id import ID, id_fields
from rdb.models.environment import Environment
from resources.userResource import auth, user_fields, check_request_for_logged_in_user
from resources.environmentResource import environment_fields
from resources.featureSetResource import feature_set_fields
import requests

ml_model_fields = {
    'id': fields.Integer,
    'environment_id': fields.Integer,
    'ml_model_name': fields.String,
    'name': fields.String,
    'description': fields.String,
    'creator': fields.Nested(user_fields),
    'created_at': fields.DateTime,
    'updated_at': fields.DateTime,
    'feature_set_id': fields.Integer,
    'environment': fields.Nested(environment_fields),
    'feature_set': fields.Nested(feature_set_fields)
}

feature_fields = {
    'resource': fields.String,
    'key': fields.String(attribute='parameter_name'),
    'value': fields.String,
}


def abort_if_ml_model_doesnt_exist(model_id):
    abort(404, message="model {} for environment {} doesn't exist".format(model_id))


def abort_if_feature_set_doesnt_exist(feature_set_id):
    abort(404, message="feature set {} doesn't exist".format(feature_set_id))


def get_ml_model(model_id):
    m = MLModel.query.get(model_id)

    if not m:
        abort_if_ml_model_doesnt_exist(model_id)

    return m


def get_feature_set(feature_set_id):
    fs = FeatureSet.query.get(feature_set_id)

    if not fs:
        abort_if_feature_set_doesnt_exist(feature_set_id)

    return fs


class MLModelListResource(Resource):
    def __init__(self):
        super(MLModelListResource, self).__init__()
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('environment_id', type=int, required=True, help='No environment id provided', location='json')
        self.parser.add_argument('name', type=str, required=True, help='No model name provided', location='json')
        self.parser.add_argument('description', type=str, required=False, location='json')
        self.parser.add_argument('feature_set_id', type=int, required=False, location='json')

    def abort_if_environment_doesnt_exist(self, env_id):
        abort(404, message="environment {} doesn't exist".format(env_id))

    @auth.login_required
    @marshal_with(ml_model_fields)
    def get(self):
        return MLModel.query.all(), 200

    @auth.login_required
    @marshal_with(ml_model_fields)
    def post(self):
        args = self.parser.parse_args()
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

        if args['feature_set_id']:
            fs = get_feature_set(args['feature_set_id'])
            m.feature_set_id = fs.id

        db.session.add(m)
        db.session.commit()

        return m, 201


class MLModelResource(Resource):
    def __init__(self):
        super(MLModelResource, self).__init__()
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('name', type=str, required=False, location='json')
        self.parser.add_argument('description', type=str, location='json')
        self.parser.add_argument('feature_set_id', type=int, required=False, location='json')

    def abort_if_environment_doesnt_exist(self, env_id):
        abort(404, message="environment {} doesn't exist".format(env_id))

    @auth.login_required
    @marshal_with(ml_model_fields)
    def get(self, model_id):
        return get_ml_model(model_id), 200

    @auth.login_required
    @marshal_with(ml_model_fields)
    def put(self, model_id):
        m = get_ml_model(model_id)
        check_request_for_logged_in_user(m.creator_id)

        args = self.parser.parse_args()
        if args['name']:
            m.name = args['name']

        if args['description']:
            m.description = args['description']

        if args['feature_set_id']:
            fs = get_feature_set(args['feature_set_id'])
            m.feature_set_id = fs.id

        db.session.commit()
        return m, 200

    @auth.login_required
    @marshal_with(id_fields)
    def delete(self, model_id):
        m = get_ml_model(model_id)
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


class MLModelPredicitionResource(Resource):
    def __init__(self):
        super(MLModelPredicitionResource, self).__init__()
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('dataUrl', type=str, required=True, help='no data url provided', location='args')

    @auth.login_required
    def post(self, model_id):
        
        parser = reqparse.RequestParser()
        parser.add_argument('patient_ids', type= int ,action='append', required= True , help='no patientIds provided', location='json')
        args = parser.parse_args()
        patient_ids = args['patient_ids']

        ml_model = get_ml_model(model_id)
        features = ml_model.feature_set.features
        feature_set = []

        for feature in features:
            cur_feature = marshal(feature, feature_fields)
            feature_set.append(cur_feature)

        preprocess_body = {'patient_ids': patient_ids, 'feature_set': feature_set}
        print(preprocess_body)
        resp = requests.post('http://data_pre:5000/crawler ', json = preprocess_body).json()

        data_url = {'dataUrl': resp.csv_url}
        resp = requests.get('http://' + ml_model.environment.container_name + ':5000/models/' + '1' + '/execute', params = data_url).json()

        return resp, 200
