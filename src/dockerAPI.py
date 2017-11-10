from flask import Flask
from flask_restful import Api
from resources.userResource import UserList, User
from rdb.rdb import connect_to_db, create_all

app = Flask(__name__)
api = Api(app)

api.add_resource(UserList, '/user', endpoint='users')
api.add_resource(User, '/user/<int:user_id>', endpoint='user')

if __name__ == '__main__':
    connect_to_db(app, 'postgresql://mad:MAD@db:5432/mad')
    create_all()
    # set debug false in production mode
    app.run(debug=True, host='0.0.0.0', port=5000)