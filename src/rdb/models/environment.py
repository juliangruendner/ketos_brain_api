from rdb.rdb import db, LowerCaseText
from enum import Enum
import datetime
from resources.adminAccess import is_admin_user
from flask import g
import rdb.models.image as Image
from dockerUtil.dockerClient import dockerClient, wait_for_it
import config
import requests
import uuid
from flask_restful import abort
import rdb.models.user as User


class Environment(db.Model):
    """Environment Class"""

    __tablename__ = "environment"

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    container_id = db.Column(db.Text, nullable=False)
    container_name = db.Column(db.Text, nullable=False)
    status = db.Column(LowerCaseText, nullable=False)
    jupyter_port = db.Column(db.Text, nullable=False)
    jupyter_token = db.Column(db.Text, nullable=False)
    jupyter_url = None
    description = db.Column(db.Text)
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    # authorized_users = db.relationship('User', lazy='subquery', secondary='user_environment_access')
    image_id = db.Column(db.Integer, db.ForeignKey('image.id'), nullable=False)
    ml_models = db.relationship('MLModel', lazy='select', cascade='delete, delete-orphan', backref='environment')
    created_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now())
    updated_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now(), onupdate=datetime.datetime.now)

    def __init__(self):
        super(Environment, self).__init__()

    def __repr__(self):
        """Display when printing a environment object"""

        return "<ID: {}, Name: {}, description: {}>".format(self.id, self.name, self.description)

    def as_dict(self):
        """Convert object to dictionary"""

        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def handle_jupyter_data(self):
        if is_admin_user() or g.user.id == self.creator_id:
            self.set_jupyter_url()
        else:
            self.hide_jupyter_data()

    def start_jupyter(self):
        # wait for container api to be up and running
        wait_for_it(self.container_name, 5000)
        # start jupyter notebook and get jupyter token
        resp = requests.post('http://' + self.container_name + ':5000/jupyter').json()
        self.jupyter_token = str(resp['jupyter_token'])
        self.status = Environment.Status.running.value

    def set_jupyter_url(self):
        # TODO: read host address from os
        host = 'localhost'
        self.jupyter_url = host + ':' + self.jupyter_port + '/?token=' + self.jupyter_token

    def hide_jupyter_data(self):
        self.jupyter_port = None
        self.jupyter_token = None
        self.jupyter_url = None

    def get_data_directory(self):
        return '/ketos/environments_data/' + self.container_name

    class Status(Enum):
        running = 'running'
        stopped = 'stopped'


def get_open_port():
    import socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("", 0))
    s.listen(1)
    port = s.getsockname()[1]
    s.close()
    return port


def create(name, desc, image_id, raise_abort=True):
    e = Environment()
    e.name = name
    e.description = desc

    i = Image.get(image_id, raise_abort=raise_abort)

    e.image_id = i.id
    e.creator_id = g.user.id

    image_name = config.DOCKER_REGISTRY_DOMAIN + "/" + i.name
    e.jupyter_port = get_open_port()

    e.container_name = str(uuid.uuid4().hex)

    container = dockerClient.containers.run(image_name,
                                            name=e.container_name,
                                            detach=True,
                                            network=config.PROJECT_NAME+"_environment",
                                            ports={"8000/tcp": e.jupyter_port},
                                            volumes={e.get_data_directory(): {'bind': '/mlenvironment/models', 'mode': 'rw'}})

    e.container_id = container.id
    e.start_jupyter()

    db.session.add(e)
    db.session.commit()

    e.set_jupyter_url()

    return e


def abort_if_environment_doesnt_exist(env_id):
        abort(404, message="environment {} doesn't exist".format(env_id))


def get(env_id, raise_abort=True):
    e = Environment.query.get(env_id)

    if raise_abort and not e:
        abort_if_environment_doesnt_exist(env_id)

    e.handle_jupyter_data()

    return e


def get_all():
    envs = Environment.query.all()
    for e in envs:
        e.handle_jupyter_data()

    return envs


def get_all_for_user(user_id):
    envs = Environment.query.filter_by(creator_id=user_id).all()
    for e in envs:
        e.handle_jupyter_data()

    return envs


def update(env_id, status=None, name=None, desc=None, raise_abort=True):
    e = get(env_id, raise_abort=raise_abort)

    User.check_request_for_logged_in_user(e.creator_id)

    if status and not e.status == status:
        if status == Environment.Environment.Status.running.value:
            dockerClient.containers.get(e.container_id).start()
            e.start_jupyter()
        elif status == Environment.Environment.Status.stopped.value:
            dockerClient.containers.get(e.container_id).stop()
        else:
            if raise_abort:
                abort(400, message="status {} is not allowed".format(status))
            else:
                return None

        e.status = status

    if name:
        e.name = name

    if desc:
        e.description = desc

    db.session.commit()
    return e


def delete(env_id, raise_abort=True):
    e = get(env_id, raise_abort=raise_abort)

    User.check_request_for_logged_in_user(e.creator_id)

    if not e.status == 'stopped':
        if raise_abort:
            abort(405, message="environment must be stopped before it can be deleted")
        else:
            return None

    container = dockerClient.containers.get(e.container_id)
    container.remove(force=True)

    db.session.delete(e)
    db.session.commit()

    return env_id
