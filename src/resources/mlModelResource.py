from flask import send_from_directory
from flask_restful import reqparse, abort, fields, marshal_with, marshal
from flask_restful_swagger_2 import swagger, Resource
import rdb.models.mlModel as MLModel
from rdb.models.id import ID, id_fields
from resources.userResource import auth, user_fields
from resources.environmentResource import environment_fields
from resources.featureSetResource import feature_set_fields
import requests
import config
from util import modelPackagingUtil
from flask_restplus import inputs
import werkzeug

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


class MLModelListResource(Resource):
    def __init__(self):
        super(MLModelListResource, self).__init__()
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('environment_id', type=int, required=True, help='No environment id provided', location='json')
        self.parser.add_argument('name', type=str, required=False, help='No model name provided', location='json')
        self.parser.add_argument('description', type=str, required=False, location='json')
        self.parser.add_argument('feature_set_id', type=int, required=False, location='json')
        self.parser.add_argument('create_example_model', type=inputs.boolean, default=True, required=False, location='args')

    def abort_if_environment_doesnt_exist(self, env_id):
        abort(404, message="environment {} doesn't exist".format(env_id))

    @auth.login_required
    @marshal_with(ml_model_fields)
    def get(self):
        return MLModel.get_all(), 200

    @auth.login_required
    @marshal_with(ml_model_fields)
    def post(self):
        args = self.parser.parse_args()

        m = MLModel.create(name=args['name'], desc=args['description'], env_id=args['environment_id'], create_example_model=args['create_example_model'], feature_set_id=args['feature_set_id'])

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
        return MLModel.get(model_id), 200

    @auth.login_required
    @marshal_with(ml_model_fields)
    def put(self, model_id):
        args = self.parser.parse_args()

        m = MLModel.update(model_id=model_id, name=args['name'], desc=args['description'], feature_set_id=args['feature_set_id'])

        return m, 200

    @auth.login_required
    @marshal_with(id_fields)
    def delete(self, model_id):
        id = ID()
        id.id = MLModel.delete(model_id)

        return id, 200


class UserMLModelListResource(Resource):
    def __init__(self):
        super(UserMLModelListResource, self).__init__()

    @auth.login_required
    @marshal_with(ml_model_fields)
    def get(self, user_id):
        return MLModel.get_all_for_user(user_id), 200


class MLModelExportResource(Resource):
    def __init__(self):
        super(MLModelExportResource, self).__init__()

    @auth.login_required
    def post(self, model_id):
        m = MLModel.get(model_id)

        modelPackagingUtil.package_model(m)

        return {'done': True}, 201

    @auth.login_required
    def get(self, model_id):
        m = MLModel.get(model_id)
        response = send_from_directory(modelPackagingUtil.get_packaging_path(m), m.ml_model_name + '.zip', as_attachment=True)
        response.headers['content-type'] = 'application/octet-stream'
        return response


class MLModelImportResource(Resource):
    def __init__(self):
        super(MLModelImportResource, self).__init__()
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('file', type=werkzeug.datastructures.FileStorage, required=True, location='files')
        self.parser.add_argument('environment_id', type=int, required=False, location='args')
        self.parser.add_argument('feature_set_id', type=int, required=False, location='args')

    def allowed_file(self, filename):
        ALLOWED_EXTENSIONS = set(['zip'])
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

    @auth.login_required
    def post(self):
        args = self.parser.parse_args()
        f = args['file']

        if f.filename == '':
            abort(400, message="No file selected")
        if not self.allowed_file(f.filename):
            abort(400, message="File not allowed")

        modelPackagingUtil.load_model(file=f, environment_id=args['environment_id'], feature_set_id=args['feature_set_id'])

        return {'done': True}, 201


class MLModelImportSuitableEnvironmentResource(Resource):
    def __init__(self):
        super(MLModelImportSuitableEnvironmentResource, self).__init__()
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('file', type=werkzeug.datastructures.FileStorage, required=True, location='files')

    def allowed_file(self, filename):
        ALLOWED_EXTENSIONS = set(['json'])
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

    @auth.login_required
    @marshal_with(environment_fields)
    def post(self):
        args = self.parser.parse_args()
        f = args['file']

        if f.filename == '':
            abort(400, message="No file selected")
        if not self.allowed_file(f.filename):
            abort(400, message="File not allowed")

        return modelPackagingUtil.get_suitable_environments(f, raise_abort=False), 200


class MLModelImportSuitableFeatureSetResource(Resource):
    def __init__(self):
        super(MLModelImportSuitableFeatureSetResource, self).__init__()
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('file', type=werkzeug.datastructures.FileStorage, required=True, location='files')

    def allowed_file(self, filename):
        ALLOWED_EXTENSIONS = set(['json'])
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

    @auth.login_required
    @marshal_with(feature_set_fields)
    def post(self):
        args = self.parser.parse_args()
        f = args['file']

        if f.filename == '':
            abort(400, message="No file selected")
        if not self.allowed_file(f.filename):
            abort(400, message="File not allowed")

        return modelPackagingUtil.get_suitable_feature_sets(f), 200


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

        ml_model = MLModel.get(model_id)
        features = ml_model.feature_set.features
        feature_set = []

        for feature in features:
            cur_feature = marshal(feature, feature_fields)
            feature_set.append(cur_feature)

        preprocess_body = {'patient': patient_ids, 'feature_set': feature_set}
        
        resp = requests.post('http://' + config.DATA_PREPROCESSING_HOST + '/crawler', json = preprocess_body).json()
        csv_url = resp['csv_url']
        csv_url = csv_url.replace("localhost", "data_pre")
        data_url = {'dataUrl': csv_url}
        docker_api_call = 'http://' + ml_model.environment.container_name + ':5000/models/' + ml_model.ml_model_name + '/execute'
        print(docker_api_call)
        resp = requests.get(docker_api_call, params = data_url).json()

        return resp, 200
