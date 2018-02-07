from flask import g, Response
from flask_restful import reqparse, abort, fields, marshal_with, marshal
from flask_restful_swagger_2 import swagger, Resource
from rdb.rdb import db
from rdb.models.user import User
from resources.userResource import auth
import requests
import config
from rdb.models.featureSet import FeatureSet
import json
import logging
logger = logging.getLogger(__name__)

feature_fields = {
    'resource': fields.String,
    'key': fields.String(attribute='parameter_name'),
    'value': fields.String,
    'name': fields.String,
}


class DataListResource(Resource):
    def __init__(self):
        super(DataListResource, self).__init__()
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('patient_ids', type=int,action='append', required=True, help='no patientIds provided', location='json')
        self.parser.add_argument('feature_set_id', type=int, location='json')
        self.parser.add_argument('resource_name', type=str, location='json')

    @auth.login_required
    def get(self):

        parser = reqparse.RequestParser()
        parser.add_argument('jobId', type=str, required=False, location='args')
        args = parser.parse_args()
        job_id = args['jobId']

        s_query = "http://" + config.DATA_PREPROCESSING_HOST + "/crawler/jobs"

        if job_id:
            s_query = s_query + "/" + str(job_id)
            
        resp = requests.get(s_query).json()

        return resp, 200

    @auth.login_required
    def post(self):
        args = self.parser.parse_args()
        patient_ids = args['patient_ids']
        feature_set = args['feature_set_id']
        resource_name = args['resource_name']

        if ((feature_set is None and resource_name is None) or (feature_set is not None and resource_name is not None)):
            return "Must provide feature_set_id XOR resource_name", 400

        preprocess_body = {'patient_ids' : patient_ids}

        if (feature_set is not None):
            features = FeatureSet.query.get(1).features
            feature_set = []

            for feature in features:
                cur_feature = marshal(feature, feature_fields)
                feature_set.append(cur_feature)

            preprocess_body["feature_set"] = feature_set
        
        if (resource_name is not None):
            preprocess_body["resource"] = resource_name

        print(preprocess_body)

        resp = requests.post("http://" + config.DATA_PREPROCESSING_HOST + "/crawler/jobs", json = preprocess_body).json()

        return resp, 200


class DataResource(Resource):
    def __init__(self):
        super(DataResource, self).__init__()

    @auth.login_required
    def get(self, datarequest_id):

        s_query = "http://" + config.DATA_PREPROCESSING_HOST + "/aggregation/" + str(datarequest_id) + "?output_type=csv&aggregation_type=latest"
        result = requests.get(s_query)
        return Response(result, mimetype='text/csv')

