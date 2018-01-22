from flask_restful import reqparse, abort, fields, marshal_with
from flask_restful_swagger_2 import swagger, Resource
from rdb.rdb import db
from rdb.models.featureSet import FeatureSet
from resources.featureResource import feature_fields
from rdb.models.feature import Feature
from rdb.models.id import ID, id_fields
from resources.userResource import auth, user_fields, check_request_for_logged_in_user
from util import featureSetUtil

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
        return FeatureSet.query.all(), 200

    @auth.login_required
    @marshal_with(feature_set_fields)
    def post(self):
        args = self.parser.parse_args()

        fs = featureSetUtil.create_feature_set(name=args['name'], desc=args['description'])
        return fs, 201


def abort_if_feature_set_doesnt_exist(feature_set_id):
    abort(404, message="feature set {} doesn't exist".format(feature_set_id))


def get_feature_set(feature_set_id):
    fs = FeatureSet.query.get(feature_set_id)

    if not fs:
        abort_if_feature_set_doesnt_exist(feature_set_id)

    return fs


class FeatureSetResource(Resource):
    def __init__(self):
        super(FeatureSetResource, self).__init__()
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('name', type=str, required=False, location='json')
        self.parser.add_argument('description', type=str, required=False, location='json')

    @auth.login_required
    @marshal_with(feature_set_fields)
    def get(self, feature_set_id):
        return self.get_feature_set(feature_set_id), 200

    @auth.login_required
    @marshal_with(feature_set_fields)
    def put(self, feature_set_id):
        fs = get_feature_set(feature_set_id)

        check_request_for_logged_in_user(fs.creator_id)

        args = self.parser.parse_args()
        if args['name']:
            fs.name = args['name']

        if args['description']:
            fs.description = args['description']

        db.session.commit()
        return fs, 200

    @auth.login_required
    @marshal_with(id_fields)
    def delete(self, feature_set_id):
        fs = get_feature_set(feature_set_id)

        check_request_for_logged_in_user(fs.creator_id)

        fs.features = []
        db.session.commit()

        db.session.delete(fs)
        db.session.commit()

        id = ID()
        id.id = feature_set_id
        return id, 200


class UserFeatureSetListResource(Resource):
    def __init__(self):
        super(UserFeatureSetListResource, self).__init__()

    @auth.login_required
    @marshal_with(feature_set_fields)
    def get(self, user_id):
        feature_sets = FeatureSet.query.filter_by(creator_id=user_id).all()
        return feature_sets, 200


class FeatureSetFeatureListResource(Resource):
    def __init__(self):
        super(FeatureSetFeatureListResource, self).__init__()
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('feature_ids', type=int, action='append', required=True, help='no feature ids provided', location='json')

    @auth.login_required
    @marshal_with(feature_set_features_fields)
    def get(self, feature_set_id):
        return get_feature_set(feature_set_id), 200

    @auth.login_required
    @marshal_with(feature_set_features_fields)
    def post(self, feature_set_id):
        fs = get_feature_set(feature_set_id)
        args = self.parser.parse_args()
        feature_ids = args['feature_ids']
        for id in feature_ids:
            f = Feature.query.get(id)
            if f not in fs.features:
                fs.features.append(f)

        db.session.commit()
        return fs, 200

    @auth.login_required
    @marshal_with(feature_set_features_fields)
    def delete(self, feature_set_id):
        fs = get_feature_set(feature_set_id)
        args = self.parser.parse_args()
        feature_ids = args['feature_ids']
        for id in feature_ids:
            f = Feature.query.get(id)
            if f in fs.features:
                fs.features.remove(f)

        db.session.commit()
        return fs, 201
