from flask import send_from_directory, request
from flask_restful import reqparse, abort, fields, marshal_with, marshal
from flask_restful_swagger_2 import swagger, Resource
from rdb.rdb import db
from rdb.models.mlModel import MLModel
from rdb.models.featureSet import FeatureSet
from rdb.models.id import ID, id_fields
from resources.userResource import auth, user_fields, check_request_for_logged_in_user
from resources.environmentResource import environment_fields
from resources.featureSetResource import feature_set_fields
import requests
from util import mlModelUtil, modelPackagingUtil

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


def get_ml_model(model_id):
    m = MLModel.query.get(model_id)

    if not m:
        abort_if_ml_model_doesnt_exist(model_id)

    return m


def get_feature_set(feature_set_id):
    fs = FeatureSet.query.get(feature_set_id)

    if not fs:
        mlModelUtil.abort_if_feature_set_doesnt_exist(feature_set_id)

    return fs


class MLModelListResource(Resource):
    def __init__(self):
        super(MLModelListResource, self).__init__()
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('environment_id', type=int, required=True, help='No environment id provided', location='json')
        self.parser.add_argument('name', type=str, required=False, help='No model name provided', location='json')
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

        m = mlModelUtil.create_ml_model(name=args['name'], desc=args['description'], env_id=args['environment_id'], feature_set_id=args['feature_set_id'])

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


class MLModelPackageResource(Resource):
    def __init__(self):
        super(MLModelPackageResource, self).__init__()

    @auth.login_required
    def post(self, model_id):
        m = get_ml_model(model_id)

        modelPackagingUtil.package_model(m)

        return {'done': True}, 201

    @auth.login_required
    def get(self, model_id):
        m = get_ml_model(model_id)
        response = send_from_directory(modelPackagingUtil.get_packaging_path(m), m.ml_model_name + '.zip', as_attachment=True)
        response.headers['content-type'] = 'application/octet-stream'
        return response


def allowed_file(filename):
    ALLOWED_EXTENSIONS = set(['zip'])
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


class MLModelLoadResource(Resource):
    def __init__(self):
        super(MLModelLoadResource, self).__init__()

    @auth.login_required
    def post(self):
        if 'file' not in request.files:
            abort(400, message="File part is empty")
        f = request.files['file']
        if f.filename == '':
            abort(400, message="No file selected")
        if not allowed_file(f.filename):
            abort(400, message="File not allowed")

        modelPackagingUtil.load_model(f)

        return {'done': True}, 201


class MLModelPredicitionResource(Resource):
    def __init__(self):
        super(MLModelPredicitionResource, self).__init__()
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('dataUrl', type=str, required=True, help='no data url provided', location='args')

    @auth.login_required
    def post(self, model_id):
        
        parser = reqparse.RequestParser()
        parser.add_argument('patient_ids', type= int, required= True , help='no patientIds provided', location='json')
        args = parser.parse_args()
        patient_ids = args['patient_ids']

        ml_model = get_ml_model(model_id)
        features = ml_model.feature_set.features
        feature_set = []

        for feature in features:
            cur_feature = marshal(feature, feature_fields)
            feature_set.append(cur_feature)

        preprocess_body = {'patient': patient_ids, 'feature_set': feature_set}
        
        resp = requests.post('http://data_pre:5000/crawler', json = preprocess_body).json()
        csv_url = resp['csv_url']
        csv_url = csv_url.replace("localhost", "data_pre")
        data_url = {'dataUrl': csv_url}
        docker_api_call = 'http://' + ml_model.environment.container_name + ':5000/models/' + ml_model.ml_model_name + '/execute'
        print(docker_api_call)
        resp = requests.get(docker_api_call, params = data_url).json()

        return resp, 200
