from flask_restful import reqparse, fields, marshal_with
from flask_restful_swagger_2 import swagger, Resource
import rdb.models.environment as Environment
from rdb.models.id import ID, id_fields
from resources.userResource import auth, user_fields

environment_fields = {
    'id': fields.Integer,
    'name': fields.String,
    'container_id': fields.String,
    'container_name': fields.String,
    'status': fields.String,
    'jupyter_port': fields.String,
    'jupyter_token': fields.String,
    'jupyter_url': fields.String,
    'description': fields.String,
    'creator': fields.Nested(user_fields),
    'image_id': fields.Integer,
    'created_at': fields.DateTime,
    'updated_at': fields.DateTime
}


env_post_parser = reqparse.RequestParser()
env_post_parser.add_argument('name', type=str, required=True, help='No environment name provided', location='json')
env_post_parser.add_argument('status', type=str, required=False, location='json')
env_post_parser.add_argument('description', type=str, required=False, location='json')
env_post_parser.add_argument('image_id', type=int, required=True, help='No image id provided', location='json')


class EnvironmentListResource(Resource):
    def __init__(self):
        super(EnvironmentListResource, self).__init__()

    @auth.login_required
    @marshal_with(environment_fields)
    @swagger.doc({
        "summary": "Returns all registered environments",
        "tags": ["environments"],
        "produces": [
            "application/json"
        ],
        "description": 'Returns all the registered environments',
        "responses": {
            "200": {
                "description": "Returns the list of environments"
            }
        }
    })
    def get(self):
        return Environment.get_all(), 200

    @auth.login_required
    @marshal_with(environment_fields)
    @swagger.doc({
        "summary": "Create a new environment",
        "tags": ["environments"],
        "produces": [
            "application/json"
        ],
        "description": 'Create a new environment',
        'reqparser': {'name': 'environment post parser',
                      'parser': env_post_parser},
        "responses": {
            "200": {
                "description": "Returns newly created environment"
            }
        }
    })
    def post(self):
        args = env_post_parser.parse_args()

        e = Environment.create(name=args['name'], desc=args['description'], image_id=args['image_id'])

        return e, 201


class EnvironmentResource(Resource):
    def __init__(self):
        super(EnvironmentResource, self).__init__()
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('name', type=str, required=False, help='No environment name provided', location='json')
        self.parser.add_argument('status', type=str, required=False, location='json')
        self.parser.add_argument('description', type=str, required=False, location='json')
        self.parser.add_argument('image_id', type=int, required=False, help='No image id provided', location='json')

    @auth.login_required
    @marshal_with(environment_fields)
    @swagger.doc({
        "summary": "Returns a specific environment",
        "tags": ["environments"],
        "produces": [
            "application/json"
        ],
        "description": 'Returns the environment for the given ID',
        "responses": {
            "200": {
                "description": "Returns the environment with the given ID"
            },
            "404": {
                "description": "Not found error when user doesn't exist"
            }
        },
        "parameters": [
            {
                "name": "env_id",
                "in": "path",
                "type": "integer",
                "description": "The ID of the environment",
                "required": True
            }
        ],
    })
    def get(self, env_id):
        return Environment.get(env_id), 200

    @auth.login_required
    @marshal_with(environment_fields)
    @swagger.doc({
        "summary": "Update an environment",
        "tags": ["environments"],
        "produces": [
            "application/json"
        ],
        "description": 'Update an specific environment',
        "responses": {
            "200": {
                "description": "Success: Newly updated environment is returned"
            },
            "404": {
                "description": "Not found error when environment doesn't exist"
            }
        },
        "parameters": [
            {
                "name": "user_id",
                "in": "path",
                "type": "integer",
                "description": "The ID of the environment",
                "required": True
            },
            {
                "name": "environment",
                "in": "body",
                "schema": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string"
                        },
                        "status": {
                            "type": "string"
                        },
                        "description": {
                            "type": "string"
                        },
                        "image_id": {
                            "type": "integer"
                        }
                    }
                }
            }
        ],
    })
    def put(self, env_id):
        args = self.parser.parse_args()

        e = Environment.update(env_id=env_id, status=args['status'], name=args['name'], desc=args['description'])

        return e, 200

    @auth.login_required
    @marshal_with(id_fields)
    @swagger.doc({
        "summary": "Deletes a specific environment",
        "tags": ["environments"],
        "produces": [
            "application/json"
        ],
        "description": 'Delete the environment for the given ID',
        "responses": {
            "200": {
                "description": "Success: Returns the given ID"
            },
            "404": {
                "description": "Not found error when user doesn't exist"
            },
            "405": {
                "description": "Error when environment is not stopped"
            }
        },
        "parameters": [
            {
                "name": "env_id",
                "in": "path",
                "type": "integer",
                "description": "The ID of the environment",
                "required": True
            }
        ],
    })
    def delete(self, env_id):
        id = ID()
        id.id = Environment.delete(env_id)

        return id, 200


class UserEnvironmentListResource(Resource):
    def __init__(self):
        super(UserEnvironmentListResource, self).__init__()

    @auth.login_required
    @marshal_with(environment_fields)
    @swagger.doc({
        "summary": "Returns all registered environments for a user",
        "tags": ["environments"],
        "produces": [
            "application/json"
        ],
        "description": 'Returns all the registered environments for a user',
        "responses": {
            "200": {
                "description": "Returns the list of environments for a user"
            }
        },
        "parameters": [
            {
                "name": "user_id",
                "in": "path",
                "type": "integer",
                "description": "The ID of the user",
                "required": True
            }
        ],
    })
    def get(self, user_id):
        return Environment.get_all_for_user(user_id), 200
