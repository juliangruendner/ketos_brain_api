from flask_restful import reqparse, abort
from flask_restful_swagger_2 import Api, swagger, Resource
from resources.userResource import auth
import requests
import config

DATA_PRE_RESOURCE_CONFIG_URL = "http://" + config.DATA_PREPROCESSING_HOST + "/resources_config"

class ResourceConfigList(Resource):
    def __init__(self):
        super(ResourceConfigList, self).__init__()
    
    @auth.login_required
    # todo: swagger
    def get(self):
        resp = requests.get(DATA_PRE_RESOURCE_CONFIG_URL).json()

        return resp, 200

class ResourceConfig(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('resource_value_relative_path', type = str, location = 'json')
        self.parser.add_argument('sort_order', type = str, action = 'append', location = 'json')
        super(ResourceConfig, self).__init__()

    @auth.login_required
    # todo: swagger
    def get(self, resource_name):
        resp = requests.get(DATA_PRE_RESOURCE_CONFIG_URL + "/" + resource_name).json()

        return resp, 200

    @auth.login_required
    # todo: swagger
    def post(self, resource_name):
        args = self.parser.parse_args()
        resource_value_relative_path = args["resource_value_relative_path"]
        sort_order = args["sort_order"]

        preprocess_body = {"resource_value_relative_path": resource_value_relative_path}
        if sort_order is not None:
            preprocess_body["sort_order"] = sort_order
        resp = requests.post(DATA_PRE_RESOURCE_CONFIG_URL + "/" + resource_name, json = preprocess_body).json()

        return resp, 200
    
    @auth.login_required
    # todo: swagger
    def delete(self, resource_name):
        resp = requests.delete(DATA_PRE_RESOURCE_CONFIG_URL + "/" + resource_name).json()

        return resp["resource_name"], 200
