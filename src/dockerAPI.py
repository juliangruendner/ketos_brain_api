from flask import Flask
from flask_restful import Api
from resources.userResource import UserListResource, UserResource
from resources.imageResource import ImageListResource, ImageResource
from resources.environmentResource import EnvironmentListResource, EnvironmentResource
from resources.mlModelResource import MLModelListResource, MLModelResource
from rdb.rdb import connect_to_db, create_all

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
api = Api(app)


api.add_resource(UserListResource, '/users', endpoint='users')
api.add_resource(UserResource, '/users/<string:user_id>', endpoint='user')
api.add_resource(EnvironmentListResource, '/environments', endpoint='environments')
api.add_resource(EnvironmentResource, '/environments/<int:env_id>', endpoint='environment')
api.add_resource(MLModelListResource, '/environments/<int:env_id>/models', endpoint='models')
api.add_resource(MLModelResource, '/environments/<int:env_id>/models/<int:model_id>', endpoint='model')
api.add_resource(ImageListResource, '/images', endpoint='images')
api.add_resource(ImageResource, '/images/<int:image_id>', endpoint='image')

if __name__ == '__main__':
    connect_to_db(app, 'postgresql://mad:MAD@db:5432/mad')
    create_all()
    # set debug false in production mode
    app.run(debug=True, host='0.0.0.0', port=5000)
