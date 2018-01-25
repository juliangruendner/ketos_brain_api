from flask_restful import reqparse, fields, marshal_with
from flask_restful_swagger_2 import swagger, Resource
import rdb.models.feature as Feature
from rdb.models.id import ID, id_fields
from resources.userResource import auth, user_fields

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
        return Feature.get_all(), 200

    @auth.login_required
    @marshal_with(feature_fields)
    def post(self):
        args = self.parser.parse_args()

        f = Feature.create(args['resource'], args['parameter_name'], args['value'], args['name'], args['description'])

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

    @auth.login_required
    @marshal_with(feature_fields)
    def get(self, feature_id):
        return Feature.get(feature_id), 200

    @auth.login_required
    @marshal_with(feature_fields)
    def put(self, feature_id):
        args = self.parser.parse_args()

        f = Feature.update(feature_id=feature_id, resource=args['resource'], parameter_name=args['parameter_name'], value=args['value'], name=args['name'], desc=args['description'])

        return f, 200

    @auth.login_required
    @marshal_with(id_fields)
    def delete(self, feature_id):
        id = ID()
        id.id = Feature.delete(feature_id)

        return id, 200


class UserFeatureListResource(Resource):
    def __init__(self):
        super(UserFeatureListResource, self).__init__()

    @auth.login_required
    @marshal_with(feature_fields)
    def get(self, user_id):
        return Feature.get_all_for_user(user_id), 200
