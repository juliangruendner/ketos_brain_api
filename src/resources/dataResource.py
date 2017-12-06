from flask import g
from flask_restful import Resource, reqparse, abort, fields, marshal_with, marshal
from rdb.rdb import db
from rdb.models.user import User
from resources.userResource import auth
import requests
from rdb.models.featureSet import FeatureSet
import json

feature_fields = {
    'resource': fields.String,
    'key': fields.String(attribute='parameter_name'),
    'value': fields.String,
}


class DataResource(Resource):
    def __init__(self):
        super(DataResource, self).__init__()
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('patient_ids', type=int,action='append', required=True, help='no patientIds provided', location='json')
        self.parser.add_argument('feature_set_id', type=int, required=True, help='No feature set id provided', location='json')

    @auth.login_required
    def get(self):

        parser = reqparse.RequestParser()
        parser.add_argument('jobId', type=str, required=True, location='args')
        args = parser.parse_args()
        job_id = args['jobId']

        resp = requests.get('http://data_pre:5000/aggregation/' + job_id).json()

        print(resp)

        return resp, 200

    @auth.login_required
    def post(self):
        args = self.parser.parse_args()
        patient_ids = args['patient_ids']
        feature_set = args['feature_set_id']

        features = FeatureSet.query.get(1).features
        feature_set = []

        for feature in features:
            cur_feature = marshal(feature, feature_fields)
            feature_set.append(cur_feature)

        preprocess_body = {'patient_ids' : patient_ids, 'feature_set': feature_set}

        print(preprocess_body)

        resp = requests.post('http://data_pre:5000/crawler/jobs', json = preprocess_body).json()

        return resp, 200
