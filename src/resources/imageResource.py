from flask_restful import reqparse, fields, marshal_with
from flask_restful_swagger_2 import swagger, Resource
from rdb.rdb import db
import rdb.models.image as Image
from rdb.models.id import ID, id_fields
from resources.userResource import auth, user_fields
from resources.adminAccess import AdminAccess

parser = reqparse.RequestParser()
parser.add_argument('name', type=str, required=True, help='No image name provided', location='json')
parser.add_argument('title', type=str, location='json')
parser.add_argument('description', type=str, required=False, location='json')

image_fields = {
    'id': fields.Integer,
    'name': fields.String,
    'title': fields.String,
    'description': fields.String,
    'creator': fields.Nested(user_fields),
    'created_at': fields.DateTime,
    'updated_at': fields.DateTime
}


class ImageListResource(Resource):
    def __init__(self):
        super(ImageListResource, self).__init__()

    @auth.login_required
    @marshal_with(image_fields)
    @swagger.doc({
        "summary": "Returns all images",
        "tags": ["images"],
        "produces": [
            "application/json"
        ],
        "description": 'Returns all images',
        "responses": {
            "200": {
                "description": "Returns the list of images"
            }
        }
    })
    def get(self):
        return Image.get_all(), 200

    @auth.login_required
    @marshal_with(image_fields)
    @AdminAccess()
    @swagger.doc({
        "summary": "Insert a new image",
        "tags": ["images"],
        "produces": [
            "application/json"
        ],
        "description": 'Insert a new image',
        'reqparser': {'name': 'image post parser',
                      'parser': parser},
        "responses": {
            "200": {
                "description": "Returns newly inserted image"
            }
        }
    })
    def post(self):
        args = parser.parse_args()

        i = Image.create(name=args['name'], desc=args['description'], title=args['title'])

        return i, 201


class ImageResource(Resource):
    def __init__(self):
        super(ImageResource, self).__init__()

    @auth.login_required
    @marshal_with(image_fields)
    @swagger.doc({
        "summary": "Returns a specific image",
        "tags": ["images"],
        "produces": [
            "application/json"
        ],
        "description": 'Returns the image for the given ID',
        "responses": {
            "200": {
                "description": "Returns the image with the given ID"
            },
            "404": {
                "description": "Not found error when image doesn't exist"
            }
        },
        "parameters": [
            {
                "name": "image_id",
                "in": "path",
                "type": "integer",
                "description": "The ID of the image",
                "required": True
            }
        ],
    })
    def get(self, image_id):
        return Image.get(image_id), 200

    @auth.login_required
    @marshal_with(image_fields)
    @AdminAccess()
    @swagger.doc({
        "summary": "Update an image",
        "tags": ["images"],
        "produces": [
            "application/json"
        ],
        "description": 'Update an specific image',
        "responses": {
            "200": {
                "description": "Success: Newly updated image is returned"
            },
            "404": {
                "description": "Not found error when image doesn't exist"
            }
        },
        "parameters": [
            {
                "name": "image_id",
                "in": "path",
                "type": "integer",
                "description": "The ID of the image",
                "required": True
            },
            {
                "name": "feature",
                "in": "body",
                "schema": {
                    "type": "object",
                    "properties": {
                        "title": {
                            "type": "string"
                        },
                        "description": {
                            "type": "string"
                        }
                    }
                }
            }
        ],
    })
    def put(self, image_id):
        i = Image.get(image_id)

        args = parser.parse_args()

        if args['title']:
            i.title = args['title']
        if args['description']:
            i.description = args['description']

        db.session.commit()
        return i, 200

    @auth.login_required
    @marshal_with(id_fields)
    @AdminAccess()
    @swagger.doc({
        "summary": "Deletes an specific image",
        "tags": ["images"],
        "produces": [
            "application/json"
        ],
        "description": 'Delete the image for the given ID',
        "responses": {
            "200": {
                "description": "Success: Returns the given ID"
            },
            "404": {
                "description": "Not found error when image doesn't exist"
            }
        },
        "parameters": [
            {
                "name": "image_id",
                "in": "path",
                "type": "integer",
                "description": "The ID of the image",
                "required": True
            }
        ],
    })
    def delete(self, image_id):
        i = Image.get(image_id)

        db.session.delete(i)
        db.session.commit()

        id = ID()
        id.id = image_id
        return id, 200
