from flask import Flask
from flask_restful import Api
from resources.userResource import UserListResource, UserResource, UserLoginResource
from resources.imageResource import ImageListResource, ImageResource
from resources.environmentResource import EnvironmentListResource, EnvironmentResource, UserEnvironmentListResource
from resources.mlModelResource import MLModelListResource, MLModelResource, UserMLModelListResource
from rdb.rdb import connect_to_db, create_all, create_admin_user
from flask_cors import CORS


app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
api = Api(app)

CORS(app)

api.add_resource(UserListResource, '/users', endpoint='users')
api.add_resource(UserLoginResource, '/users/login', endpoint='user_login')
api.add_resource(UserResource, '/users/<int:user_id>', endpoint='user')
api.add_resource(UserEnvironmentListResource, '/users/<int:user_id>/environments', endpoint='environments_for_user')
api.add_resource(UserMLModelListResource, '/users/<int:user_id>/models', endpoint='models_for_user')
api.add_resource(EnvironmentListResource, '/environments', endpoint='environments')
api.add_resource(EnvironmentResource, '/environments/<int:env_id>', endpoint='environment')
api.add_resource(MLModelListResource, '/environments/<int:env_id>/models', endpoint='models')
api.add_resource(MLModelResource, '/environments/<int:env_id>/models/<int:model_id>', endpoint='model')
api.add_resource(ImageListResource, '/images', endpoint='images')
api.add_resource(ImageResource, '/images/<int:image_id>', endpoint='image')

if __name__ == '__main__':
    connect_to_db(app)
    create_all()
    create_admin_user()
    # set debug false in production mode
    app.run(debug=True, host='0.0.0.0', port=5000)
