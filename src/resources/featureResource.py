from flask_restful import reqparse, abort, fields, marshal_with
from flask_restful_swagger_2 import swagger, Resource
from rdb.rdb import db
from rdb.models.feature import Feature
from rdb.models.id import ID, id_fields
from resources.userResource import auth, user_fields, check_request_for_logged_in_user
from util import featureUtil

feature_fields = {
    'id': fields.Integer,
    'resource': fields.String,
    'parameter_name': fields.String,
    'value': fields.String,
    'name': fields.String,
    'description': fields.String,
    'creator': fields.Nested(user_fields),
    'created_at': fields.DateTime,
    'updated_at': fields.DateTime
}


class FeatureListResource(Resource):
    def __init__(self):
        super(FeatureListResource, self).__init__()
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('resource', type=str, required=True, help='No resource provided', location='json')
        self.parser.add_argument('parameter_name', type=str, required=True, help='No parameter name provided', location='json')
        self.parser.add_argument('value', type=str, required=True, help='No value provided', location='json')
        self.parser.add_argument('name', type=str, required=False, location='json')
        self.parser.add_argument('description', type=str, required=False, location='json')

    @auth.login_required
    @marshal_with(feature_fields)
    def get(self):
        return Feature.query.all(), 200

    @auth.login_required
    @marshal_with(feature_fields)
    def post(self):
        args = self.parser.parse_args()

        f = featureUtil.create_feature(args['resource'], args['parameter_name'], args['value'], args['name'], args['description'])
        return f, 201


class FeatureResource(Resource):
    def __init__(self):
        super(FeatureResource, self).__init__()
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('resource', type=str, required=False, location='json')
        self.parser.add_argument('parameter_name', type=str, required=False, location='json')
        self.parser.add_argument('value', type=str, required=False, location='json')
        self.parser.add_argument('name', type=str, required=False, location='json')
        self.parser.add_argument('description', type=str, required=False, location='json')

    def abort_if_feature_doesnt_exist(self, feature_id):
        abort(404, message="feature {} doesn't exist".format(feature_id))

    def get_feature(self, feature_id):
        f = Feature.query.get(feature_id)

        if not f:
            self.abort_if_feature_doesnt_exist(feature_id)

        return f

    @auth.login_required
    @marshal_with(feature_fields)
    def get(self, feature_id):
        return self.get_feature(feature_id), 200

    @auth.login_required
    @marshal_with(feature_fields)
    def put(self, feature_id):
        f = self.get_feature(feature_id)

        check_request_for_logged_in_user(f.creator_id)

        args = self.parser.parse_args()
        if args['resource']:
            f.resource = args['resource']

        if args['parameter_name']:
            f.parameter_name = args['parameter_name']

        if args['value']:
            f.value = args['value']

        if args['name']:
            f.name = args['name']

        if args['description']:
            f.description = args['description']

        db.session.commit()
        return f, 200

    @auth.login_required
    @marshal_with(id_fields)
    def delete(self, feature_id):
        f = self.get_feature(feature_id)

        check_request_for_logged_in_user(f.creator_id)

        db.session.delete(f)
        db.session.commit()

        id = ID()
        id.id = feature_id
        return id, 200


class UserFeatureListResource(Resource):
    def __init__(self):
        super(UserFeatureListResource, self).__init__()

    @auth.login_required
    @marshal_with(feature_fields)
    def get(self, user_id):
        features = Feature.query.filter_by(creator_id=user_id).all()
        return features, 200
