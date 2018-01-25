from flask_restful import reqparse, fields, marshal_with
from flask_restful_swagger_2 import swagger, Resource
import rdb.models.featureSet as FeatureSet
from resources.featureResource import feature_fields
from rdb.models.id import ID, id_fields
from resources.userResource import auth, user_fields

feature_set_fields = {
    'id': fields.Integer,
    'name': fields.String,
    'description': fields.String,
    'creator': fields.Nested(user_fields),
    'created_at': fields.DateTime,
    'updated_at': fields.DateTime
}

feature_set_features_fields = {
    'id': fields.Integer,
    'name': fields.String,
    'description': fields.String,
    'creator': fields.Nested(user_fields),
    'created_at': fields.DateTime,
    'updated_at': fields.DateTime,
    'features': fields.Nested(feature_fields)
}


class FeatureSetListResource(Resource):
    def __init__(self):
        super(FeatureSetListResource, self).__init__()
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('name', type=str, required=False, location='json')
        self.parser.add_argument('description', type=str, required=False, location='json')

    @auth.login_required
    @marshal_with(feature_set_fields)
    def get(self):
        return FeatureSet.get_all(), 200

    @auth.login_required
    @marshal_with(feature_set_fields)
    def post(self):
        args = self.parser.parse_args()

        fs = FeatureSet.create(name=args['name'], desc=args['description'])

        return fs, 201


class FeatureSetResource(Resource):
    def __init__(self):
        super(FeatureSetResource, self).__init__()
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('name', type=str, required=False, location='json')
        self.parser.add_argument('description', type=str, required=False, location='json')

    @auth.login_required
    @marshal_with(feature_set_fields)
    def get(self, feature_set_id):
        return FeatureSet.get(feature_set_id), 200

    @auth.login_required
    @marshal_with(feature_set_fields)
    def put(self, feature_set_id):
        args = self.parser.parse_args()

        fs = FeatureSet.update(feature_set_id=feature_set_id, name=args['name'], desc=args['description'])

        return fs, 200

    @auth.login_required
    @marshal_with(id_fields)
    def delete(self, feature_set_id):
        id = ID()
        id.id = FeatureSet.delete(feature_set_id)

        return id, 200


class UserFeatureSetListResource(Resource):
    def __init__(self):
        super(UserFeatureSetListResource, self).__init__()

    @auth.login_required
    @marshal_with(feature_set_fields)
    def get(self, user_id):
        return FeatureSet.get_all_for_user(user_id), 200


class FeatureSetFeatureListResource(Resource):
    def __init__(self):
        super(FeatureSetFeatureListResource, self).__init__()
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('feature_ids', type=int, action='append', required=True, help='no feature ids provided', location='json')

    @auth.login_required
    @marshal_with(feature_set_features_fields)
    def get(self, feature_set_id):
        return FeatureSet.get(feature_set_id), 200

    @auth.login_required
    @marshal_with(feature_set_features_fields)
    def post(self, feature_set_id):
        args = self.parser.parse_args()
        feature_ids = args['feature_ids']

        fs = FeatureSet.add_features(feature_set_id, feature_ids)

        return fs, 200

    @auth.login_required
    @marshal_with(feature_set_features_fields)
    def delete(self, feature_set_id):
        args = self.parser.parse_args()
        feature_ids = args['feature_ids']

        fs = FeatureSet.remove_features(feature_set_id, feature_ids)

        return fs, 201
