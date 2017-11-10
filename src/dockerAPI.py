from flask import Flask
from flask_restful import Api
from resources.userResource import UserList, User

app = Flask(__name__)
api = Api(app)

api.add_resource(UserList, '/user', endpoint='users')
api.add_resource(User, '/user/<int:user_id>', endpoint='user')

if __name__ == '__main__':
    # set debug false in production mode
    app.run(debug=True, host='0.0.0.0', port=5000)