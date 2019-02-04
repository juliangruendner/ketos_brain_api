from flask import send_from_directory
from flask_restful import reqparse, abort, fields, marshal_with, marshal
from flask_restful_swagger_2 import swagger, Resource
import rdb.models.mlModel as MLModel
import rdb.models.predictionOutcome as PredictionOutcome
from rdb.models.id import ID, id_fields
from resources.userResource import auth, user_fields
from resources.environmentResource import environment_fields
from resources.featureSetResource import feature_set_fields
import requests
import config
from util import modelPackagingUtil
from flask_restplus import inputs
import werkzeug
import fhirclient.models.riskassessment as fhir_ra
import rdb.fhir_models.riskAssessment as fhir_ra_base
import sys


ml_model_fields = {
    'id': fields.Integer,
    'environment_id': fields.Integer,
    'ml_model_name': fields.String,
    'condition_refcode': fields.String,
    'condition_name': fields.String,
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
        self.parser.add_argument('condition_refcode', type=str, required=False, location='json')
        self.parser.add_argument('condition_name', type=str, required=False, location='json')
        self.parser.add_argument('create_example_model', type=inputs.boolean, default=True, required=False, location='args')

    @auth.login_required
    @marshal_with(ml_model_fields)
    @swagger.doc({
        "summary": "Returns all existing ML models",
        "tags": ["ml models"],
        "produces": [
            "application/json"
        ],
        "description": 'Returns all existing machine learning models',
        "responses": {
            "200": {
                "description": "Returns the list of ML models"
            }
        }
    })
    def get(self):
        return MLModel.get_all(), 200

    @auth.login_required
    @marshal_with(ml_model_fields)
    @swagger.doc({
        "summary": "Create a new ML model",
        "tags": ["ml models"],
        "produces": [
            "application/json"
        ],
        "description": 'Create a new machine learning model',
        "parameters": [
            {
                "name": "create_example_model",
                "in": "query",
                "type": "boolean",
                "description": "Flag whether to create an example model or not",
                "required": False
            },
            {
                "name": "ml_model",
                "in": "body",
                "schema": {
                    "type": "object",
                    "properties": {
                        "environment_id": {
                            "type": "integer"
                        },
                        "name": {
                            "type": "string"
                        },
                        "description": {
                            "type": "string"
                        },
                        "feature_set_id": {
                            "type": "integer"
                        },
                        "condition_refcode": {
                            "type": "string"
                        },
                        "condition_name": {
                            "type": "string"
                        }
                    }
                }
            }
        ],
        "responses": {
            "200": {
                "description": "Returns newly created ML model"
            },
            "404": {
                "description": "Not found error when environment or feature set doesn't exist"
            }
        }
    })
    def post(self):
        args = self.parser.parse_args()

        m = MLModel.create(name=args['name'], desc=args['description'], env_id=args['environment_id'], create_example_model=args['create_example_model'],
                           feature_set_id=args['feature_set_id'], condition_refcode=args['condition_refcode'], condition_name=args['condition_name'])

        return m, 201


class MLModelResource(Resource):
    def __init__(self):
        super(MLModelResource, self).__init__()
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('name', type=str, required=False, location='json')
        self.parser.add_argument('description', type=str, location='json')
        self.parser.add_argument('feature_set_id', type=int, required=False, location='json')
        self.parser.add_argument('condition_refcode', type=str, required=False, location='json')
        self.parser.add_argument('condition_name', type=str, required=False, location='json')

    @auth.login_required
    @marshal_with(ml_model_fields)
    @swagger.doc({
        "summary": "Returns a specific ML model",
        "tags": ["ml models"],
        "produces": [
            "application/json"
        ],
        "description": 'Returns the machine learning model for the given ID',
        "responses": {
            "200": {
                "description": "Returns the ML model with the given ID"
            },
            "404": {
                "description": "Not found error when ML model doesn't exist"
            }
        },
        "parameters": [
            {
                "name": "model_id",
                "in": "path",
                "type": "integer",
                "description": "The ID of the ML model",
                "required": True
            }
        ],
    })
    def get(self, model_id):
        return MLModel.get(model_id), 200

    @auth.login_required
    @marshal_with(ml_model_fields)
    @swagger.doc({
        "summary": "Update a ML model",
        "tags": ["ml models"],
        "produces": [
            "application/json"
        ],
        "description": 'Update a machine learning model',
        "responses": {
            "200": {
                "description": "Success: Newly updated ML model is returned"
            },
            "404": {
                "description": "Not found error when ML model doesn't exist"
            }
        },
        "parameters": [
            {
                "name": "model_id",
                "in": "path",
                "type": "integer",
                "description": "The ID of the ML model",
                "required": True
            },
            {
                "name": "ml_model",
                "in": "body",
                "schema": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string"
                        },
                        "description": {
                            "type": "string"
                        },
                        "feature_set_id": {
                            "type": "integer"
                        },
                        "condition_refcode": {
                            "type": "string"
                        },
                        "condition_name": {
                            "type": "string"
                        }
                    }
                }
            }
        ],
    })
    def put(self, model_id):
        args = self.parser.parse_args()

        m = MLModel.update(model_id=model_id, name=args['name'], desc=args['description'], feature_set_id=args['feature_set_id'],
                           condition_refcode=args['condition_refcode'], condition_name=args['condition_name'])

        return m, 200

    @auth.login_required
    @marshal_with(id_fields)
    @swagger.doc({
        "summary": "Deletes a specific ML model",
        "tags": ["ml models"],
        "produces": [
            "application/json"
        ],
        "description": 'Delete the machine learning model for the given ID',
        "responses": {
            "200": {
                "description": "Success: Returns the given ID"
            },
            "404": {
                "description": "Not found error when ML model doesn't exist"
            }
        },
        "parameters": [
            {
                "name": "model_id",
                "in": "path",
                "type": "integer",
                "description": "The ID of the ML model",
                "required": True
            }
        ],
    })
    def delete(self, model_id):
        id = ID()
        id.id = MLModel.delete(model_id)

        return id, 200


