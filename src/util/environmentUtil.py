from resources.adminAccess import is_admin_user
from flask import g
from rdb.rdb import db
from rdb.models.environment import Environment
from rdb.models.image import Image
from dockerUtil.dockerClient import dockerClient, wait_for_it
import config
import requests
import uuid
from flask_restful import abort


def get_open_port():
    import socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("", 0))
    s.listen(1)
    port = s.getsockname()[1]
    s.close()
    return port


def handle_jupyter_data(e):
        if is_admin_user() or g.user.id == e.creator_id:
            e.set_jupyter_url()
        else:
            e.hide_jupyter_data()


def start_jupyter(e):
    # wait for container api to be up and running
    wait_for_it(e.container_name, 5000)
    # start jupyter notebook and get jupyter token
    resp = requests.post('http://' + e.container_name + ':5000/jupyter').json()
    e.jupyter_token = str(resp['jupyter_token'])
    e.status = Environment.Status.running.value


def abort_if_image_doesnt_exist(self, image_id):
    abort(404, message="image {} doesn't exist".format(image_id))


def create_environment(name, desc, image_id, abort=True):
    e = Environment()
    e.name = name
    e.description = desc

    image = Image.query.get(image_id)
    if abort and not image:
        abort_if_image_doesnt_exist(image_id)

    e.image_id = image.id
    e.creator_id = g.user.id

    image_name = config.DOCKER_REGISTRY_DOMAIN + "/" + image.name
    e.jupyter_port = get_open_port()

    e.container_name = str(uuid.uuid4().hex)

    container = dockerClient.containers.run(image_name,
                                            name=e.container_name,
                                            detach=True,
                                            network=config.PROJECT_NAME+"_environment",
                                            ports={"8000/tcp": e.jupyter_port},
                                            volumes={'/ketos/environments_data/'+e.container_name: {'bind': '/mlenvironment/models', 'mode': 'rw'}})

    e.container_id = container.id
    start_jupyter(e)

    db.session.add(e)
    db.session.commit()

    e.set_jupyter_url()

    return e
