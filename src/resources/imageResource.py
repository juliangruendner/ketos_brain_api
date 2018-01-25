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
    def get(self):
        return Image.get_all(), 200

    @auth.login_required
    @marshal_with(image_fields)
    @AdminAccess()
    def post(self):
        args = parser.parse_args()

        i = Image.create(name=args['name'], desc=args['description'], title=args['title'])

        return i, 201


class ImageResource(Resource):
    def __init__(self):
        super(ImageResource, self).__init__()

    @auth.login_required
    @marshal_with(image_fields)
    def get(self, image_id):
        return Image.get(image_id), 200

    @auth.login_required
    @marshal_with(image_fields)
    @AdminAccess()
    def put(self, image_id):
        i = Image.get(image_id)

        args = parser.parse_args()
        i.title = args['title']
        i.description = args['description']

        db.session.commit()
        return i, 200

    @auth.login_required
    @marshal_with(id_fields)
    @AdminAccess()
    def delete(self, image_id):
        i = Image.get(image_id)

        db.session.delete(i)
        db.session.commit()

        id = ID()
        id.id = image_id
        return id, 200
