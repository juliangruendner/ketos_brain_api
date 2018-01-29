from flask_restful import reqparse, abort
from flask_restful_swagger_2 import Api, swagger, Resource
from resources.userResource import auth
import requests
import config

DATA_PRE_RESOURCE_CONFIG_URL = "http://" + config.DATA_PREPROCESSING_HOST + "/resources_config"

class ResourceConfigList(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('resource_name', type = str, location = 'json')
        self.parser.add_argument('resource_mapping', type = dict, action = 'append', location = 'json')

        super(ResourceConfigList, self).__init__()
    
    @auth.login_required
    def get(self):
        resp = requests.get(DATA_PRE_RESOURCE_CONFIG_URL).json()

        return resp, 200

    @auth.login_required
    def post(self):
        args = self.parser.parse_args()
        resource_name = args["resource_name"]
        resource_mapping = args["resource_mapping"]

        preprocess_body = {"resource_name": resource_name, "resource_mapping": resource_mapping}
        resp = requests.post(DATA_PRE_RESOURCE_CONFIG_URL, json = preprocess_body).json()

        return resp, 200

    @auth.login_required
    def delete(self):
        args = self.parser.parse_args()
        resource_name = args["resource_name"]

        resp = requests.delete(DATA_PRE_RESOURCE_CONFIG_URL + "/" + + "resource_name").json

        return resp, 200

class ResourceConfig(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('resource_mapping', type = dict, action = 'append', location = 'json')

        super(ResourceConfig, self).__init__()

    @auth.login_required
    def get(self, resource_name):
        resp = requests.get(DATA_PRE_RESOURCE_CONFIG_URL + "/" + resource_name).json()

        return resp, 200

    @auth.login_required
    def post(self, resource_name):
        args = self.parser.parse_args()
        resource_mapping = args["resource_mapping"]

        preprocess_body = {"resource_mapping": resource_mapping}
        resp = requests.post(DATA_PRE_RESOURCE_CONFIG_URL + "resource_name", json = preprocess_body).json()

        return resp, 200
    
    @auth.login_required
    def delete(self, resource_name):
        args = self.parser.parse_args()
        resource_name = args["resource_name"]

        resp = requests.delete(DATA_PRE_RESOURCE_CONFIG_URL + "/" + + "resource_name").json

        return resp, 200
