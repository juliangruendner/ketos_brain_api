from flask import Flask
from flask_restful import Api
from resources.userResource import UserListResource, UserResource
from resources.dockerResource import DockerResource
from rdb.rdb import connect_to_db, create_all
from dockerUtil.dockerClient import dockerClient

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
api = Api(app)

api.add_resource(UserListResource, '/user', endpoint='users')
api.add_resource(UserResource, '/user/<int:user_id>', endpoint='user')
api.add_resource(DockerResource, '/docker', endpoint='docker')

if __name__ == '__main__':
    connect_to_db(app, 'postgresql://mad:MAD@db:5432/mad')
    create_all()
    # set debug false in production mode
    app.run(debug=True, host='0.0.0.0', port=5000)