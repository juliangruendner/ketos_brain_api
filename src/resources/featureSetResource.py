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


feature_set_post_parser = reqparse.RequestParser()
feature_set_post_parser.add_argument('name', type=str, required=False, location='json')
feature_set_post_parser.add_argument('description', type=str, required=False, location='json')


class FeatureSetListResource(Resource):
    def __init__(self):
        super(FeatureSetListResource, self).__init__()

    @auth.login_required
    @marshal_with(feature_set_fields)
    @swagger.doc({
        "summary": "Returns all existing feature sets",
        "tags": ["feature sets"],
        "produces": [
            "application/json"
        ],
        "description": 'Returns all existing feature sets',
        "responses": {
            "200": {
                "description": "Returns the list of feature sets"
            }
        }
    })
    def get(self):
        return FeatureSet.get_all(), 200

    @auth.login_required
    @marshal_with(feature_set_fields)
    @swagger.doc({
        "summary": "Create a new feature set",
        "tags": ["feature sets"],
        "produces": [
            "application/json"
        ],
        "description": 'Create a new feature set',
        'reqparser': {'name': 'feature set post parser',
                      'parser': feature_set_post_parser},
        "responses": {
            "200": {
                "description": "Returns newly created feature set"
            }
        }
    })
    def post(self):
        args = feature_set_post_parser.parse_args()

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
    @swagger.doc({
        "summary": "Returns a specific feature set",
        "tags": ["feature sets"],
        "produces": [
            "application/json"
        ],
        "description": 'Returns the feature set for the given ID',
        "responses": {
            "200": {
                "description": "Returns the feature set with the given ID"
            },
            "404": {
                "description": "Not found error when feature set doesn't exist"
            }
        },
        "parameters": [
            {
                "name": "feature_set_id",
                "in": "path",
                "type": "integer",
                "description": "The ID of the feature set",
                "required": True
            }
        ],
    })
    def get(self, feature_set_id):
        return FeatureSet.get(feature_set_id), 200

    @auth.login_required
    @marshal_with(feature_set_fields)
    @swagger.doc({
        "summary": "Update a feature set",
        "tags": ["feature sets"],
        "produces": [
            "application/json"
        ],
        "description": 'Update a specific feature set',
        "responses": {
            "200": {
                "description": "Success: Newly updated feature set is returned"
            },
            "404": {
                "description": "Not found error when feature set doesn't exist"
            }
        },
        "parameters": [
            {
                "name": "feature_set_id",
                "in": "path",
                "type": "integer",
                "description": "The ID of the feature set",
                "required": True
            },
            {
                "name": "feature_set",
                "in": "body",
                "schema": {
                    "type": "object",
                    "properties": {
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
    def put(self, feature_set_id):
        args = self.parser.parse_args()

        fs = FeatureSet.update(feature_set_id=feature_set_id, name=args['name'], desc=args['description'])

        return fs, 200

    @auth.login_required
    @marshal_with(id_fields)
    @swagger.doc({
        "summary": "Deletes a specific feature set",
        "tags": ["feature sets"],
        "produces": [
            "application/json"
        ],
        "description": 'Delete the feature set for the given ID',
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
                "name": "feature_set_id",
                "in": "path",
                "type": "integer",
                "description": "The ID of the feature set",
                "required": True
            }
        ],
    })
    def delete(self, feature_set_id):
        id = ID()
        id.id = FeatureSet.delete(feature_set_id)

        return id, 200


class UserFeatureSetListResource(Resource):
    def __init__(self):
        super(UserFeatureSetListResource, self).__init__()

    @auth.login_required
    @marshal_with(feature_set_fields)
    @swagger.doc({
        "summary": "Returns all feature sets for a user",
        "tags": ["feature sets"],
        "produces": [
            "application/json"
        ],
        "description": 'Returns all the feature sets for a user',
        "responses": {
            "200": {
                "description": "Returns the list of feature sets for a user"
            }
        },
        "parameters": [
            {
                "name": "feature_set_id",
                "in": "path",
                "type": "integer",
                "description": "The ID of the feature set",
                "required": True
            }
        ],
    })
    def get(self, user_id):
        return FeatureSet.get_all_for_user(user_id), 200


class FeatureSetFeatureListResource(Resource):
    def __init__(self):
        super(FeatureSetFeatureListResource, self).__init__()
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('feature_ids', type=int, action='append', required=True, help='no feature ids provided', location='json')

    @auth.login_required
    @marshal_with(feature_set_features_fields)
    @swagger.doc({
        "summary": "Returns a specific feature set including all features",
        "tags": ["feature sets"],
        "produces": [
            "application/json"
        ],
        "description": 'Returns the feature set including all features for the given ID',
        "responses": {
            "200": {
                "description": "Returns the feature set including all features with the given ID"
            },
            "404": {
                "description": "Not found error when feature set doesn't exist"
            }
        },
        "parameters": [
            {
                "name": "feature_set_id",
                "in": "path",
                "type": "integer",
                "description": "The ID of the feature set",
                "required": True
            }
        ],
    })
    def get(self, feature_set_id):
        return FeatureSet.get(feature_set_id), 200

    @auth.login_required
    @marshal_with(feature_set_features_fields)
    @swagger.doc({
        "summary": "Add new features to a feature set",
        "tags": ["feature sets"],
        "produces": [
            "application/json"
        ],
        "description": 'Add new features to a feature set',
        "responses": {
            "200": {
                "description": "Returns feature set including all features"
            },
            "404": {
                "description": "Not found error when feature set or a feature doesn't exist"
            }
        },
        "parameters": [
            {
                "name": "feature_set_id",
                "in": "path",
                "type": "integer",
                "description": "The ID of the feature set",
                "required": True
            },
            {
                "name": "feature_ids",
                "in": "body",
                "schema": {
                    "type": "object",
                    "properties": {
                        "feature_ids": {
                            "type": "array",
                            "items": {
                                "type": "integer"
                            }
                        }
                    }
                }
            }
        ],
    })
    def post(self, feature_set_id):
        args = self.parser.parse_args()
        feature_ids = args['feature_ids']

        fs = FeatureSet.add_features(feature_set_id, feature_ids)

        return fs, 200

    @auth.login_required
    @marshal_with(feature_set_features_fields)
    @swagger.doc({
        "summary": "Remove features from a feature set",
        "tags": ["feature sets"],
        "produces": [
            "application/json"
        ],
        "description": 'Remove features from a feature set',
        "responses": {
            "200": {
                "description": "Returns feature set including all remaining features"
            },
            "404": {
                "description": "Not found error when feature set or a feature doesn't exist"
            }
        },
        "parameters": [
            {
                "name": "feature_set_id",
                "in": "path",
                "type": "integer",
                "description": "The ID of the feature set",
                "required": True
            },
            {
                "name": "feature_ids",
                "in": "body",
                "schema": {
                    "type": "object",
                    "properties": {
                        "feature_ids": {
                            "type": "array",
                            "items": {
                                "type": "integer"
                            }
                        }
                    }
                }
            }
        ],
    })
    def delete(self, feature_set_id):
        args = self.parser.parse_args()
        feature_ids = args['feature_ids']

        fs = FeatureSet.remove_features(feature_set_id, feature_ids)

        return fs, 201
