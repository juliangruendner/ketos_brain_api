from flask import g
from flask_restful import Resource, reqparse, abort, fields, marshal_with
from rdb.rdb import db
from rdb.models.user import User
from rdb.models.image import Image
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
    'creator': fields.Nested(user_fields)
}


class ImageListResource(Resource):
    def __init__(self):
        super(ImageListResource, self).__init__()

    @auth.login_required
    @marshal_with(image_fields)
    def get(self):
        return Image.query.all(), 200

    @auth.login_required
    @marshal_with(image_fields)
    @AdminAccess()
    def post(self):
        args = parser.parse_args()

        i = Image()
        i.name = args['name']
        i.description = args['description']
        i.title = args['title']
        i.creator_id = User.query.get(g.user.id).id

        db.session.add(i)
        db.session.commit()
        return i, 201


class ImageResource(Resource):
    def __init__(self):
        super(ImageResource, self).__init__()

    def abort_if_image_doesnt_exist(self, image_id):
        abort(404, message="image {} doesn't exist".format(image_id))

    def get_image(self, image_id):
        i = Image.query.get(image_id)

        if not i:
            self.abort_if_image_doesnt_exist(image_id)

        return i

    @auth.login_required
    @marshal_with(image_fields)
    def get(self, image_id):
        return self.get_image(image_id), 200

    @auth.login_required
    @marshal_with(image_fields)
    @AdminAccess()
    def put(self, image_id):
        i = self.get_image(image_id)

        args = parser.parse_args()
        i.title = args['title']
        i.description = args['description']

        db.session.commit()
        return i, 200

    @auth.login_required
    @marshal_with(image_fields)
    @AdminAccess()
    def delete(self, image_id):
        i = self.get_image(image_id)

        db.session.delete(i)
        db.session.commit()
        return {'result': True}, 204