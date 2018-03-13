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


feature_post_parser = reqparse.RequestParser()
feature_post_parser.add_argument('resource', type=str, required=True, help='No resource provided', location='json')
feature_post_parser.add_argument('parameter_name', type=str, required=True, help='No parameter name provided', location='json')
feature_post_parser.add_argument('value', type=str, required=True, help='No value provided', location='json')
feature_post_parser.add_argument('name', type=str, required=False, location='json')
feature_post_parser.add_argument('description', type=str, required=False, location='json')


class FeatureListResource(Resource):
    def __init__(self):
        super(FeatureListResource, self).__init__()

    @auth.login_required
    @marshal_with(feature_fields)
    @swagger.doc({
        "summary": "Returns all existing features",
        "tags": ["features"],
        "produces": [
            "application/json"
        ],
        "description": 'Returns all existing features',
        "responses": {
            "200": {
                "description": "Returns the list of features"
            }
        }
    })
    def get(self):
        return Feature.get_all(), 200

    @auth.login_required
    @marshal_with(feature_fields)
    @swagger.doc({
        "summary": "Create a new feature",
        "tags": ["features"],
        "produces": [
            "application/json"
        ],
        "description": 'Create a new feature',
        'reqparser': {'name': 'feature post parser',
                      'parser': feature_post_parser},
        "responses": {
            "200": {
                "description": "Returns newly created feature"
            }
        }
    })
    def post(self):
        args = feature_post_parser.parse_args()

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
    @swagger.doc({
        "summary": "Returns a specific feature",
        "tags": ["features"],
        "produces": [
            "application/json"
        ],
        "description": 'Returns the feature for the given ID',
        "responses": {
            "200": {
                "description": "Returns the feature with the given ID"
            },
            "404": {
                "description": "Not found error when feature doesn't exist"
            }
        },
        "parameters": [
            {
                "name": "feature_id",
                "in": "path",
                "type": "integer",
                "description": "The ID of the feature",
                "required": True
            }
        ],
    })
    def get(self, feature_id):
        return Feature.get(feature_id), 200

    @auth.login_required
    @marshal_with(feature_fields)
    @swagger.doc({
        "summary": "Update a feature",
        "tags": ["features"],
        "produces": [
            "application/json"
        ],
        "description": 'Update a specific feature',
        "responses": {
            "200": {
                "description": "Success: Newly updated feature is returned"
            },
            "404": {
                "description": "Not found error when feature doesn't exist"
            }
        },
        "parameters": [
            {
                "name": "feature_id",
                "in": "path",
                "type": "integer",
                "description": "The ID of the feature",
                "required": True
            },
            {
                "name": "feature",
                "in": "body",
                "schema": {
                    "type": "object",
                    "properties": {
                        "resource": {
                            "type": "string"
                        },
                        "parameter_name": {
                            "type": "string"
                        },
                        "value": {
                            "type": "string"
                        },
                        "name": {
                            "type": "integer"
                        },
                        "description": {
                            "type": "string"
                        }
                    }
                }
            }
        ],
    })
    def put(self, feature_id):
        args = self.parser.parse_args()

        f = Feature.update(feature_id=feature_id, resource=args['resource'], parameter_name=args['parameter_name'], value=args['value'], name=args['name'],
                           desc=args['description'])

        return f, 200

    @auth.login_required
    @marshal_with(id_fields)
    @swagger.doc({
        "summary": "Deletes a specific feature",
        "tags": ["features"],
        "produces": [
            "application/json"
        ],
        "description": 'Delete the feature for the given ID',
        "responses": {
            "200": {
                "description": "Success: Returns the given ID"
            },
            "404": {
                "description": "Not found error when feature doesn't exist"
            }
        },
        "parameters": [
            {
                "name": "feature_id",
                "in": "path",
                "type": "integer",
                "description": "The ID of the feature",
                "required": True
            }
        ],
    })
    def delete(self, feature_id):
        id = ID()
        id.id = Feature.delete(feature_id)

        return id, 200


class UserFeatureListResource(Resource):
    def __init__(self):
        super(UserFeatureListResource, self).__init__()

    @auth.login_required
    @marshal_with(feature_fields)
    @swagger.doc({
        "summary": "Returns all features for a user",
        "tags": ["features"],
        "produces": [
            "application/json"
        ],
        "description": 'Returns all the features for a user',
        "responses": {
            "200": {
                "description": "Returns the list of features for a user"
            }
        },
        "parameters": [
            {
                "name": "feature_id",
                "in": "path",
                "type": "integer",
                "description": "The ID of the feature",
                "required": True
            }
        ],
    })
    def get(self, user_id):
        return Feature.get_all_for_user(user_id), 200
