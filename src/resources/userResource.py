from flask import g
from flask_restful import reqparse, fields, marshal_with
from flask_restful_swagger_2 import swagger, Resource
import rdb.models.user as User
from rdb.models.user import auth
from rdb.models.id import ID, id_fields
from resources.adminAccess import AdminAccess

user_fields = {
    'id': fields.Integer,
    'first_name': fields.String,
    'last_name': fields.String,
    'username': fields.String,
    'email': fields.String,
    'created_at': fields.DateTime,
    'updated_at': fields.DateTime
}


class UserLoginResource(Resource):
    def __init__(self):
        super(UserLoginResource, self).__init__()

    @auth.login_required
    @marshal_with(user_fields)
    def get(self):
        return g.user, 200


user_post_parser = reqparse.RequestParser()
user_post_parser.add_argument('first_name', type=str, location='json')
user_post_parser.add_argument('last_name', type=str, location='json')
user_post_parser.add_argument('username', type=str, required=True, help='No username provided', location='json')
user_post_parser.add_argument('email', type=str, required=True, help='No email provided', location='json')
user_post_parser.add_argument('password', type=str, required=True, help='No password provided', location='json')


class UserListResource(Resource):
    def __init__(self):
        super(UserListResource, self).__init__()

    @auth.login_required
    @marshal_with(user_fields)
    @AdminAccess()
    @swagger.doc({
        "summary": "Get all registered users",
        "tags": ["users"],
        "produces": [
            "application/json"
        ],
        "description": 'Get all the registered users for the current Ketos instance',
        "responses": {
            "200": {
                "description": "Returns the list of registered users"
            }
        }
    })
    def get(self):
        return User.get_all(), 200

    @auth.login_required
    @marshal_with(user_fields)
    @swagger.doc({
        "summary": "Create a new user",
        "tags": ["users"],
        "produces": [
            "application/json"
        ],
        "description": 'Option to create a new user by admin',
        'reqparser': {'name': 'user post parser',
                      'parser': user_post_parser},
        "responses": {
            "200": {
                "description": "Returns newly created user"
            }
        }
    })
    def post(self):
        args = user_post_parser.parse_args()

        u = User.create(username=args['username'], email=args['email'], password=args['password'], first_name=args['first_name'], last_name=args['last_name'])

        return u, 201


user_put_parser = reqparse.RequestParser()
user_put_parser.add_argument('first_name', type=str, location='json')
user_put_parser.add_argument('last_name', type=str, location='json')
user_put_parser.add_argument('username', type=str, location='json')
user_put_parser.add_argument('email', type=str, location='json')
user_put_parser.add_argument('password', type=str, location='json')


class UserResource(Resource):
    def __init__(self):
        super(UserResource, self).__init__()

    @auth.login_required
    @marshal_with(user_fields)
    @swagger.doc({
        "summary": "Gets a specific user",
        "tags": ["users"],
        "produces": [
            "application/json"
        ],
        "description": 'Get the user for the given ID',
        "responses": {
            "200": {
                "description": "Returns the user with the given ID"
            },
            "404": {
                "description": "Not found error when user doesn't exist"
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
        return User.get(user_id), 200

    @auth.login_required
    @marshal_with(id_fields)
    @swagger.doc({
        "summary": "Deletes a specific user",
        "tags": ["users"],
        "produces": [
            "application/json"
        ],
        "description": 'Delete the user for the given ID',
        "responses": {
            "200": {
                "description": "Success: Returns the user the given ID"
            },
            "404": {
                "description": "Not found error when user doesn't exist"
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
    def delete(self, user_id):
        id = ID()
        id.id = User.delete(user_id)

        return id, 200

    @auth.login_required
    @marshal_with(user_fields)
    @swagger.doc({
        "summary": "Update a user",
        "tags": ["users"],
        "produces": [
            "application/json"
        ],
        "description": 'Update a specific user',
        "responses": {
            "200": {
                "description": "Success: Newly updated user is returned"
            },
            "404": {
                "description": "Not found error when user doesn't exist"
            }
        },
        "parameters": [
            {
                "name": "user_id",
                "in": "path",
                "type": "integer",
                "description": "The ID of the user",
                "required": True
            },
            {
                "name": "user",
                "in": "body",
                "schema": {
                    "type": "object",
                    "properties": {
                        "first_name": {
                            "type": "string"
                        },
                        "last_name": {
                            "type": "string"
                        },
                        "username": {
                            "type": "string"
                        },
                        "email": {
                            "type": "string"
                        },
                        "password": {
                            "type": "string"
                        }
                    }
                }
            }
        ],
    })
    def put(self, user_id):
        args = user_put_parser.parse_args()

        u = User.update(user_id=user_id, username=args['username'], email=args['email'], password=args['password'], first_name=args['first_name'], last_name=args['last_name'])

        return u, 200