class UserMLModelListResource(Resource):
    def __init__(self):
        super(UserMLModelListResource, self).__init__()

    @auth.login_required
    @marshal_with(ml_model_fields)
    @swagger.doc({
        "summary": "Returns all ML models for a user",
        "tags": ["ml models"],
        "produces": [
            "application/json"
        ],
        "description": 'Returns all the machine learning models for a user',
        "responses": {
            "200": {
                "description": "Returns the list of ML models for a user"
            }
        },
        "parameters": [
            {
                "name": "user_id",
                "in": "path",
                "type": "integer",
                "description": "The ID of the user",
                "required": True
            }
        ],
    })
    def get(self, user_id):
        return MLModel.get_all_for_user(user_id), 200


class MLModelExportResource(Resource):
    def __init__(self):
        super(MLModelExportResource, self).__init__()

    @auth.login_required
    @swagger.doc({
        "summary": "Exports a specific ML model",
        "tags": ["ml models"],
        "produces": [
            "application/json"
        ],
        "description": 'Exports a specific machine learning model',
        "responses": {
            "200": {
                "description": "Returns a success flag"
            }
        },
        "parameters": [
            {
                "name": "model_id",
                "in": "path",
                "type": "integer",
                "description": "The ID of the ML model to export",
                "required": True
            }
        ],
    })
    def post(self, model_id):
        m = MLModel.get(model_id)

        modelPackagingUtil.package_model(m)

        return {'done': True}, 201

    @auth.login_required
    @swagger.doc({
        "summary": "Download an exported ML model's data",
        "tags": ["ml models"],
        "produces": [
            "application/octet-stream"
        ],
        "description": "Download an exported machine learning model's data",
        "responses": {
            "200": {
                "description": "Returns a zip file with all model data",
                "schema": {
                    "type": "file"
                }
            }
        },
        "parameters": [
            {
                "name": "model_id",
                "in": "path",
                "type": "integer",
                "description": "The ID of the ML model to export",
                "required": True
            }
        ],
    })
    def get(self, model_id):
        m = MLModel.get(model_id)
        response = send_from_directory(modelPackagingUtil.get_packaging_path(m), m.ml_model_name + '.zip', as_attachment=True)
        response.headers['content-type'] = 'application/octet-stream'
        response.status_code = 200
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
    @swagger.doc({
        "summary": "Import a ML model",
        "tags": ["ml models"],
        "produces": [
            "application/json"
        ],
        "consumes": [
            "multipart/form-data"
        ],
        "description": 'Import a machine learning model',
        "parameters": [
            {
                "name": "environment_id",
                "in": "query",
                "type": "integer",
                "description": "ID of environment to import ML model to",
                "required": False
            },
            {
                "name": "feature_set_id",
                "in": "query",
                "type": "integer",
                "description": "ID of the feature set to assign to the ML model",
                "required": False
            },
            {
                "name": "file",
                "in": "formData",
                "type": "file",
                "description": "zip file with ML model data",
                "required": True
            }
        ],
        "responses": {
            "200": {
                "description": "Returns newly created ML model"
            },
            "400": {
                "description": "No file or wrong file type submitted"
            },
            "404": {
                "description": "Not found error when environment or feature set doesn't exist"
            }
        }
    })
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
    @swagger.doc({
        "summary": "Returns suitable environments for ML model import",
        "tags": ["ml models"],
        "produces": [
            "application/json"
        ],
        "consumes": [
            "multipart/form-data"
        ],
        "description": 'Returns suitable environments for machine learning model import',
        "parameters": [
            {
                "name": "file",
                "in": "formData",
                "type": "file",
                "description": "json file with ML model metadata",
                "required": True
            }
        ],
        "responses": {
            "200": {
                "description": "Returns list with suitable environments"
            },
            "400": {
                "description": "No file or wrong file type submitted"
            }
        }
    })
    def post(self):
        args = self.parser.parse_args()
        f = args['file']

        if f.filename == '':
            abort(400, message="No file selected")
        if not self.allowed_file(f.filename):
            abort(400, message="File not allowed")

        return modelPackagingUtil.get_suitable_environments(f), 200


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
    @swagger.doc({
        "summary": "Returns suitable feature sets for ML model import",
        "tags": ["ml models"],
        "produces": [
            "application/json"
        ],
        "consumes": [
            "multipart/form-data"
        ],
        "description": 'Returns suitable featuresets for machine learning model import',
        "parameters": [
            {
                "name": "file",
                "in": "formData",
                "type": "file",
                "description": "json file with ML model metadata",
                "required": True
            }
        ],
        "responses": {
            "200": {
                "description": "Returns list with suitable feature sets"
            },
            "400": {
                "description": "No file or wrong file type submitted"
            }
        }
    })
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

    # @auth.login_required
    # TODO: comment in @auth.login_required again
    def post(self, model_id):
        parser = reqparse.RequestParser()
        parser.add_argument('patient_ids', type=int, required=True, action='append', help='no patientIds provided', location='json')
        parser.add_argument('writeToFhir', type=inputs.boolean, required=False, location='args')
        parser.add_argument('ownInputData', type=inputs.boolean, required=False, location='args')
        args = parser.parse_args()
        patient_ids = args['patient_ids']

        ml_model = MLModel.get(model_id)

        if args['ownInputData'] is False:
            features = ml_model.feature_set.features
            feature_set = []

            for feature in features:
                cur_feature = marshal(feature, feature_fields)
                feature_set.append(cur_feature)
            preprocess_body = {'patient': patient_ids, 'feature_set': feature_set}

            resp = requests.post('http://' + config.DATA_PREPROCESSING_HOST + '/crawler', json=preprocess_body).json()
            csv_url = resp['csv_url']
            csv_url = csv_url.replace("localhost", "data_pre")

            data_url = {'dataUrl': csv_url}
            docker_api_call = 'http://' + ml_model.environment.container_name + ':5000/models/' + ml_model.ml_model_name + '/execute'
            predictions = requests.get(docker_api_call, params=data_url).json()
        else:
            data_url = {'dataUrl': "http://buhu"}
            docker_api_call = 'http://' + ml_model.environment.container_name + ':5000/models/' + ml_model.ml_model_name + '/execute'
            predictions = requests.get(docker_api_call, params=data_url).json()

        if args['writeToFhir'] is not False:
            return self.predict_fhir_request(predictions, model_id)

        return predictions, 200

    # todo: swagger
    def predict_fhir_request(self, predictions, model_id):
        ml_model = MLModel.get(model_id)
        risk_ass = fhir_ra.RiskAssessment(fhir_ra_base.fhir__base_risk_assessment)
        cond_ref = ml_model.condition_refcode
        risk_ass.condition = {"reference": cond_ref}
        model_outcomes = PredictionOutcome.get_all_for_model(model_id)
        outcomes = {}
        for outcome in model_outcomes:
            outcomes[outcome.outcome_value] = outcome.outcome_code

        patient_prediction = fhir_ra_base.fhir_base_patient_prediction
        risk_ass.prediction = [patient_prediction]
        predictions = predictions['prediction']
        fhir_risk_assessments = []

        for prediction in predictions:
            risk_ass.subject = {"reference": "Patient/" + prediction['patientId']}

            # temporary mapping of output string to code with "_" - needs to be changed to proper concept
            patient_prediction['outcome']['coding'][0]['code'] = outcomes[prediction['prediction']]
            risk_ass.prediction = [patient_prediction]
            fhir_risk_assessments.append(risk_ass.as_json())
            resp = requests.post(config.HAPIFHIR_URL + 'gtfhir/base/RiskAssessment', json=risk_ass.as_json())

        return fhir_risk_assessments, 200
